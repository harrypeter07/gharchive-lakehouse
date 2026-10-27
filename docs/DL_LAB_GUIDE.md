# System Architecture & Technical Specification
## Automated GitHub Issue Classification Engine via 1D-Convolutional Neural Networks
**Lead Engineer / Author:** Hassan  
**Affiliation:** Department of Computer Science & Engineering, Shri Ramdeobaba College of Engineering and Management (RCOEM)  
**System Repository:** https://github.com/harrypeter07/gharchive-lakehouse  
**Live Production Host:** https://gharchive.up.railway.app  

---

## 1. Executive Summary & Author Profile

In modern distributed software engineering, open-source repositories receive tens of thousands of developer tickets, crash reports, and feature requests every hour. Manually triaging incoming reports is labor-intensive, creating backlogs that delay critical bug patches and architectural improvements.

This project delivers an end-to-end, high-throughput automated classification platform. Incoming software issue tickets are ingested from streaming GitHub Archive data, cleaned through a zero-loss analytical lakehouse, and categorized in real time into four operational classes:
- **Bug**: Functional defects, segmentation faults, memory leaks, and runtime errors.
- **Enhancement**: Feature proposals, architectural requests, and performance optimizations.
- **Documentation**: Typo corrections, API documentation updates, and tutorial enhancements.
- **Question**: Configuration guidance, deployment inquiries, and general usage questions.

Rather than relying on brittle keyword rules or heavy generative models with prohibitive computational requirements, the core inference engine utilizes a custom-trained **PyTorch 1D-Convolutional Neural Network (IssueCNN)**. The system achieves **77.15% overall accuracy** and **62.34% Macro-F1** with a sub-2 millisecond inference latency on commodity CPU hardware.

---

## 2. Deep Learning Pipeline & Model Architecture

While standard 2D Convolutional Neural Networks operate across spatial dimensions (height and width pixels), our architecture applies **1D temporal convolutions over dense word embeddings**, capturing local n-gram semantic patterns across variable-length technical text.

```
[Raw Issue Title & Description]
             │
             ▼
   1. Tokenization & Sequence Standardization (L = 50 tokens)
             │
             ▼
   2. Embedding Layer (Vocabulary = 20,075 -> Dimension = 64)
             │
             ▼
   3. 1D Convolution (64 Filters, Kernel Size = 3, Padding = 1)
             │
             ▼
   4. Non-Linear Activation (Rectified Linear Unit - ReLU)
             │
             ▼
   5. Global Max-Over-Time Pooling (Extracts Dominant Feature Vector -> [1, 64])
             │
             ▼
   6. Dropout Regularization (p = 0.2 during training)
             │
             ▼
   7. Dense Linear Head & Softmax (Projects [1, 64] -> 4 Class Probabilities)
```

### Layer-by-Layer Mathematical Formulation

1. **Tokenization and Embedding Lookup:**
   Input text is tokenized into integer indices $x = (w_1, w_2, \dots, w_L)$ truncated or padded to a fixed sequence length $L = 50$. Each token index maps to a 64-dimensional dense semantic vector via an embedding matrix $E \in \mathbb{R}^{|V| \times d}$, where $|V| = 20,075$ and $d = 64$:
   $$X = \text{Embedding}(x) \in \mathbb{R}^{L \times d}$$

2. **1D Convolution (Temporal Phrase Scanning):**
   The embedded representation is transposed to $\mathbb{R}^{d \times L}$. We define 64 convolutional filters $W^{(j)} \in \mathbb{R}^{k \times d}$ with kernel size $k = 3$ (scanning 3-word windows). For each position $t \in [1, L]$:
   $$c_t^{(j)} = \text{ReLU}\left( \sum_{i=1}^{k} \langle W_i^{(j)}, X_{t+i-1} \rangle + b^{(j)} \right)$$

3. **Global Max-Over-Time Pooling:**
   To make classification position-invariant (so that critical indicators like *"fatal segmentation fault"* are detected regardless of sentence placement), the model extracts the maximum activation per filter:
   $$\hat{c}^{(j)} = \max_{1 \le t \le L} c_t^{(j)} \quad \implies \quad \mathbf{h} = [\hat{c}^{(1)}, \hat{c}^{(2)}, \dots, \hat{c}^{(64)}]^T \in \mathbb{R}^{64}$$

4. **Dropout Regularization:**
   During training, a Bernoulli dropout mask zeroes out 20% of the pooled feature dimensions ($p=0.2$):
   $$\mathbf{\tilde{h}} = \mathbf{r} \odot \mathbf{h}, \quad r_i \sim \text{Bernoulli}(1 - p)$$

5. **Linear Projection & Softmax Head:**
   The regularized vector is projected into 4 operational logits via a linear layer $W_c \in \mathbb{R}^{4 \times 64}, b_c \in \mathbb{R}^4$:
   $$\mathbf{z} = W_c \mathbf{\tilde{h}} + b_c$$
   $$\hat{y}_c = P(y = c \mid x) = \frac{\exp(z_c)}{\sum_{k=1}^4 \exp(z_k)}, \quad c \in \{1, 2, 3, 4\}$$

---

## 3. Dataset Engineering & Zero-Leakage Audit

The model was trained on real open-source issue activity from GitHub Archive. To maintain academic and industrial integrity, the raw stream was subjected to a comprehensive deduplication and split-isolation audit:

