# LinguaFuse AI Backend

Production-ready Python backend for AI-powered multilingual video translation.

## Prerequisites

1. **Docker & Docker Compose**: Ensure Docker is installed on your machine.
2. **NVIDIA Container Toolkit**: Since this application heavily utilizes PyTorch, Whisper, SeamlessM4T, Coqui TTS, and Wav2Lip, you **must** have an NVIDIA GPU and the NVIDIA Container Toolkit installed to allow the Docker containers to access your GPU.

   *Installation instructions for NVIDIA Container Toolkit:*
   [NVIDIA Docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Setup Instructions

1. **Clone the repository**
2. **Environment Variables**:
   Copy the example environment file and fill in any required API keys (if using external providers like ElevenLabs or Google Translate).
   ```bash
   cd backend
   cp .env.example .env
   ```

3. **Models Checkpoints**:
   The Wav2Lip model requires a pre-trained checkpoint. You must download `wav2lip_gan.pth` and place it in the `backend/models/checkpoints/` directory.
   ```bash
   mkdir -p models/checkpoints
   # Download wav2lip_gan.pth here (e.g. from official Wav2Lip repository links)
   ```

## Deployment

To deploy the entire stack (FastAPI, PostgreSQL, Redis, Celery Worker, Nginx):

```bash
docker-compose up -d --build
```

### Services Started:
- **FastAPI API**: Port 8000 (Internal) / Port 80 via Nginx
- **Celery Worker**: Background task processing (GPU accelerated)
- **PostgreSQL**: Port 5432
- **Redis**: Port 6379 (Broker & Pub/Sub for WebSockets)
- **Nginx**: Reverse Proxy handling large file uploads and WebSocket connections

## API Usage

1. **Upload Video**:
   `POST /upload-video` (multipart/form-data)
   - `file`: The video file
   - `target_language`: e.g., "Hindi"
   - `source_language`: (Optional) e.g., "English"

2. **Start Translation**:
   `POST /translate-video/{job_id}`

3. **Track Status**:
   `GET /processing-status/{job_id}`
   *or connect via WebSocket:*
   `ws://localhost/progress/{job_id}`

4. **Download**:
   `GET /download/{job_id}`
