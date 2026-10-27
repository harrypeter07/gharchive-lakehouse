# 🚀 Step-by-Step Railway Deployment Guide
**How to put your GH Archive Lakehouse & Deep Learning App on the Internet**
**Student**: Hassan | **Platform**: [Railway.com](https://railway.com) (Free / Hobby Tier)

---

## What is Railway?
Railway is a cloud platform that runs your code in the cloud 24/7 so anyone can open your website on their phone or laptop without you having to keep your computer turned on.

---

## Prerequisite: Push Your Code to GitHub

Make sure your latest code is pushed to your GitHub repository:
```bash
git add .
git commit -m "feat: add PyTorch 1D-CNN, Railway Dockerfile, and DL documentation"
git push origin main
```

---

## 3 Easy Steps to Deploy on Railway

### Step 1: Sign in to Railway
1. Go to **[https://railway.com](https://railway.com)**.
2. Click **"Login"** (top right) and choose **"Login with GitHub"**.

---

### Step 2: Deploy Your Repository
1. On your Railway dashboard, click the purple button **"+ New Project"**.
2. Select **"Deploy from GitHub repo"**.
3. Pick your repository: `gharchive-lakehouse` (or whatever your repo name is).
4. Railway will automatically detect the `Dockerfile` we just created!
5. Click **"Deploy Now"**.

---

### Step 3: Generate Your Public Website Link
1. In Railway, click on your newly deployed service tile.
2. Go to the **"Settings"** tab.
3. Scroll down to the **"Networking"** section.
4. Click **"Generate Domain"**.
5. Railway will give you a live public link, like:
   `https://gharchive-lakehouse-production.up.railway.app`
6. Click the link — your Streamlit Lakehouse & Deep Learning Command Center is now live on the internet! 🎉

---

## What Happens Under the Hood?
- Railway reads our `Dockerfile`.
- It installs Python 3.11, PyTorch CPU, DuckDB, and Streamlit.
- It loads our pre-trained model weights (`data/curated/cnn_weights.pt`), vocabulary, and star schema.
- It binds to Railway's dynamic `$PORT` and serves the app.
