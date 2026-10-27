# Experimental Results & Model Evaluation

Generated on: 2026-10-26 14:46:15 UTC

## 1. Information Retrieval (IR) Benchmarks
- **Corpus Size**: 15,324 indexed GitHub issue documents
- **Vocabulary Size**: 53,442 unique terms
- **Average Document Length**: 35.35 tokens
- **Test Query Set**: 20 developer and DevOps search queries

| Model | Smoothing / Tuning | Top-10 Retrieval Rate |
| :--- | :--- | :--- |
| **BM25** | $k_1=1.5, b=0.75$ | 10.0 / 10 results/query |
| **Language Model (QLM)** | Dirichlet prior $\mu=2000.0$ | 10.0 / 10 results/query |

---

## 2. Multinomial Naive Bayes Issue Classifier
- **Train split**: 13,622 samples
- **Test split**: 1,704 samples
- **Overall Accuracy**: **75.94%**
- **Macro F1-Score**: **56.22%**

### Per-Class Performance
| Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **bug** | 0.7535 | 0.8427 | 0.7956 | 693 |
| **documentation** | 0.7978 | 0.3944 | 0.5279 | 180 |
| **enhancement** | 0.7596 | 0.8172 | 0.7874 | 777 |
| **question** | 1.0000 | 0.0741 | 0.1379 | 54 |

### Confusion Matrix (Rows = Actual, Columns = Predicted)

| Actual \ Predicted | bug | documentation | enhancement | question |
| :--- | :---: | :---: | :---: | :---: |
| **bug** | 584 | 4 | 105 | 0 |
| **documentation** | 33 | 71 | 76 | 0 |
| **enhancement** | 129 | 13 | 635 | 0 |
| **question** | 29 | 1 | 20 | 4 |

## 3. Deep Learning: 1D-CNN Classifier
- **Architecture**: Embedding(dim=64) -> Conv1D(64, kernel=3) -> ReLU -> MaxPool1D -> Dropout(0.2) -> Linear(4)
- **Vocabulary Size (Train Only)**: 22,415 tokens
- **Training Epochs**: 4
- **Test Accuracy**: **78.81%**
- **Macro F1-Score**: **60.72%**

### Model Comparison
| Model | Type | Test Accuracy | Macro F1 |
| :--- | :--- | :--- | :--- |
| **Multinomial Naive Bayes** | Probabilistic n-gram | 75.94% | 56.22% |
| **1D-CNN** | Deep Convolutional | **78.81%** | **60.72%** |
