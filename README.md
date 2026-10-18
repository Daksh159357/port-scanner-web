# TCP Port Scanner

A Flask web application for authorized TCP port scanning, with a browser UI, live progress, cancellation, and CSV export.

## Features

- Scan TCP ports 0–65535 on one target
- Browser-based dark UI
- Live progress and open-port results
- Configurable timeout and concurrency
- CSV export
- Render deployment configuration
- Password-protected UI and API

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SCANNER_PASSWORD='choose-a-long-password'
export FLASK_SECRET_KEY='replace-with-a-long-random-secret'
python app.py
```

Open http://127.0.0.1:5000 and sign in using `SCANNER_PASSWORD` (default fallback password is `admin123`).

## Deploy to Render

### Option A: Using Render Blueprint (Automatic)
1. In Render, click **New +** -> **Blueprint**.
2. Select this repository. Render will automatically read `render.yaml`.
3. Click **Apply**.

### Option B: Web Service (Python or Docker)
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Select your repository `port-scanner-web`.
3. Choose either **Python** or **Docker**:
   - **If choosing Python**:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120`
   - **If choosing Docker**:
     - Render automatically detects the included `Dockerfile` and builds it.
4. Environment Variables:
   - `SCANNER_PASSWORD`: Choose your login password (default fallback: `admin123`).
   - `FLASK_SECRET_KEY`: Long random string for session encryption.
5. Deploy and open your `.onrender.com` link.

## Important limitations

- This performs TCP connect checks, not UDP scans.
- Port 0 is reserved and normally cannot be a listening service.
- Scans run from Render's network, not from your laptop or home LAN.
- Free hosting may sleep while idle and may not be suitable for long scans.
- Only scan targets you own or are explicitly authorized to test.
- Do not remove authentication or expose the scanner without access controls.
