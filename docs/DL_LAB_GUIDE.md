# Information Retrieval & Probabilistic Text Intelligence Engine
## Academic Practical Specification & System Architecture

**Affiliation:** Department of Computer Science and Engineering, Shri Ramdeobaba College of Engineering and Management (RCOEM)  
**System Repository:** https://github.com/harrypeter07/gharchive-lakehouse  
**Live Production Host:** https://gharchive.up.railway.app  

---

## 1. Executive Summary & Core IR Architecture

This platform implements an enterprise-grade Information Retrieval (IR) and Probabilistic Language Modeling engine designed for automated discovery, defect deduplication, and classification across massive open-source software streams.

The engine processes 14,780 curated GitHub issue documents across 57,306 unique vocabulary terms, implementing three foundational pillars of modern Information Retrieval:

1. **Probabilistic IR using Okapi BM25 Ranking:** Incorporating Robertson-Spärck Jones IDF, non-linear term frequency saturation ($k_1=1.5$), document length penalization ($b=0.75$), and query coordination matching.
2. **Language Model-Based Information Retrieval using Unigram Language Models:** Evaluating query likelihood under a smoothed unigram multinomial distribution with Bayesian Dirichlet Prior Smoothing ($\mu=2000.0$) and Jelinek-Mercer Linear Interpolation ($\lambda=0.7$).
3. **Supervised Text Classification using Multinomial Naive Bayes:** Probabilistic bag-of-words categorization with Laplace add-one smoothing ($\alpha=1.0$), establishing an empirical baseline against neural classifiers.

---

## 2. End-to-End System Pipeline

The following diagram illustrates how raw GitHub Archive event data flows into the Inverted Index, ranking models, and classification layers:

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
                                     v  [src/ir/index.py]
+-------------------------------------------------------------------------+
|                         INVERTED INDEX ENGINE                           |
|  - Tokenizer: Regex \b[a-z0-9_]{2,}\b (35 English Stopwords Excluded)   |
|  - Postings Lists: Term -> [(doc_id, term_frequency)]                   |
|  - Corpus Statistics: N = 14,780 docs | |V| = 57,306 terms | avgdl = 35.3|
+-------------------------------------------------------------------------+
                                     |
         +---------------------------+---------------------------+
         |                                                       |
         v [src/ir/bm25.py]                                      v [src/ir/lm.py]
+-----------------------------------+   +-----------------------------------+
|      OKAPI BM25 RANKER            |   |     UNIGRAM LANGUAGE MODEL        |
|  - Robertson-Spärck Jones IDF     |   |  - Bayesian Dirichlet Smoothing   |
|  - TF Saturation (k1 = 1.5)       |   |    Prior mu = 2000.0              |
|  - Length Normalization (b=0.75)  |   |  - Query Likelihood Log-Prob      |
|  - Query Coordination Boost       |   |  - Jelinek-Mercer Interpolation   |
+-----------------------------------+   +-----------------------------------+
         |                                                       |
         +---------------------------+---------------------------+
                                     |
                                     v  [src/ir/naive_bayes.py]
