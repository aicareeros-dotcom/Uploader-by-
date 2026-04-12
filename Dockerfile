# Use Python 3.12 (non-alpine for better compatibility)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    wget \
    unzip \
    gcc \
    g++ \
    make \
    cmake \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Bento4 (mp4decrypt)
RUN wget -q https://github.com/axiomatic-systems/Bento4/archive/v1.6.0-639.zip \
    && unzip v1.6.0-639.zip \
    && cd Bento4-1.6.0-639 \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && cp mp4decrypt /usr/local/bin/ \
    && cd ../.. \
    && rm -rf Bento4-1.6.0-639 v1.6.0-639.zip

# Copy project files
COPY . .

# Install Python dependencies (IMPORTANT FIX)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir setuptools wheel \
    && pip install --no-cache-dir -r sainibots.txt \
    && pip install --no-cache-dir gunicorn yt-dlp

# Expose port
EXPOSE 10000

# Start both Web + Bot
CMD sh -c "gunicorn app:app --bind 0.0.0.0:$PORT & python3 modules/main.py"
