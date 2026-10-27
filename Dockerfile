# Use official lightweight Python 3.11 slim image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

WORKDIR /app

# Install minimal build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU wheel first for maximum layer caching
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and curated ML/DL assets
COPY src/ ./src/
COPY data/curated/ ./data/curated/
COPY README.md .

# Create empty directories for runtime data
RUN mkdir -p data/raw data/clean data/gold

# Expose Railway assigned port
EXPOSE 8501

# Run Streamlit bound to 0.0.0.0 and dynamic Railway $PORT
CMD ["sh", "-c", "streamlit run src/app/main.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false"]
