FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive
ENV WAV2LIP_DIR=/app/Wav2Lip

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    python3-dev \
    git \
    ffmpeg \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Symlink python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Set working directory
WORKDIR /app

# Clone Wav2Lip (We assume the checkpoint will be mounted or downloaded later)
RUN git clone https://github.com/Rudrabha/Wav2Lip.git $WAV2LIP_DIR

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose port
EXPOSE 8000

# Command to run (overridden in docker-compose for celery workers)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
