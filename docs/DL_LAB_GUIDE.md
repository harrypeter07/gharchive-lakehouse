# System Architecture and Technical Specification
## Automated GitHub Issue Classification Engine via 1D-Convolutional Neural Networks

**Author:** Hassan  
**Affiliation:** Department of Computer Science and Engineering, Shri Ramdeobaba College of Engineering and Management (RCOEM)  
**System Repository:** https://github.com/harrypeter07/gharchive-lakehouse  
**Live Production Host:** https://gharchive.up.railway.app  

---

## 1. Executive Summary and Profile

This platform provides an automated triage and categorization system for high-volume open-source software repositories. Software issues ingested from streaming GitHub Archive data are processed through an analytical lakehouse and classified into four operational categories in real time:

- **Bug:** Functional defects, memory faults, crashes, and exceptions.
- **Enhancement:** Feature requests, performance improvements, and architectural proposals.
- **Documentation:** README updates, API reference changes, and tutorial additions.
- **Question:** Usage inquiries, environment setup, and configuration guidance.

The core inference engine uses a custom-trained **PyTorch 1D-Convolutional Neural Network (IssueCNN)**. It achieves **77.15% overall accuracy** and **62.34% Macro-F1** with an average CPU inference latency of **1.8 milliseconds** and a model footprint of **5.19 MB**.

---

## 2. End-to-End System Pipeline

The diagram below outlines the end-to-end data processing workflow from public event stream to user interface:

```
+-------------------------------------------------------------------------+
|                         GH ARCHIVE EVENT STREAM                         |
|             Raw hourly public event archives (data.gharchive.org)       |
+-------------------------------------------------------------------------+
                                     |
                                     v  [src/ingest/download_gharchive.py]
+-------------------------------------------------------------------------+
|                              BRONZE LAYER                               |
|        Gzip-compressed JSON event streams (schema-on-read validation)   |
+-------------------------------------------------------------------------+
                                     |
                                     v  [src/ingest/clean_raw.py]
+-------------------------------------------------------------------------+
|                              SILVER LAYER                               |
|       Partitioned Snappy Parquet files with deduplication audit         |
+-------------------------------------------------------------------------+
                                     |
                                     v  [src/storage/schema.py]
+-------------------------------------------------------------------------+
|                               GOLD LAYER                                |
|        DuckDB Star Schema (fact_events, dim_repos, dim_actors)          |
+-------------------------------------------------------------------------+
                                     |
                  +------------------+------------------+
                  |                                     |
                  v [src/ml/train.py]                   v [src/search/ranker.py]
+-----------------------------------+ +-----------------------------------+
|       DEEP LEARNING ENGINE        | |       LAKEHOUSE RETRIEVAL         |
|  IssueCNN PyTorch Model           | |  BM25 In-Memory Index             |
|  1,297,412 Parameters             | |  8,000 Curated Lakehouse Issues   |
|  Dynamic 4-Class Probability Head | |  Similar Historical Resolutions   |
+-----------------------------------+ +-----------------------------------+
                  |                                     |
                  +------------------+------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                       STREAMLIT MODULAR WEB APP                         |
|             Interactive UI running on Railway Cloud Infrastructure      |
+-------------------------------------------------------------------------+
```

---

## 3. Deep Learning Neural Pipeline and Code Implementation

### 3.1 Tensor Transformation Diagram

The model processes text through a sequence of deterministic matrix operations. Below is the exact tensor dimension transformation from raw input string to class probabilities:

```
Input Text: "Panic: index out of bounds in parser loop"
   |
   |  [src/ir/index.py -> tokenize()]
   |  Regex tokenization: re.findall(r"\b[a-z0-9_]{2,}\b", text.lower())
   v
Token IDs: Vector of length L = 50, padded with 0
   Shape: [1, 50]
   |
   |  [src/ml/model.py -> nn.Embedding(20075, 64, padding_idx=0)]
   |  Each token mapped to a learned 64-dimensional dense vector
   v
Embedding Matrix
   Shape: [1, 50, 64]
   |
   |  [src/ml/model.py -> x.transpose(1, 2)]
   |  Transposed to channel-first format for 1D convolution
   v
Transposed Tensor
   Shape: [1, 64, 50]
   |
   |  [src/ml/model.py -> nn.Conv1d(in_channels=64, out_channels=64, kernel_size=3, padding=1)]
   |  64 filters slide across 3-word windows (trigrams)
   v
Feature Map
   Shape: [1, 64, 50]
   |
   |  [src/ml/model.py -> nn.ReLU()]
   |  Non-linear activation: max(0, x)
   v
Rectified Feature Map
   Shape: [1, 64, 50]
   |
   |  [src/ml/model.py -> torch.max(..., dim=2)[0]]
   |  Global max-over-time pooling extracts strongest signal per filter
   v
Pooled Feature Vector
   Shape: [1, 64]
   |
   |  [src/ml/model.py -> nn.Dropout(p=0.2)]
   |  Randomly zeroes 20% of activations during training (identity at inference)
   v
Regularized Latent Vector
   Shape: [1, 64]
   |
   |  [src/ml/model.py -> nn.Linear(in_features=64, out_features=4)]
   |  Dense projection to four class logits
   v
Raw Logits
   Shape: [1, 4]
   |
   |  [src/ml/inference.py -> torch.softmax(dim=1)]
   |  Normalizes logits into sum-to-one probabilities
   v
Output Probabilities: [Bug, Enhancement, Documentation, Question]
   Shape: [1, 4]
```

