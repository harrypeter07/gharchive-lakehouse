"""Reproducible CPU training with measured validation curves and test reports."""
import copy
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.common.config import (CURATED_DATA_DIR, GLOBAL_SEED, DL_LABELS, DL_MAX_LEN,
                               DL_BATCH_SIZE, DL_EPOCHS, DL_LEARNING_RATE, DL_CPU_THREADS)
from src.ir.naive_bayes import MultinomialNaiveBayes
from src.ml.dataset import IssueVocabulary
from src.ml.model import create_issue_cnn

LABEL_MAP = {label: i for i, label in enumerate(DL_LABELS)}


def set_seed(seed: int = GLOBAL_SEED) -> None:
    """Repeat random initialization and batch order on this CPU environment."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(DL_CPU_THREADS)


def fingerprint(path: Path) -> str:
    """Identify the exact model/data files used by a report."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_predictions(targets: list[int], predictions: list[int]) -> dict:
    """Measure each class equally as well as overall accuracy."""
    confusion = [[0] * len(DL_LABELS) for _ in DL_LABELS]
    for target, predicted in zip(targets, predictions):
        confusion[target][predicted] += 1
    per_class = {}
    for i, label in enumerate(DL_LABELS):
        tp = confusion[i][i]
        support = sum(confusion[i])
        predicted_count = sum(row[i] for row in confusion)
        precision = tp / predicted_count if predicted_count else 0
        recall = tp / support if support else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        per_class[label] = dict(precision=precision, recall=recall, f1=f1, support=support)
    return dict(accuracy=sum(p == y for p, y in zip(predictions, targets)) / len(targets),
                macro_f1=sum(r['f1'] for r in per_class.values()) / len(DL_LABELS),
                per_class=per_class, confusion_matrix=confusion)


def evaluate(model: nn.Module, loader: DataLoader) -> tuple[float, list, list]:
    """Evaluate without dropout or weight updates; average loss by sample count."""
    model.eval()
    total, targets, predictions = 0., [], []
    with torch.inference_mode():
        for x, y in loader:
            logits = model(x)
            total += nn.functional.cross_entropy(logits, y, reduction='sum').item()
            targets.extend(y.tolist())
            predictions.extend(logits.argmax(1).tolist())
    return total / len(targets), targets, predictions


def fit_model(vocab: IssueVocabulary, loaders: dict, epochs: int,
              dropout: float) -> tuple[nn.Module, list]:
    """Train with Adam and select the epoch with the lowest validation loss."""
    set_seed()
    model = create_issue_cnn(len(vocab))
    model.dropout.p = dropout
    loaders['train'].generator.manual_seed(GLOBAL_SEED)
    optimizer = torch.optim.Adam(model.parameters(), lr=DL_LEARNING_RATE)
    counts = torch.bincount(loaders['train'].dataset.tensors[1], minlength=len(DL_LABELS)).float()
    weights = counts.sum().div(counts.clamp_min(1)).sqrt()
    weights = weights / weights.mean()
    history, best_loss, best_weights = [], float('inf'), None
    for epoch in range(1, epochs + 1):
        model.train()
        total, correct, count = 0., 0, 0
        for x, y in loaders['train']:
            optimizer.zero_grad()
            logits = model(x)
            loss = nn.functional.cross_entropy(logits, y, weight=weights)
            loss.backward()
            optimizer.step()
            total += nn.functional.cross_entropy(logits.detach(), y, reduction='sum').item()
            correct += (logits.argmax(1) == y).sum().item()
            count += len(y)
        val_loss, targets, predictions = evaluate(model, loaders['val'])
        history.append(dict(epoch=epoch, train_loss=total/count, val_loss=val_loss,
                            train_accuracy=correct/count,
                            val_accuracy=sum(a == b for a, b in zip(targets, predictions))/len(targets)))
        if val_loss < best_loss:
            best_loss, best_weights = val_loss, copy.deepcopy(model.state_dict())
        print(f'dropout={dropout} epoch={epoch} train_loss={total/count:.4f} val_loss={val_loss:.4f}', flush=True)
    model.load_state_dict(best_weights)
    model.eval()
    return model, history