+-------------------------------------------------------------------------+
|                     MULTINOMIAL NAIVE BAYES CLASSIFIER                  |
|  - Prior Class Probabilities P(c) over 4 classes                        |
|  - Laplace Smoothing (alpha = 1.0) on feature likelihoods               |
|  - Output: bug (80% F1), enhancement (78% F1), docs (53% F1), q (14% F1)|
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    STREAMLIT REVENUE & RESEARCH INTERFACE               |
|  Sub-millisecond query execution with live highlighting & AI fix solver |
+-------------------------------------------------------------------------+
```

---

## 3. Academic Practical Alignments & Mathematical Formulations

### Practical A: Probabilistic Information Retrieval using BM25 Ranking
- **Source File:** `src/ir/bm25.py` (`BM25Ranker`)
- **Mathematical Foundation:**
  BM25 computes relevance scores based on the Robertson-Spärck Jones probabilistic model:
  
  $$\text{Score}(D, Q) = \sum_{t \in Q} \text{IDF}(t) \cdot \frac{tf_{t, D} \cdot (k_1 + 1)}{tf_{t, D} + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)} \cdot \left(1 + \gamma \cdot \text{Coord}(Q, D)\right)$$

  Where:
  - $\text{IDF}(t) = \ln\left(1 + \frac{N - df_t + 0.5}{df_t + 0.5}\right)$ is the Robertson-Spärck Jones Inverse Document Frequency with additive smoothing to avoid negative weights for common words.
  - $tf_{t, D}$ is the term frequency of token $t$ in document $D$.
  - $|D|$ is the length of document $D$ in tokens, and $\text{avgdl}$ is the average document length across the corpus ($35.35$ tokens).
  - $k_1 = 1.5$ regulates term frequency saturation. As $tf$ increases, marginal gain asymptotically approaches $k_1 + 1$.
  - $b = 0.75$ controls document length normalization, penalizing verbose documents that mention keywords purely by chance.
  - $\text{Coord}(Q, D) = \left(\frac{|Q \cap D|}{|Q|}\right)^2$ provides coordination matching, heavily rewarding documents that satisfy multiple query dimensions simultaneously.

### Practical B: Language Model-Based Retrieval using Unigram Language Model
- **Source File:** `src/ir/lm.py` (`LanguageModelRanker`)
- **Mathematical Foundation:**
  Under the Query Likelihood framework, a document is viewed as a multinomial generative model $\theta_D$. Documents are ranked by the posterior log-likelihood of generating query terms $Q = (q_1, q_2, \dots, q_m)$:

  $$\ln P(Q \mid \theta_D) = \sum_{t \in Q} \ln P(t \mid \theta_D)$$

  Because raw maximum likelihood estimates produce zero probabilities for missing query tokens ($tf_{t, D} = 0$), smoothing against the background collection language model $P(t \mid C) = \frac{cf_t}{|C|}$ is mandatory.

  **1. Bayesian Dirichlet Prior Smoothing (Default, $\mu = 2000.0$):**
  Treating collection frequencies as pseudo-counts under a Dirichlet conjugate prior:
  
  $$P(t \mid \theta_D) = \frac{tf_{t, D} + \mu \cdot \frac{cf_t}{|C|}}{|D| + \mu}$$

  **2. Jelinek-Mercer Linear Interpolation Smoothing ($\lambda = 0.7$):**
  Direct linear combination of document maximum likelihood and background collection probability:
  
  $$P(t \mid \theta_D) = \lambda \frac{tf_{t, D}}{|D|} + (1 - \lambda) \frac{cf_t}{|C|}$$

### Practical C: Text Classification using Multinomial Naive Bayes
- **Source File:** `src/ir/naive_bayes.py` (`MultinomialNaiveBayes`)
- **Mathematical Foundation:**
  Multinomial Naive Bayes calculates the maximum a posteriori (MAP) class for a document $d = (t_1, t_2, \dots, t_n)$:

  $$\hat{c} = \arg\max_{c \in C} \left[ \ln P(c) + \sum_{i=1}^n \ln P(t_i \mid c) \right]$$

  Where:
  - Prior probability: $P(c) = \frac{N_c}{N}$
  - Likelihood with Laplace add-one smoothing ($\alpha = 1.0$):
    $$P(t \mid c) = \frac{N_{c, t} + \alpha}{N_c + \alpha \cdot |V|}$$
  - $N_{c, t}$ is the count of term $t$ in class $c$, $N_c$ is the total token count in class $c$, and $|V| = 57,306$ is the vocabulary dimension.

---

## 4. Empirical Evaluation & Benchmark Results

All models were evaluated on the held-out test partition consisting of real open-source GitHub issues:

### 4.1 Information Retrieval Performance Benchmarks

| Retrieval Model | Configuration | Corpus Size | Query Evaluation Set | Mean Response Latency | Top-10 Retrieval Rate |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Okapi BM25 Ranker** | $k_1 = 1.5, b = 0.75$, Coord | 14,780 docs | 20 Developer Queries | **0.82 ms** | **10.0 / 10 (100%)** |
| **Language Model (QLM)** | Dirichlet $\mu = 2000.0$ | 14,780 docs | 20 Developer Queries | **1.14 ms** | **10.0 / 10 (100%)** |
| **Language Model (JM)** | Linear $\lambda = 0.70$ | 14,780 docs | 20 Developer Queries | **1.05 ms** | **10.0 / 10 (100%)** |

### 4.2 Text Classification Benchmarks

| Model Architecture | Paradigm | Overall Accuracy | Macro-F1 | Inference Speed | Memory Footprint |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Majority Baseline** | Constant "Bug" assignment | 44.69% | 15.44% | 0.0 ms | 0 KB |
| **Multinomial Naive Bayes** | Probabilistic Bag-of-Words | **75.94%** | **56.22%** | **< 0.4 ms** | **1.4 MB** |
| **IssueCNN (PyTorch 1D-CNN)** | Deep Convolutional Neural Network | **77.15%** | **62.34%** | **1.8 ms** | **5.19 MB** |

### 4.3 Naive Bayes Per-Class Confusion Matrix (Test Split: 1,704 Issues)

| Actual \ Predicted | Bug | Enhancement | Documentation | Question | Class Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bug** | **584** | 105 | 4 | 0 | 693 | 75.35% | 84.27% | **79.56%** |
| **Enhancement** | 129 | **635** | 13 | 0 | 777 | 75.96% | 81.72% | **78.74%** |
| **Documentation** | 33 | 76 | **71** | 0 | 180 | 79.78% | 39.44% | **52.79%** |
| **Question** | 29 | 20 | 1 | **4** | 54 | 100.0% | 7.41% | **13.79%** |

---

## 5. Architectural Implementation Mapping

The implementation code is organized into modular Python components:

- **`src/ir/index.py`:**
  - `InvertedIndex`: Manages postings lists, document frequencies, and length arrays.
  - `tokenize`: Applies regex tokenization with stopword filtering.
- **`src/ir/bm25.py`:**
  - `BM25Ranker`: Executes Okapi BM25 scoring with Robertson-Spärck Jones IDF and query coordination boosting.
- **`src/ir/lm.py`:**
  - `LanguageModelRanker`: Implements Query Likelihood retrieval with Dirichlet and Jelinek-Mercer smoothing.
- **`src/ir/naive_bayes.py`:**
  - `MultinomialNaiveBayes`: Implements log-space Bayesian classification with Laplace smoothing.
- **`src/ir/evaluate.py`:**
  - Automated benchmark runner validating retrieval rates across 20 standard engineering queries.
- **`src/app/tabs/search.py`:**
  - Production search interface featuring live keyword highlighting, coordination match percentages, and triage resolution insights.
- **`src/app/tabs/solver.py`:**
  - AI-assisted issue solution module integrating Google Search grounding to retrieve live GitHub commits and propose verified code fixes.

---

## 6. Technical Examination Defense

**1. What is the fundamental difference between BM25 and Query Likelihood Language Models?**  
BM25 is a probabilistic heuristic model based on 2-Poisson indexing theory that scores documents by summing individual term relevance weights with saturation and length penalization. The Language Model approach treats each document as a statistical generative distribution, ranking documents by the joint probability that the document model would generate the exact sequence of query words.

**2. Why is Laplace smoothing necessary in Multinomial Naive Bayes?**  
Without smoothing, if a query contains even a single word that never appeared in class $c$ in the training corpus ($N_{c, t} = 0$), the maximum likelihood probability $P(t \mid c) = 0$. In multiplicative space (or log space where $\ln(0) = -\infty$), this causes the entire class probability to crash to zero regardless of how many other strong indicator terms match. Laplace smoothing ($\alpha = 1.0$) ensures every vocabulary term receives non-zero probability mass.

**3. Why do software defect queries require Query Coordination matching?**  
In technical queries (e.g., `memory leak in connection pool`), individual words like `connection` or `pool` appear in thousands of unrelated issues. A pure unigram sum could rank a short document mentioning `connection` 5 times higher than a document mentioning `memory`, `leak`, and `pool` once each. Coordination matching computes $|Q \cap D| / |Q|$, ensuring that multi-term conceptual matches always outrank single-term high-frequency matches.
