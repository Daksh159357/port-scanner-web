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

Open http://127.0.0.1:5000 and sign in using `SCANNER_PASSWORD`.

## Deploy to Render

1. Push this repository to your GitHub account.
2. In Render, create a Web Service connected to this repository.
3. Render can use the included `render.yaml`.
4. Set `SCANNER_PASSWORD` to a strong, unique password in Render's environment settings.
5. Keep `FLASK_SECRET_KEY` private. Render can generate it from `render.yaml`; otherwise set a long random value yourself.
6. Deploy and open the `.onrender.com` URL.

## Important limitations

- This performs TCP connect checks, not UDP scans.
- Port 0 is reserved and normally cannot be a listening service.
- Scans run from Render's network, not from your laptop or home LAN.
- Free hosting may sleep while idle and may not be suitable for long scans.
- Only scan targets you own or are explicitly authorized to test.
- Do not remove authentication or expose the scanner without access controls.
