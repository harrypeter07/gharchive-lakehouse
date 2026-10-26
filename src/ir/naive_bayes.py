"""Multinomial Naive Bayes classifier with Laplace add-one smoothing.

Categorizes issue titles and bodies into software issue categories:
bug, enhancement, documentation, or question.
"""

from collections import Counter, defaultdict
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any

from src.ir.index import tokenize


class MultinomialNaiveBayes:
    """Multinomial Naive Bayes text classifier."""

    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha
        self.classes: List[str] = []
        self.class_doc_counts: Dict[str, int] = defaultdict(int)
        self.class_word_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.class_total_words: Dict[str, int] = defaultdict(int)
        self.vocab: set[str] = set()
        self.total_docs: int = 0

    def fit(self, texts: List[str], labels: List[str]) -> None:
        """Fit model from text documents and class labels."""
        self.classes = sorted(list(set(labels)))
        self.total_docs = len(texts)

        for text, label in zip(texts, labels):
            self.class_doc_counts[label] += 1
            tokens = tokenize(text)
            for token in tokens:
                self.vocab.add(token)
                self.class_word_counts[label][token] += 1
                self.class_total_words[label] += 1

    def predict_log_proba(self, text: str) -> Dict[str, float]:
        """Compute log posterior probability for each class."""
        tokens = tokenize(text)
        vocab_size = len(self.vocab)
        log_probs: Dict[str, float] = {}

        for c in self.classes:
            # Prior log P(c)
            prior = math.log(self.class_doc_counts[c] / self.total_docs)
            total_words = self.class_total_words[c]
            denominator = total_words + self.alpha * vocab_size

            log_likelihood = 0.0
            for token in tokens:
                if token in self.vocab:
                    word_count = self.class_word_counts[c].get(token, 0)
                    prob = (word_count + self.alpha) / denominator
                    log_likelihood += math.log(prob)

            log_probs[c] = prior + log_likelihood

        return log_probs

    def predict(self, text: str) -> str:
        """Predict highest scoring class label."""
        log_probs = self.predict_log_proba(text)
        return max(log_probs.items(), key=lambda x: x[1])[0]

    def evaluate(self, texts: List[str], true_labels: List[str]) -> Dict[str, Any]:
        """Compute accuracy, per-class metrics, and confusion matrix."""
        preds = [self.predict(t) for t in texts]
        correct = sum(1 for p, y in zip(preds, true_labels) if p == y)
        acc = correct / len(true_labels) if true_labels else 0.0

        # Confusion matrix
        confusion: Dict[str, Dict[str, int]] = {c1: {c2: 0 for c2 in self.classes} for c1 in self.classes}
        for p, y in zip(preds, true_labels):
            confusion[y][p] += 1

        # Per-class Precision, Recall, F1
        per_class: Dict[str, Dict[str, float]] = {}
        macro_f1_sum = 0.0
        for c in self.classes:
            tp = confusion[c][c]
            fp = sum(confusion[other][c] for other in self.classes if other != c)
            fn = sum(confusion[c][other] for other in self.classes if other != c)
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
            per_class[c] = {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4), "support": sum(confusion[c].values())}
            macro_f1_sum += f1

        macro_f1 = macro_f1_sum / len(self.classes) if self.classes else 0.0

        return {
            "accuracy": round(acc, 4),
            "macro_f1": round(macro_f1, 4),
            "per_class": per_class,
            "confusion_matrix": confusion
        }
