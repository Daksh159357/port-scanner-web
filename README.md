# TCP Port Scanner

A Flask web application for authorized TCP port scanning, with a browser UI, live progress, cancellation, and CSV export.

## Features

- Scan TCP ports 0–65535 on one target
- Browser-based dark UI
- Live progress and open-port results
- Configurable timeout and concurrency
- CSV export
- Native Render deployment configuration (Python + Gunicorn)
- Direct access (no login or password required)

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:10000 to access the scanner.

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
4. Click **Create Web Service**.

## Important limitations

- This performs TCP connect checks, not UDP scans.
- Port 0 is reserved and normally cannot be a listening service.
- Scans run from Render's network, not from your laptop or home LAN.
- Free hosting may sleep while idle and may not be suitable for long scans.
- Only scan targets you own or are explicitly authorized to test.
