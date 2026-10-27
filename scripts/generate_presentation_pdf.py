"""Script to generate a presentation-ready Slide Deck & Lab Defense Guide PDF."""

from pathlib import Path
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = PROJECT_ROOT / "docs" / "DL_PRESENTATION_SLIDES.html"
PDF_PATH = PROJECT_ROOT / "docs" / "DL_PRESENTATION_SLIDES.pdf"
DOWNLOADS_PATH = Path("C:/Users/ASUS/Downloads/DL_PRESENTATION_SLIDES_AND_GUIDE.pdf")

PRESENTATION_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Deep Learning Lab Presentation: GitHub Issue Classifier</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap');

  @page {
    size: A4 landscape;
    margin: 10mm 12mm 10mm 12mm;
    @bottom-right {
      content: "Slide " counter(page);
      font-family: 'Inter', sans-serif;
      font-size: 8pt;
      color: #64748b;
    }
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0f172a;
    line-height: 1.4;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background: #ffffff;
  }

  .slide {
    page-break-after: always;
    height: 180mm;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 12px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 20px;
    background: #ffffff;
  }

  .slide:last-child {
    page-break-after: avoid;
  }

  .slide-header {
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }

  .slide-num {
    font-size: 9pt;
    font-weight: 700;
    color: #0284c7;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .slide-title {
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
  }

  .slide-subtitle {
    font-size: 9.5pt;
    color: #475569;
    margin: 2px 0 0 0;
  }

  .content-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 16px;
    flex: 1;
  }

  .card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 9pt;
  }

  .card-navy {
    background: #0b1222;
    color: #e8f0ff;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 9pt;
  }

  .card-navy strong {
    color: #46c6ef;
  }

  .speech-box {
    background: #eff6ff;
    border-left: 4px solid #2563eb;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    margin-top: 8px;
    font-size: 8.5pt;
  }

  .speech-box strong {
    color: #1d4ed8;
  }

  .tech-box {
    background: #fdf4ff;
    border-left: 4px solid #c026d3;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    margin-top: 8px;
    font-size: 8.5pt;
  }

  .tech-box strong {
    color: #9333ea;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0;
    font-size: 8pt;
  }

  th, td {
    border: 1px solid #cbd5e1;
    padding: 4px 8px;
    text-align: left;
  }

  th {
    background: #e2e8f0;
    font-weight: 700;
    color: #1e293b;
  }

  .badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
  }
  .b-bug { background-color: #fee2e2; color: #dc2626; }
  .b-enh { background-color: #dcfce7; color: #16a34a; }
  .b-doc { background-color: #e0f2fe; color: #0284c7; }
  .b-que { background-color: #fef3c7; color: #d97706; }

  ul {
    margin: 4px 0;
    padding-left: 18px;
  }

  li {
    margin-bottom: 4px;
  }

  .footer-bar {
    border-top: 1px solid #e2e8f0;
    padding-top: 4px;
    display: flex;
    justify-content: space-between;
    font-size: 7.5pt;
    color: #64748b;
  }
</style>
</head>
<body>

<!-- SLIDE 1: TITLE SLIDE -->
<div class="slide">
  <div>
    <div class="slide-num">Slide 1 of 8 · Introduction</div>
    <div style="background: linear-gradient(135deg, #0b1222 0%, #1e3a8a 100%); color: white; padding: 24px 28px; border-radius: 8px; margin-top: 10px;">
      <div style="color: #46c6ef; font-weight: 700; font-size: 11pt; letter-spacing: 1px;">DEEP LEARNING LAB PRESENTATION</div>
      <h1 style="font-size: 24pt; margin: 8px 0; color: #ffffff;">Automated Issue Classification Engine</h1>
      <p style="font-size: 12pt; color: #cbd5e1; margin: 0 0 16px 0;">Solving Real-World GitHub Triage with 1D-Convolutional Neural Networks</p>
      
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 12px; font-size: 8.5pt;">
        <div><b>Student:</b> Hassan</div>
        <div><b>College:</b> RCOEM, Nagpur (CSE)</div>
        <div><b>Framework:</b> PyTorch 2.14 & Streamlit</div>
        <div><b>Live App:</b> gharchive.up.railway.app</div>
      </div>
    </div>
  </div>

  <div class="content-grid" style="margin-top: 12px;">
    <div class="speech-box">
      <strong>🗣️ What to Say (Child-Like Pitch):</strong><br>
      "Good morning professors! Today I am presenting our Deep Learning project: an automated system that reads technical GitHub issue reports and sorts them into Bugs, Enhancements, Documentation, or Questions in under 2 milliseconds using a real PyTorch neural network."
    </div>
    <div class="tech-box">
      <strong>⚙️ Technical Foundation:</strong><br>
      "Trained on 11,823 deduplicated GitHub issues from the GH Archive Lakehouse, optimizing 1,297,412 parameters with Adam and Dropout regularization."
    </div>
  </div>

  <div class="footer-bar">
    <span>Shri Ramdeobaba College of Engineering and Management (CSE Dept)</span>
    <span>Live Deployment: https://gharchive.up.railway.app</span>
  </div>
</div>

<!-- SLIDE 2: THE PROBLEM & ANALOGY -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-num">Slide 2 of 8 · Problem Statement</div>
      <div class="slide-title">The Challenge: Millions of Unsorted Tickets</div>
      <div class="slide-subtitle">Why automated triage is necessary in modern open-source software engineering</div>
    </div>
  </div>

  <div class="content-grid">
    <div class="card">
      <h3 style="margin-top: 0; color: #0284c7;">The Real-World Bottleneck</h3>
      <ul>
        <li>GitHub repositories receive <b>millions of issue tickets</b> every single day.</li>
        <li>Human maintainers waste hours reading titles to label them manually.</li>
        <li>Triage delay slows down critical bug fixes and patch releases.</li>
      </ul>

      <div class="speech-box" style="margin-top: 12px;">
        <strong>👶 The Mailroom Analogy (Explain like a 10-year-old):</strong><br>
        "Imagine working in a busy post office where thousands of letters arrive every hour. If one person has to open and read every letter, the mail piles up. Our neural network acts like a smart sorting machine that scans the letter's headline and immediately drops it into the right basket!"
      </div>
    </div>

    <div class="card">
      <h3 style="margin-top: 0; color: #0f172a;">Target Categories (4 Classes)</h3>
      <table style="margin-top: 6px;">
        <tr><th>Class</th><th>Description</th><th>Example Trigger Words</th></tr>
        <tr><td><span class="badge b-bug">Bug</span></td><td>Code defect or crash</td><td><i>segfault, null pointer, panic, fail</i></td></tr>
        <tr><td><span class="badge b-enh">Enhancement</span></td><td>New feature request</td><td><i>add, support, implement, export</i></td></tr>
        <tr><td><span class="badge b-doc">Documentation</span></td><td>Guides & README typos</td><td><i>typo, readme, tutorial, setup guide</i></td></tr>
        <tr><td><span class="badge b-que">Question</span></td><td>Usage inquiries</td><td><i>how to configure, where is, how can I</i></td></tr>
      </table>

      <div class="tech-box">
        <strong>⚙️ Objective:</strong> Multi-class text classification maximizing Macro-F1 across severe real-world class imbalances.
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>GH Archive Lakehouse & Neural Analytics</span>
    <span>Slide 2</span>
  </div>
</div>

<!-- SLIDE 3: GENUINE ML PROOF -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-num">Slide 3 of 8 · Verification</div>
      <div class="slide-title">Academic Integrity: 100% Real Neural Network</div>
      <div class="slide-subtitle">Demonstrating true learned weights vs. fake heuristic rules</div>
    </div>
  </div>

  <div class="content-grid">
    <div class="card">
      <h3 style="margin-top: 0; color: #0284c7;">Fake Function vs. Our PyTorch Model</h3>
      <table>
        <tr><th>Aspect</th><th>Fake Rule-Based Function</th><th>Our Real Model (`IssueCNN`)</th></tr>
        <tr><td><b>Decision Rule</b></td><td>`if "crash" in text: return bug`</td><td>Matrix multiplications across 1.29M weights</td></tr>
        <tr><td><b>Learned Weights</b></td><td>0 bytes (None)</td><td><b>5.19 MB</b> serialized (`cnn_weights.pt`)</td></tr>
        <tr><td><b>Vocabulary</b></td><td>None</td><td><b>20,075 tokens</b> (`vocab.json`)</td></tr>
        <tr><td><b>Training Evidence</b></td><td>None (manual text)</td><td>8 epochs with <b>Adam optimizer</b> & logged loss</td></tr>
      </table>

      <div class="speech-box">
        <strong>🗣️ What to Say to the Professor:</strong><br>
        "Sir, we did not write 'if-else' statements. We trained a genuine PyTorch 1D-CNN with 1,297,412 parameters. The model weights are serialized on disk in `cnn_weights.pt` and loaded into CPU memory for sub-2ms inference."
      </div>
    </div>

    <div class="card-navy">
      <h3 style="margin-top: 0; color: #46c6ef;">Strict Split Isolation (Zero Data Leakage)</h3>
      <p>A rigorous audit found 551 duplicate issue records in the raw GH Archive stream. We eliminated all duplicates:</p>
      <ul>
        <li><b>Total Unique Issues:</b> 14,780</li>
        <li><b>Training Set (80%):</b> 11,823 samples</li>
        <li><b>Validation Set (10%):</b> 1,478 samples</li>
        <li><b>Test Set (10%):</b> 1,479 samples</li>
      </ul>
      <p style="color: #94a3b8; font-size: 8pt;"><b>Zero overlap:</b> No issue ID or 50-token sequence exists in more than one partition.</p>
    </div>
  </div>

  <div class="footer-bar">
    <span>Verified Dataset: 14,780 records · 20,075 vocabulary tokens</span>
    <span>Slide 3</span>
  </div>
</div>

<!-- SLIDE 4: THE 4 LAB PRACTICALS -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-num">Slide 4 of 8 · Syllabus Mapping</div>
      <div class="slide-title">Direct Alignment with College Lab Practicals</div>
      <div class="slide-subtitle">How our real GitHub classifier implements each core deep learning practical</div>
    </div>
  </div>

  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; flex: 1;">
    <div class="card">
      <h4 style="margin: 0 0 4px 0; color: #0284c7;">Practical 6: CNN</h4>
      <p style="font-size: 8pt; color: #64748b;">Convolution & Pooling</p>
      <div style="font-size: 8pt;">
        <b>In our model:</b> 64 filters (`nn.Conv1d`, kernel 3) slide across 3-word windows. <b>Global Max-Pooling</b> grabs the loudest clue from the entire sentence.
      </div>
      <div class="speech-box" style="font-size: 7.5pt; margin-top: 6px;">
        "Like 64 magnifying glasses scanning 3 words at a time."
      </div>
    </div>

    <div class="card">
      <h4 style="margin: 0 0 4px 0; color: #0284c7;">Practical 5: Regularizers</h4>
      <p style="font-size: 8pt; color: #64748b;">Preventing Overfitting</p>
      <div style="font-size: 8pt;">
        <b>In our model:</b> `nn.Dropout(p=0.2)` randomly sets 20% of activations to 0 during training, forcing redundant, robust feature learning.
      </div>
      <div class="speech-box" style="font-size: 7.5pt; margin-top: 6px;">
        "Like blindfolding 20% of the player's eyes so they don't memorize one trick."
      </div>
    </div>

    <div class="card">
      <h4 style="margin: 0 0 4px 0; color: #0284c7;">Practical 4: Optimizers</h4>
      <p style="font-size: 8pt; color: #64748b;">Adam & Mini-Batches</p>
      <div style="font-size: 8pt;">
        <b>In our model:</b> `torch.optim.Adam` (lr=0.001) computes adaptive learning rates per parameter on mini-batches of 64 issues.
      </div>
      <div class="speech-box" style="font-size: 7.5pt; margin-top: 6px;">
        "A smart mountain bike with gears that speeds up on flats and slows on rocky turns."
      </div>
    </div>

    <div class="card">
      <h4 style="margin: 0 0 4px 0; color: #0284c7;">Practical 3: Feedforward</h4>
      <p style="font-size: 8pt; color: #64748b;">Dense Head & Softmax</p>
      <div style="font-size: 8pt;">
        <b>In our model:</b> `nn.Linear(64, 4)` projects features to 4 logits. `torch.softmax` outputs calibrated percentages summing to 1.00.
      </div>
      <div class="speech-box" style="font-size: 7.5pt; margin-top: 6px;">
        "4 judges voting with percentages that always add up to 100%."
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Demonstrates CNN, Regularization, Optimization, and Feedforward Networks</span>
    <span>Slide 4</span>
  </div>
</div>

<!-- SLIDE 5: NEURAL EXECUTION TRACE -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-num">Slide 5 of 8 · Execution Flow</div>
      <div class="slide-title">How Words Become Decisions (Live Execution Trace)</div>
      <div class="slide-subtitle">Step-by-step tensor transformations inside the PyTorch forward pass</div>
    </div>
  </div>

  <div class="content-grid">
    <div class="card">
      <h3 style="margin-top: 0; color: #0284c7;">Tensor Lifecycle Inside `IssueCNN`</h3>
      <ol style="margin: 4px 0; padding-left: 18px; font-size: 8.5pt;">
        <li><b>Input Text:</b> <i>"Fatal segmentation fault in memory allocator"</i></li>
        <li><b>Tokenizer:</b> Text mapped to 50 token IDs `[108, 412, 92, ...]` (padding with 0).</li>
        <li><b>Embedding:</b> `[1, 50]` &rarr; `[1, 50, 64]` (64-dim coordinate per word).</li>
        <li><b>Conv1D + ReLU:</b> `[1, 64, 50]` (64 filters sliding over 3-word windows).</li>
        <li><b>Global Max Pooling:</b> `[1, 64]` (one strongest feature per filter).</li>
        <li><b>Dropout (p=0.2):</b> `[1, 64]` (regularization during training).</li>
        <li><b>Linear Layer (FC):</b> `[1, 4]` (raw logits for 4 classes).</li>
        <li><b>Softmax:</b> Probability distribution across Bug, Feature, Docs, Question.</li>
      </ol>
    </div>

    <div class="card-navy">
      <h3 style="margin-top: 0; color: #46c6ef;">Live Output Verification</h3>
      <div style="background: #142139; padding: 10px; border-radius: 4px; font-family: 'Fira Code', monospace; font-size: 8pt; margin-top: 8px;">
        Input Shape: [1, 50]<br>
        Embedding:  [1, 50, 64]<br>
        Conv1D:     [1, 64, 50]<br>
        Max-Pool:   [1, 64]<br>
        Logits:     [2.84, -0.61, -1.24, -2.15]<br>
        <hr style="border: 0.5px solid #334155;">
        <b>Predicted Label: BUG (94.2% Confidence)</b><br>
        Latency: 1.8 ms on CPU
      </div>
      <div class="speech-box" style="color: #0f172a; margin-top: 10px;">
        <strong>🗣️ What to Say:</strong><br>
        "This execution trace is captured live in our Streamlit dashboard on every single click, proving the forward pass executes in real-time."
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>PyTorch Forward Hook Diagnostic Trace</span>
    <span>Slide 5</span>
  </div>
</div>

<!-- SLIDE 6: MEASURED BENCHMARKS -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-num">Slide 6 of 8 · Empirical Results</div>
      <div class="slide-title">Experimental Benchmarks: Real Measured Scores</div>
      <div class="slide-subtitle">Held-out evaluation across 1,479 test issues (stored in dl_report.json)</div>
    </div>
  </div>

  <div class="content-grid">
    <div class="card">
      <h3 style="margin-top: 0; color: #0284c7;">Overall Performance Comparison</h3>
      <table>
        <tr><th>Model</th><th>Test Accuracy</th><th>Macro-F1</th><th>Inference Time</th></tr>
        <tr><td>Majority Class Baseline</td><td>44.69%</td><td>15.44%</td><td>0 ms</td></tr>
        <tr><td>Multinomial Naive Bayes</td><td>74.65%</td><td>50.85%</td><td>&lt; 0.5 ms</td></tr>
        <tr><td><b>1D-CNN (PyTorch)</b></td><td><b>77.15%</b></td><td><b>62.34%</b></td><td><b>1.8 ms</b></td></tr>
      </table>

      <div class="speech-box" style="margin-top: 10px;">
        <strong>🗣️ What to Say:</strong><br>
        "Our PyTorch 1D-CNN beats Naive Bayes by +2.5% in accuracy and by a massive <b>+11.5% in Macro-F1</b>. Macro-F1 is the crucial metric because it weights all classes equally, proving the CNN captures rare categories far better than bag-of-words counting."
      </div>
    </div>

    <div class="card">
      <h3 style="margin-top: 0; color: #0f172a;">Per-Class Performance (Honest Breakdown)</h3>
      <table>
        <tr><th>Class</th><th>Test Count</th><th>Precision</th><th>Recall</th><th>F1-Score</th></tr>
        <tr><td><span class="badge b-bug">Bug</span></td><td>661</td><td>79.4%</td><td>82.6%</td><td><b>80.95%</b></td></tr>
        <tr><td><span class="badge b-enh">Enhancement</span></td><td>626</td><td>76.3%</td><td>80.4%</td><td><b>78.29%</b></td></tr>
        <tr><td><span class="badge b-doc">Documentation</span></td><td>144</td><td>70.6%</td><td>58.3%</td><td><b>63.88%</b></td></tr>
        <tr><td><span class="badge b-que">Question</span></td><td>48</td><td>61.5%</td><td>16.7%</td><td><b>26.23%</b></td></tr>
      </table>

      <div class="tech-box" style="margin-top: 6px;">
        <strong>💡 Honest Limitation:</strong> Questions are naturally rare in open source (only 48 test samples). While Naive Bayes scored 0% on Questions, the CNN correctly found 8, demonstrating superior semantic generalization.
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <span>Empirical Evidence: data/curated/dl_report.json</span>
    <span>Slide 6</span>
  </div>
</div>

<!-- SLIDE 7: LIVE APP & CLOUD ARCHITECTURE -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-num">Slide 7 of 8 · Deployment</div>
      <div class="slide-title">Interactive Dashboard & Cloud Hosting</div>
      <div class="slide-subtitle">Live Streamlit Command Center running inside Docker on Railway</div>
    </div>
  </div>

  <div class="content-grid">
    <div class="card">
      <h3 style="margin-top: 0; color: #0284c7;">Production Architecture</h3>
      <ul>
        <li><b>Frontend:</b> Streamlit 1.66 with modular tabs (`src/app/tabs/`) and dark navy theme.</li>
        <li><b>Containerization:</b> Multi-stage `Dockerfile` (Python 3.11-slim, CPU PyTorch wheels).</li>
        <li><b>Cloud Host:</b> Hosted live on Railway with dynamic `$PORT` binding and healthchecks.</li>
        <li><b>Artifact Size:</b> Lightweight 5.19 MB model weights ensure zero-cost hobby cloud hosting.</li>
      </ul>

      <div class="speech-box">
        <strong>🌐 Live URL:</strong> https://gharchive.up.railway.app<br>
        Accessible from any mobile phone, laptop, or classroom projector!
      </div>
    </div>

    <div class="card-navy">
      <h3 style="margin-top: 0; color: #46c6ef;">Dashboard Capabilities</h3>
      <ul>
        <li><b>⚡ Instant Quick Presets:</b> 4 one-click buttons to test real Bug, Feature, Docs, and Question issues.</li>
        <li><b>📊 Side-by-Side Comparison:</b> Horizontal bar charts comparing CNN probabilities vs. Naive Bayes in real time.</li>
        <li><b>🔬 Neural Diagnostic Inspector:</b> Explores token IDs, known vs. unknown words, and tensor shapes.</li>
        <li><b>📖 Embedded Lab Guide:</b> Full syllabus alignment guide rendered directly in the app.</li>
      </ul>
    </div>
  </div>

  <div class="footer-bar">
    <span>Dockerized · Cloud Hosted on Railway</span>
    <span>Slide 7</span>
  </div>
</div>

<!-- SLIDE 8: VIVA CHEAT SHEET -->
<div class="slide">
  <div class="slide-header">
    <div>
      <div class="slide-num">Slide 8 of 8 · Defense Guide</div>
      <div class="slide-title">Viva Voce Examination Defense Guide</div>
      <div class="slide-subtitle">Direct, confident answers to common evaluator and faculty questions</div>
    </div>
  </div>

  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; flex: 1;">
    <div class="card">
      <p style="margin: 0; font-weight: 700; color: #0284c7;">Q1: Why use 1D-CNN instead of an LSTM, RNN, or Transformer?</p>
      <p style="font-size: 8pt; margin: 4px 0;"><b>Answer:</b> 1D-CNNs compute all sliding windows in parallel ($O(1)$ parallel time) rather than sequentially ($O(N)$ for LSTMs). For short issue text, local 3-word n-grams provide sufficient classification signal with 1.8 ms CPU latency, avoiding the heavy GPU and memory cost of Transformers.</p>

      <p style="margin: 8px 0 0 0; font-weight: 700; color: #0284c7;">Q2: What is the purpose of Dropout in your model?</p>
      <p style="font-size: 8pt; margin: 4px 0;"><b>Answer:</b> `nn.Dropout(0.2)` randomly sets 20% of neuron outputs to zero during each training step. This prevents co-adaptations between neurons, forcing the network to learn robust, generalized features rather than memorizing training sentences.</p>
    </div>

    <div class="card">
      <p style="margin: 0; font-weight: 700; color: #0284c7;">Q3: Why is Macro-F1 more rigorous than overall Accuracy?</p>
      <p style="font-size: 8pt; margin: 4px 0;"><b>Answer:</b> Our dataset has class imbalance (661 bugs vs. 48 questions). Accuracy gives equal weight to every sample, so predicting only majority classes looks deceptively good. Macro-F1 averages the F1 scores across all 4 classes equally, exposing performance on rare classes.</p>

      <p style="margin: 8px 0 0 0; font-weight: 700; color: #0284c7;">Q4: How does your Embedding layer handle Out-Of-Vocabulary (OOV) words?</p>
      <p style="font-size: 8pt; margin: 4px 0;"><b>Answer:</b> Words with frequency &lt; 2 or unseen during training map to index 1 (`<unk>`). Index 0 is reserved for `<pad>` with `padding_idx=0`, ensuring padding tokens receive zero gradients and do not bias the weights.</p>
    </div>
  </div>

  <div class="footer-bar">
    <span>Candidate: Hassan · Department of Computer Science & Engineering</span>
    <span>Slide 8</span>
  </div>
</div>

</body>
</html>
"""

def generate_presentation_pdf():
    print(f"Writing presentation HTML to {HTML_PATH}...")
    HTML_PATH.write_text(PRESENTATION_HTML, encoding="utf-8")
    
    edge_paths = [
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    ]
    edge_exe = None
    for p in edge_paths:
        if p.exists():
            edge_exe = p
            break
            
    if not edge_exe:
        print("ERROR: Microsoft Edge executable not found.")
        return False

    print(f"Rendering PDF with Edge at {edge_exe}...")
    cmd = [
        str(edge_exe),
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={PDF_PATH}",
        f"file:///{HTML_PATH.resolve().as_posix()}",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Edge conversion failed: {res.stderr}")
        return False
        
    print(f"Presentation PDF generated successfully at {PDF_PATH} ({PDF_PATH.stat().st_size} bytes).")
    
    if DOWNLOADS_PATH.parent.exists():
        shutil.copy2(PDF_PATH, DOWNLOADS_PATH)
        print(f"Copied Presentation PDF directly to Downloads folder: {DOWNLOADS_PATH} ({DOWNLOADS_PATH.stat().st_size} bytes).")
        
    return True

if __name__ == "__main__":
    generate_presentation_pdf()