### 3.2 Code Component Mapping

The implementation is structured across modular, test-covered Python files:

- **`src/ir/index.py` (`tokenize`):**
  Extracts lowercase alphanumeric tokens using regular expressions. Strips punctuation while preserving compound technical identifiers.

- **`src/ml/dataset.py` (`IssueVocabulary`):**
  Maintains the token-to-index mapping. Sets `<pad> = 0` and `<unk> = 1`. Discards terms with frequency less than 2, resulting in a vocabulary size of 20,075 words.

- **`src/ml/model.py` (`IssueCNN`):**
  Defines the PyTorch `nn.Module` with `nn.Embedding`, `nn.Conv1d`, `nn.ReLU`, `torch.max`, `nn.Dropout`, and `nn.Linear`. Parameter count is calculated as:
  - Embedding: $20,075 \times 64 = 1,284,800$ weights.
  - Conv1d: $(64 \times 3 \times 64) + 64 = 12,352$ weights and biases.
  - Linear Head: $(64 \times 4) + 4 = 260$ weights and biases.
  - Total Parameters: **1,297,412**.

- **`src/ml/train.py` (`train_epoch`):**
  Executes mini-batch gradient descent using the Adam optimizer (`lr=0.001`, `weight_decay=1e-4`) and class-weighted cross-entropy loss.

- **`src/ml/inference.py` (`predict_issue`):**
  Runs CPU-optimized forward inference, measures execution duration via `time.perf_counter_ns()`, and captures layer output shapes in a diagnostic trace.

- **`src/search/ranker.py` (`BM25Ranker`):**
  Indexes 8,000 Lakehouse issue records using the Okapi BM25 ranking function ($k_1 = 1.5, b = 0.75$) to return relevant historical issues alongside model predictions.

---

## 4. Dataset Engineering and Split Isolation

To prevent data contamination, all records were subjected to a deduplication audit before partitioning:

- **Raw Extracted Events:** Extracted from GitHub Archive daily event dumps.
- **Deduplication:** Removed 551 duplicate issue identities and 507 identical token sequences across event timestamps.
- **Cleaned Dataset:** **14,780 distinct issues**.
- **Data Partitions:**
  - **Training Set (80%):** 11,823 samples used for gradient updates.
  - **Validation Set (10%):** 1,478 samples used for checkpoint evaluation.
  - **Test Set (10%):** 1,479 samples used strictly for final evaluation.
- **Zero-Leakage Guarantee:** Validated by `tests/test_dl_lab.py`, ensuring zero overlap in issue identifiers and token sequences between train, validation, and test sets.

```
+--------------------------------------------------------------------------+
|                          CLEANED DATASET: 14,780                         |
+-----------------------------------+--------------------+-----------------+
|          TRAIN: 11,823 (80%)      |   VAL: 1,478 (10%) | TEST: 1,479(10%)|
|          Gradient Updates         |   Model Selection  | Final Benchmark |
+-----------------------------------+--------------------+-----------------+
```

---

## 5. Training Dynamics and Regularization

### 5.1 Optimization Configuration
- **Algorithm:** Adam (`torch.optim.Adam`).
- **Learning Rate:** $0.001$.
- **Weight Decay ($L_2$):** $10^{-4}$.
- **Batch Size:** 64.
- **Training Epochs:** 8.
- **Loss Function:** Class-weighted Cross-Entropy to address class imbalance:
  $$w_c = \frac{1}{\sqrt{N_c}}$$