def validate_splits(records: list[dict]) -> None:
    """Refuse empty groups or leakage before fitting any weights."""
    from src.ir.index import tokenize
    seen_issues, seen_texts = {}, {}
    for row in records:
        issue = (row['repo_name'], row['issue_number'])
        text = tuple(tokenize(f"{row['title']} {row['body']}")[:DL_MAX_LEN])
        for seen, key in ((seen_issues, issue), (seen_texts, text)):
            if key in seen and seen[key] != row['split']:
                raise ValueError('Data leakage: an issue or processed text occurs across splits.')
            seen[key] = row['split']
    if {r['split'] for r in records} != {'train','val','test'}:
        raise ValueError('Nonempty train, val, and test groups are required.')


def train_cnn(epochs: int = DL_EPOCHS, batch_size: int = DL_BATCH_SIZE) -> dict:
    """Train the lab model and a controlled dropout comparison; save real evidence."""
    set_seed()
    records = pq.read_table(CURATED_DATA_DIR / 'splits.parquet').to_pylist()
    validate_splits(records)
    groups = {split: [r for r in records if r['split'] == split] for split in ('train','val','test')}
    vocab = IssueVocabulary()
    vocab.build_from_texts([f"{r['title']} {r['body']}" for r in groups['train']])
    loaders = {}
    for split, rows in groups.items():
        x = torch.tensor([vocab.encode(f"{r['title']} {r['body']}", DL_MAX_LEN) for r in rows])
        y = torch.tensor([LABEL_MAP[r['label']] for r in rows])
        loaders[split] = DataLoader(TensorDataset(x, y), batch_size=batch_size, shuffle=split == 'train',
                                    generator=torch.Generator().manual_seed(GLOBAL_SEED))
    model, history = fit_model(vocab, loaders, epochs, dropout=.2)
    _, targets, predictions = evaluate(model, loaders['test'])
    cnn_scores = score_predictions(targets, predictions)
    _, no_dropout_history = fit_model(vocab, loaders, epochs, dropout=0.)
    nb = MultinomialNaiveBayes()
    nb.fit([f"{r['title']} {r['body']}" for r in groups['train']], [r['label'] for r in groups['train']])
    nb_predictions = [LABEL_MAP[nb.predict(f"{r['title']} {r['body']}")] for r in groups['test']]
    majority = Counter(r['label'] for r in groups['train']).most_common(1)[0][0]
    torch.save(model.state_dict(), CURATED_DATA_DIR / 'cnn_weights.pt')
    (CURATED_DATA_DIR / 'vocab.json').write_text(json.dumps(vocab.token2id), encoding='utf-8')
    report = dict(seed=GLOBAL_SEED, epochs=epochs, batch_size=batch_size, learning_rate=DL_LEARNING_RATE,
                  class_weighting="inverse square root of training class frequency",
                  selected_epoch=min(history, key=lambda h: h['val_loss'])['epoch'],
                  split_counts={s: len(r) for s,r in groups.items()}, labels=list(DL_LABELS),
                  parameters=sum(p.numel() for p in model.parameters()), vocab_size=len(vocab),
                  cnn=cnn_scores, naive_bayes=score_predictions(targets, nb_predictions),
                  majority=score_predictions(targets, [LABEL_MAP[majority]] * len(targets)),
                  history=history, no_dropout_history=no_dropout_history,
                  artifacts={name: fingerprint(CURATED_DATA_DIR/name) for name in
                             ('splits.parquet','cnn_weights.pt','vocab.json')})
    (CURATED_DATA_DIR/'dl_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    result = train_cnn()
    print(json.dumps({k:result[k] for k in ('split_counts','selected_epoch','cnn','naive_bayes','majority')}, indent=2))
