"""Inference through the actual trained model with inspectable layer outputs."""
import time
import torch
from src.common.config import DL_LABELS, DL_MAX_LEN
from src.ir.index import tokenize
from src.ml.dataset import IssueVocabulary


def predict_issue(model: torch.nn.Module, vocab: IssueVocabulary, text: str) -> dict:
    """Reject uninformative input and trace one real evaluation-mode forward pass."""
    tokens = tokenize(text)
    if not tokens:
        raise ValueError('Enter at least one meaningful word; blank text and punctuation cannot be classified.')
    encoded = vocab.encode(text, DL_MAX_LEN)
    known = sum(i > 1 for i in encoded)
    if not known:
        raise ValueError('None of these words are in the training vocabulary. Try an English software issue.')
    tensor = torch.tensor([encoded], dtype=torch.long)
    trace, hooks = {}, []
    def capture(name: str):
        def hook(module, inputs, output):
            trace[name] = list(output.shape)
        return hook
    for name in ('embedding', 'conv', 'relu', 'dropout', 'fc'):
        hooks.append(getattr(model, name).register_forward_hook(capture(name)))
    model.eval()
    start = time.perf_counter()
    try:
        with torch.inference_mode():
            logits = model(tensor)
            probabilities = torch.softmax(logits, dim=1)[0].tolist()
    finally:
        for hook in hooks:
            hook.remove()
    elapsed = (time.perf_counter()-start)*1000
    return dict(prediction=DL_LABELS[max(range(len(probabilities)), key=probabilities.__getitem__)],
                probabilities=dict(zip(DL_LABELS, probabilities)), latency_ms=elapsed,
                trace=trace, input_shape=list(tensor.shape), token_ids=encoded,
                tokens=tokens[:DL_MAX_LEN], known_tokens=known,
                unknown_tokens=sum(i == 1 for i in encoded), truncated=len(tokens)>DL_MAX_LEN)
