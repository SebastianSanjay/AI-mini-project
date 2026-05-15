# LinguaFuse AI - VS Code Local Setup Guide

This guide provides step-by-step instructions for running both the frontend and backend locally in VS Code.

## 1. Folder Structure in VS Code

Open the root project folder in VS Code. Your workspace should look like this:
```text
project-root/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
└── .vscode/
    ├── settings.json
    └── launch.json
```

## 2. Recommended Extensions

Install these extensions in VS Code for the best experience:
- **Python** (`ms-python.python`)
- **Pylance** (`ms-python.vscode-pylance`)
- **Live Server** (`ritwickdey.liveserver`)
- **Docker** (`ms-azuretools.vscode-docker`)
- *(Optional)* Thunder Client (API testing)
- *(Optional)* SQLTools + SQLTools PostgreSQL driver (Database inspection)

## 3. Backend Setup

1. Open a new terminal in VS Code (`Terminal > New Terminal`).
2. Navigate to the backend folder:
   ```bash
   cd backend
   ```
3. Create and activate a virtual environment:
   ```bash
   # Mac/Linux
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Setup the environment configuration:
   ```bash
   cp .env.example .env
   ```
6. Start the backing services (Redis and PostgreSQL) via Docker:
   ```bash
   docker-compose up redis postgres -d
   ```

### Running the Backend

You can use the built-in VS Code debugger or run commands in the terminal.

**Option A: Using the Terminal**
Terminal 1 (FastAPI):
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Terminal 2 (Celery Worker):
```bash
cd backend
celery -A workers.celery_app worker --loglevel=info
```

**Option B: Using VS Code Run/Debug Panel (F5)**
- Go to the "Run and Debug" tab on the left sidebar.
- Select "Full Backend Stack" from the dropdown and hit the play button.

## 4. Frontend Setup

1. Ensure the **Live Server** extension is installed.
2. In the VS Code file explorer, expand the `frontend/` folder.
3. Right-click on `index.html` and select **"Open with Live Server"**.
4. Your default browser will open to `http://127.0.0.1:5500`.

*Note: The frontend is pre-configured in `frontend/js/config.js` to communicate with the backend at `http://localhost:8000` and `ws://localhost:8000`.*

## 5. Testing the Full Flow

1. **Verify Backend APIs:** Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the FastAPI Swagger documentation.
2. **Launch Application:** Navigate to [http://127.0.0.1:5500/upload.html](http://127.0.0.1:5500/upload.html) (Live Server URL).
3. **Upload & Process:** Select a video, pick a target language, and click "Start Translation".
4. **Monitor Processing:** The browser will redirect to the processing page where you can see live WebSocket logs and progress.
5. **Download:** Once complete, you will be redirected to the Result page to download the final MP4.