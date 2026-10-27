# Deep Learning Lab Project Guide 🧠
**GitHub Issue Classification Engine & Academic Practical Alignment**
**Author**: Hassan · B.Tech CSE · Shri Ramdeobaba College of Engineering and Management (RCOEM)

---

## 1. 👶 Explain Like I'm 10: How It Works

Imagine you work inside an enormous, bustling mailroom where **thousands of letters (GitHub issues)** arrive every single day. Your job is to quickly inspect each letter and sort it into one of **4 color-coded baskets**:
- 🐞 **Bug**: Something is broken, crashing, or throwing an error.
- ✨ **Enhancement**: A developer asking for a new feature or button.
- 📚 **Documentation**: A missing tutorial, guide, or typo in the README.
- ❓ **Question**: A confused user asking how to configure their setup.

Instead of hiring 10 people to read every word, we built a **trained PyTorch Deep Learning Robot** (`IssueCNN`) that reads the letter and sorts it in under **2 milliseconds**.

```
[Raw Issue Title & Body]
          │
          ▼
   1. Tokenizer ──▶ Converts words to integer numbers (Vocab: 20,075 words)
          │
          ▼
   2. Embedding Layer ──▶ Maps each word number into a 64-dimensional concept coordinate
          │
          ▼
   3. 1D Convolution ──▶ 64 sliding magnifying glasses (width=3 words) scan for trigger phrases
          │
          ▼
   4. Global Max-Pooling ──▶ Remembers only the loudest clue found across the whole sentence
          │
          ▼
   5. Dropout (p=0.2) ──▶ Blindfolds 20% of clues during training to prevent memorization
          │
          ▼
   6. Dense + Softmax Head ──▶ 4 voting judges output exact percentages adding up to 100%
```

---

## 2. 🎓 How This Project Directly Implements Your 4 College Lab Practicals

Your professor assigned specific practical topics in the Deep Learning syllabus. Here is how our production GitHub issue classifier uses every single one:

### Practical 6: Convolutional Neural Networks (1D Text Convolutions)
- **In the syllabus**: Calculating matrix convolutions with sliding kernels, stride, padding, downsampling/pooling, and flattening.
- **In our real project**: Instead of pixels in an image, our network applies **1D temporal convolutions** (`nn.Conv1d(in_channels=64, out_channels=64, kernel_size=3, padding=1)`).
- **The intuition**: The 64 filters slide across 3-word windows (trigrams). When a filter detects a clue like *"segmentation fault in"* or *"how to install"*, it fires a high activation score. **Global Max-Pooling** (`torch.max`) extracts the strongest clue regardless of where it appeared in the sentence.

### Practical 5: Study of Regularizers (Preventing Overfitting)
- **In the syllabus**: Studying L1, L2 (Weight Decay), Dropout, and Early Stopping.
- **In our real project**: A neural network with 1.29 million parameters can easily "cheat" by memorizing exact phrases from the training set (overfitting).
- **The solution**: We integrated `nn.Dropout(p=0.2)`. During every training step, 20% of neuron outputs are randomly muted to zero. This forces the model to learn robust, distributed representations across multiple words. Without dropout, validation loss diverges; with dropout, the model generalizes safely to new unseen GitHub issues.

### Practical 4: Study of Optimizers & Mini-Batching
- **In the syllabus**: Comparing Gradient Descent algorithms (Vanilla SGD, Momentum, RMSProp, Adam) and batching methods.
- **In our real project**: The network's 1,297,412 weights are trained using **Adam (`torch.optim.Adam`, lr=0.001)** on **mini-batches of 64 issues**.
- **Why Adam?** Standard SGD takes equal steps everywhere, causing it to bounce wildly across steep slopes. Adam computes adaptive learning rates for each parameter using running averages of past gradients (momentum) and squared gradients (variance), descending smoothly into the loss minimum.

### Practical 3: Feedforward Neural Network & Softmax
- **In the syllabus**: Multi-layer perceptrons, backpropagation, and multi-class activation functions.
- **In our real project**: Once the CNN extracts the 64 dominant semantic features, they pass into a **Dense classification head** (`nn.Linear(64, 4)`).
- **Softmax Activation**: Softmax normalizes the 4 raw linear outputs (logits) into a true probability distribution ($P_1 + P_2 + P_3 + P_4 = 1.0$), allowing the system to output confident, calibrated predictions.

