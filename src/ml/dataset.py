"""PyTorch Dataset and vocabulary tokenization for 1D-CNN issue classifier.

Handles deterministic token-to-id mapping, sequence padding/truncation,
and PyTorch tensor batch generation.
"""

from collections import Counter
from typing import Dict, List, Tuple
from src.ir.index import tokenize

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"
PAD_IDX = 0
UNK_IDX = 1


class IssueVocabulary:
    """Vocabulary mapping tokens to integer indices with frequency thresholding."""

    def __init__(self, min_freq: int = 2) -> None:
        self.min_freq = min_freq
        self.token2id: Dict[str, int] = {PAD_TOKEN: PAD_IDX, UNK_TOKEN: UNK_IDX}
        self.id2token: Dict[int, str] = {PAD_IDX: PAD_TOKEN, UNK_IDX: UNK_TOKEN}

    def build_from_texts(self, texts: List[str]) -> None:
        """Collect token frequencies from training texts and build vocabulary."""
        counts = Counter()
        for text in texts:
            counts.update(tokenize(text))

        idx = 2
        for token, freq in counts.items():
            if freq >= self.min_freq and token not in self.token2id:
                self.token2id[token] = idx
                self.id2token[idx] = token
                idx += 1

    def encode(self, text: str, max_len: int = 50) -> List[int]:
        """Convert text into fixed-length integer token sequence with padding/truncation."""
        tokens = tokenize(text)
        token_ids = [self.token2id.get(t, UNK_IDX) for t in tokens[:max_len]]
        if len(token_ids) < max_len:
            token_ids += [PAD_IDX] * (max_len - len(token_ids))
        return token_ids

    def __len__(self) -> int:
        return len(self.token2id)