- **Raw Stream Ingestion:** Extracted from hourly GH Archive event dumps.
- **Deduplication Audit:** Identified and removed 551 duplicate issue identities and 507 identical token sequences across event timestamps.
- **Final Cleaned Dataset:** **14,780 unique issues**.
- **Split Partitions:**
  - **Training Set (80%):** 11,823 samples (used exclusively for gradient optimization).
  - **Validation Set (10%):** 1,478 samples (used for checkpointing and early stopping).
  - **Test Set (10%):** 1,479 samples (unseen holdout for final benchmark reporting).
- **Leakage Prevention Assertion:** Mathematically verified via cryptographic hashing that zero overlap exists across train, validation, and test partitions (`tests/test_dl_lab.py`).

---

## 4. Optimization Strategy & Training Dynamics

- **Optimizer:** `torch.optim.Adam` with learning rate $\alpha = 0.001$ and $L_2$ weight decay $\lambda = 10^{-4}$.
- **Mini-Batch Size:** 64 samples per step.
- **Epoch Budget:** 8 full passes over the training set.
- **Loss Function:** Multi-Class Cross-Entropy with inverse square root class-frequency weighting to counteract minority class suppression:
  $$\mathcal{L} = -\sum_{c=1}^4 w_c \cdot y_c \log \hat{y}_c, \quad w_c = \frac{1}{\sqrt{N_c}}$$
- **Overfitting Prevention Evidence:** A controlled ablation experiment was logged (`data/curated/dl_report.json`). Without dropout, validation loss diverged past epoch 3 (reaching 1.25); with `Dropout(0.2)`, validation loss stabilized at 0.44 across all 8 epochs.

---

## 5. Measured Experimental Benchmarks

Performance was evaluated on the 1,479 held-out test issues. All metrics are empirically verified:

| Architecture / Model | Modeling Paradigm | Accuracy | Macro-F1 | Inference Latency | Model Footprint |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Majority-Class Baseline** | Predicts "Bug" always | 44.69% | 15.44% | 0.0 ms | 0 KB |
| **Multinomial Naive Bayes** | Probabilistic Bag-of-Words ($\alpha=1.0$) | 74.65% | 50.85% | < 0.5 ms | Sparse Matrix |
| **PyTorch 1D-CNN (IssueCNN)** | **Deep Neural Network** | **77.15%** | **62.34%** | **1.8 ms** | **5.19 MB** |

### Detailed Per-Class Breakdown

| Category | Test Support | Precision | Recall | F1-Score | Operational Analysis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Bug** | 661 | 79.36% | 82.60% | **80.95%** | High technical term density (`panic`, `segfault`, `error`). |
| **Enhancement** | 626 | 76.33% | 80.35% | **78.29%** | Frequent proposal vocabulary (`add`, `support`, `feature`). |
| **Documentation** | 144 | 70.59% | 58.33% | **63.88%** | Medium volume; localized cues (`readme`, `typo`, `guide`). |
| **Question** | 48 | 61.54% | 16.67% | **26.23%** | Extreme natural minority (3.2% of test set); CNN identified 8 of 48 (Naive Bayes identified 0). |

**Macro-F1 Justification:** Because open-source software produces substantially more bug reports and feature requests than documentation fixes or configuration questions, overall accuracy is skewed toward the majority classes. Macro-F1 assigns equal weight to all four classes, preventing minority class failures from being concealed behind high accuracy.

---

## 6. Production Deployment & Cloud Serving

- **Application Framework:** Streamlit 1.66 modular architecture with distinct functional modules (`src/app/tabs/`).
- **Containerization:** Multi-stage `Dockerfile` based on `python:3.11-slim`, utilizing official CPU-only PyTorch wheels (`torch==2.14.1+cpu`) to optimize memory footprint and build caching.
- **Cloud Infrastructure:** Hosted on Railway with dynamic `$PORT` binding, live container healthchecks, and sub-2ms response latency.
- **Integrated Lakehouse Retrieval:** In addition to category triage, the system queries an in-memory Okapi BM25 index over 8,000 Lakehouse records, retrieving real past issues and historical resolutions for developer context.

---

## 7. Technical Examination & Architectural Defense

**Q1: Why was a 1D-CNN chosen instead of a recurrent network (LSTM/GRU) or a Transformer?**  
*Response:* 1D-CNNs evaluate all sequence filters in parallel ($O(1)$ parallel time complexity) rather than sequentially ($O(N)$ for recurrent architectures). For short-to-medium technical texts, local 3-word n-grams provide strong discriminative signal. A 1D-CNN delivers sub-2ms CPU inference and a 5.19 MB memory footprint, avoiding the latency and compute demands of self-attention Transformers on commodity hardware.

**Q2: What is the exact role of Dropout in this architecture?**  
*Response:* With 1,297,412 parameters, the model could easily overfit to training vocabularies. Setting $p=0.2$ randomly deactivates 20% of activations during training forward passes. This prevents co-adaptation, forcing the network to develop redundant semantic paths across multiple words.

**Q3: How does the embedding layer handle out-of-vocabulary (OOV) tokens and padding?**  
*Response:* Words occurring fewer than twice during training map to index 1 (`<unk>`). Index 0 is reserved for `<pad>` with `padding_idx=0` in PyTorch, guaranteeing that padding vectors remain zero and receive zero gradient updates during backpropagation.

**Q4: Why is the Macro-F1 score on Questions lower than on Bugs?**  
*Response:* Real GitHub data exhibits severe class imbalance: the test partition contains 661 Bugs and 626 Enhancements, but only 48 Questions. Due to this natural scarcity, the model receives fewer gradient updates for question syntax. However, inverse frequency weighting enabled the 1D-CNN to capture 8 questions, whereas Naive Bayes scored 0%.