---

## 3. 🔬 Honest Measured Results (Zero Fake Data)

All numbers shown in this dashboard and report are measured directly from the verified dataset (`data/curated/dl_report.json`):

| Metric | PyTorch 1D-CNN | Naive Bayes Baseline | Majority-Class Baseline |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **77.15%** | 74.65% | 44.69% |
| **Macro-F1 (Equal Class Weight)** | **62.34%** | 50.85% | 15.44% |
| **Trainable Parameters** | **1,297,412** | 0 (Statistical counts) | 0 |
| **CPU Inference Latency** | **~1.8 ms** | < 0.5 ms | 0 ms |

### Strict Split Isolation (No Data Leakage):
- Total Cleaned & Deduplicated Issues: **14,780**
- **Training Set (80%)**: 11,823 samples
- **Validation Set (10%)**: 1,478 samples
- **Test Set (10%)**: 1,479 samples
- **Audit Verification**: Every duplicate issue ID and repeated token sequence was removed prior to splitting. Zero training sentences exist in the test split!

### Honest Breakdown by Category (Real Class Imbalance):
In real open-source software, bugs and feature requests are common, while questions and documentation are rare:
- 🐞 **Bug** (661 test samples): **80.95% F1** (Precision: 79.4%, Recall: 82.6%)
- ✨ **Enhancement** (626 test samples): **78.29% F1** (Precision: 76.3%, Recall: 80.4%)
- 📚 **Documentation** (144 test samples): **63.88% F1** (Precision: 70.6%, Recall: 58.3%)
- ❓ **Question** (48 test samples): **26.23% F1** (Precision: 61.5%, Recall: 16.7% — 8 of 48 detected)

> 💡 **Key Viva Insight**: The model performs well on Bugs and Features, but struggles on Questions because only 48 test examples exist. Naive Bayes failed completely on Questions (0% F1), whereas our CNN successfully identified 8 questions, demonstrating superior semantic capture despite severe data rarity!

---

## 4. 🎯 What This Lab Implements vs. What It Does Not

To maintain academic honesty during evaluation:
- ✅ **What this project DOES implement**: A full, real-world, end-to-end NLP Deep Learning system demonstrating 1D Convolution, Max-Pooling, Adam Optimization, Dropout Regularization, and Feedforward Softmax Classification on 14,780 real GitHub issues.
- ❌ **What this project DOES NOT claim to implement**: It does not implement 2D handwritten digit recognition (MNIST) or pretrained image vision models (like ResNet or VGG16), because our lakehouse dataset consists of technical text rather than image pixels.

---

## 5. 🗣️ Viva Voce Examination Cheat Sheet

**Q1: Why use a 1D-CNN for text rather than an LSTM, RNN, or Transformer?**
> *Answer*: "1D-CNNs compute all n-gram filters in parallel $O(1)$ operations on CPU, avoiding the sequential bottleneck of RNNs/LSTMs. For short software issue text, local 3-word phrases like 'segmentation fault' provide sufficient classification signal, achieving 77.15% accuracy in 1.8 ms without the multi-gigabyte memory overhead of Transformers."

**Q2: What is the difference between Accuracy and Macro-F1?**
> *Answer*: "Accuracy measures total correct predictions, which can be misleading on imbalanced datasets (e.g., predicting only Bugs and Enhancements yields 75% accuracy while ignoring Questions). Macro-F1 calculates F1 independently for each of the 4 classes and computes their unweighted average, ensuring rare classes like Questions and Docs are fairly evaluated."

**Q3: How does Dropout prevent overfitting in our model?**
> *Answer*: "With `nn.Dropout(0.2)`, 20% of neuron activations are randomly set to zero during each training forward pass. This prevents complex co-adaptations between neurons, forcing the network to learn robust, generalized patterns rather than memorizing specific training phrases."

**Q4: How does the embedding layer handle unknown out-of-vocabulary (OOV) words?**
> *Answer*: "Tokens that appeared fewer than twice during training or words never seen before map to index 1 (`<unk>`). Reserved index 0 is used for `<pad>` with `padding_idx=0` in PyTorch, guaranteeing that padding vectors receive zero gradient updates."
