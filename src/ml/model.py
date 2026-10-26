"""1D Convolutional Neural Network (CNN) for Software Issue Classification.

Architecture:
1. Embedding Layer: maps token IDs to dense vectors.
2. 1D Convolution: captures local n-gram patterns across tokens.
3. ReLU Non-Linear Activation.
4. Global Max-over-Time Pooling: extracts dominant semantic features.
5. Dropout & Linear Head: outputs class logits (bug, enhancement, doc, question).
"""

from typing import Any


def create_issue_cnn(vocab_size: int, num_classes: int = 4, embed_dim: int = 64, num_filters: int = 64) -> Any:
    """Instantiate the 1D-CNN PyTorch model."""
    import torch
    import torch.nn as nn

    class IssueCNN(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
            self.conv = nn.Conv1d(
                in_channels=embed_dim,
                out_channels=num_filters,
                kernel_size=3,
                padding=1
            )
            self.relu = nn.ReLU()
            self.dropout = nn.Dropout(0.2)
            self.fc = nn.Linear(num_filters, num_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # x shape: (batch_size, seq_len)
            embedded = self.embedding(x)  # (batch_size, seq_len, embed_dim)
            embedded = embedded.transpose(1, 2)  # (batch_size, embed_dim, seq_len)
            conved = self.relu(self.conv(embedded))  # (batch_size, num_filters, seq_len)
            pooled = torch.max(conved, dim=2)[0]  # (batch_size, num_filters)
            dropped = self.dropout(pooled)
            return self.fc(dropped)  # (batch_size, num_classes)

    return IssueCNN()
