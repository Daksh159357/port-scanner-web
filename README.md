# TCP Port Scanner

A Flask web application for authorized TCP port scanning, with a browser UI, live progress, cancellation, and CSV export.

## Features

- Scan TCP ports 0–65535 on one target
- Browser-based dark UI
- Live progress and open-port results
- Configurable timeout and concurrency
- CSV export
- Native Render deployment configuration (Python + Gunicorn)
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

### Option 1: Render Blueprint (Automatic)
1. In Render Dashboard, click **New +** -> **Blueprint**.
2. Connect your repository `port-scanner-web`.
3. Render will automatically read `render.yaml` and configure everything.
4. Click **Apply**.

### Option 2: Web Service (Manual)
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Connect your repository `port-scanner-web`.
3. Set the following settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120`
4. Under **Environment Variables**:
   - `SCANNER_PASSWORD`: Your login password (fallback: `admin123`).
   - `FLASK_SECRET_KEY`: A long random secret string.
5. Click **Create Web Service**.

## Important limitations

- This performs TCP connect checks, not UDP scans.
- Port 0 is reserved and normally cannot be a listening service.
- Scans run from Render's network, not from your laptop or home LAN.
- Free hosting may sleep while idle and may not be suitable for long scans.
- Only scan targets you own or are explicitly authorized to test.
- Do not remove authentication or expose the scanner without access controls.