### 5.2 Regularization Ablation (Dropout Effect)
An ablation experiment recorded in `data/curated/dl_report.json` demonstrates the impact of dropout regularization:

```
Validation Loss Comparison across 8 Epochs:

Epoch:          1      2      3      4      5      6      7      8
--------------------------------------------------------------------
Without Dropout: 0.82   0.68   0.65   0.78   0.94   1.08   1.19   1.25  (Diverges / Overfits)
With Dropout 0.2: 0.74   0.58   0.51   0.47   0.45   0.44   0.44   0.44  (Converges / Stable)
```

Without dropout, the network memorizes training tokens, leading to validation loss divergence by epoch 4. With `Dropout(p=0.2)`, validation loss stabilizes at 0.44.

---

## 6. Empirical Performance Benchmarks

Performance evaluated on the 1,479 held-out test issues:

| Model Architecture | Paradigm | Accuracy | Macro-F1 | CPU Latency | Parameter Footprint |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Majority Baseline** | Constant "Bug" prediction | 44.69% | 15.44% | 0.0 ms | 0 KB |
| **Multinomial Naive Bayes** | Probabilistic Bag-of-Words | 74.65% | 50.85% | < 0.5 ms | Sparse Matrix |
| **IssueCNN (PyTorch)** | **1D-Convolutional Neural Network** | **77.15%** | **62.34%** | **1.8 ms** | **5.19 MB** |

### Per-Class Test Set Evaluation

| Category | Test Support | Precision | Recall | F1-Score | Dominant Indicator Patterns |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Bug** | 661 | 79.36% | 82.60% | **80.95%** | `crash`, `panic`, `exception`, `segfault`, `failed` |
| **Enhancement** | 626 | 76.33% | 80.35% | **78.29%** | `add`, `support`, `feature`, `allow`, `option` |
| **Documentation** | 144 | 70.59% | 58.33% | **63.88%** | `readme`, `docs`, `typo`, `guide`, `example` |
| **Question** | 48 | 61.54% | 16.67% | **26.23%** | `how`, `why`, `where`, `configure`, `help` |

**Why Macro-F1 Matters:**  
Open-source issue trackers have an inherent class imbalance. Bugs and Enhancements make up 87% of all incoming issues, while Questions make up only 3.2%. A model predicting only the majority classes could achieve high accuracy while failing entirely on questions. Macro-F1 gives equal weight to all four classes, reflecting true multi-class capability.

---

## 7. Production Deployment and Infrastructure

- **Containerization:** Multi-stage `Dockerfile` using `python:3.11-slim` and CPU-specific PyTorch binaries (`torch==2.14.1+cpu`) to keep container image size minimal and build times fast.
- **Cloud Hosting:** Hosted on Railway with dynamic `$PORT` assignment and automated healthcheck probes.
- **Operational Serving:** Streamlit interface (`src/app/main.py`) provides real-time model inference, layer tensor inspection, and similarity lookup against Lakehouse data.
- **Inference Latency:** Sub-2ms per query on single CPU core without external GPU dependencies.

---

## 8. Technical Architecture Q&A

**1. Why use a 1D-CNN instead of a Recurrent Neural Network (LSTM/GRU) or a Transformer?**  
- **Parallelism:** 1D-CNNs compute convolutions across the full sequence simultaneously in $O(1)$ sequential operations, unlike RNNs which require $O(N)$ sequential steps.
- **Efficiency:** Standard Transformers incur quadratic attention cost $O(N^2)$ and require large parameter footprints (100M+ parameters). IssueCNN requires only 1.29M parameters and 5.19 MB of memory.
- **Suitability:** For software issue triage, local n-grams (such as "null pointer exception" or "update readme instructions") provide the strongest predictive signals, making 3-word convolutional kernels well-suited for the task.

**2. How are out-of-vocabulary (OOV) tokens and padding managed?**  
- Vocabulary terms occurring fewer than 2 times in the training data map to index 1 (`<unk>`).
- Sequences shorter than 50 tokens are padded with index 0 (`<pad>`). In PyTorch, `nn.Embedding(..., padding_idx=0)` ensures that the padding embedding vector remains zero and receives zero gradient updates during backpropagation.

**3. What explains the lower F1-score on the Question class?**  
- The Question class represents only 3.2% of the real-world dataset (48 test instances out of 1,479).
- Due to limited training volume, question representations receive fewer gradient updates.
- Applying inverse square-root class weighting enabled the 1D-CNN to correctly identify 8 questions, whereas the baseline Naive Bayes model identified 0.
