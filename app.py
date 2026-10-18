import csv
import hmac
import io
import ipaddress
import os
import secrets
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, jsonify, render_template, request, Response, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
SCANNER_PASSWORD = os.environ.get("SCANNER_PASSWORD")

lock = threading.Lock()
state = {
    "running": False, "stop": None, "target": "", "completed": 0,
    "total": 65536, "results": [], "started": 0, "error": None,
}


@app.before_request
def require_login():
    if request.endpoint in {"login", "health", "static"}:
        return None
    if not SCANNER_PASSWORD:
        if request.endpoint == "index":
            return ("Scanner is not configured. Set SCANNER_PASSWORD in the environment.", 503)
        return jsonify(error="Scanner is not configured. Set SCANNER_PASSWORD."), 503
    if not session.get("authenticated"):
        if request.path == "/":
            return redirect(url_for("login"))
        return jsonify(error="Authentication required."), 401


@app.get("/login")
def login():
    if not SCANNER_PASSWORD:
        return "Set SCANNER_PASSWORD in the environment.", 503
    return render_template("login.html")


@app.post("/login")
def login_post():
    password = request.form.get("password", "")
    if SCANNER_PASSWORD and hmac.compare_digest(password, SCANNER_PASSWORD):
        session["authenticated"] = True
        session.permanent = True
        return redirect(url_for("index"))
    return render_template("login.html", error="Incorrect password."), 401


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


def check_port(host, port, timeout, stop):
    if stop.is_set():
        return None
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            if sock.connect_ex((host, port)) == 0:
                return port
    except OSError:
        pass
    return None


def run_scan(host, timeout, workers):
    stop = state["stop"]
    executor = ThreadPoolExecutor(max_workers=workers)
    futures = {}
    try:
        # Keep the number of outstanding futures bounded.
        ports = iter(range(65536))
        pending = set()
        for _ in range(workers * 4):
            try:
                port = next(ports)
            except StopIteration:
                break
            pending.add(executor.submit(check_port, host, port, timeout, stop))

        while pending and not stop.is_set():
            done = set()
            for future in as_completed(pending):
                done.add(future)
                break
            pending.difference_update(done)

            for future in done:
                with lock:
                    state["completed"] += 1
                try:
                    result = future.result()
                except Exception:
                    result = None
                if result is not None:
                    with lock:
                        state["results"].append(result)

                if not stop.is_set():
                    try:
                        port = next(ports)
                    except StopIteration:
                        continue
                    pending.add(executor.submit(check_port, host, port, timeout, stop))

        for future in pending:
            future.cancel()
    except Exception as exc:
        with lock:
            state["error"] = str(exc)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
        with lock:
            state["running"] = False


@app.post("/api/start")
def start():
    data = request.get_json(silent=True) or {}
    target = str(data.get("target", "")).strip()
    if not data.get("authorized"):
        return jsonify(error="Confirm that you are authorized to scan this target."), 400
    if not target or len(target) > 253 or "/" in target:
        return jsonify(error="Enter one IP address or hostname, not a network range."), 400
    try:
        timeout = float(data.get("timeout", 0.3))
        workers = int(data.get("workers", 100))
        if not 0.1 <= timeout <= 3:
            raise ValueError
        if not 10 <= workers <= 300:
            raise ValueError
        host = socket.gethostbyname(target)
        ipaddress.ip_address(host)
    except (ValueError, socket.gaierror):
        return jsonify(error="Invalid target or settings."), 400

    # Do not allow scanning local, private, loopback, link-local, multicast,
    # reserved, or unspecified addresses from a public cloud deployment.
    ip = ipaddress.ip_address(host)
    if not ip.is_global:
        return jsonify(error="Public cloud scanning is restricted to globally routable IP addresses. Local/private targets are not reachable from Render."), 400

    with lock:
        if state["running"]:
            return jsonify(error="A scan is already running."), 409
        state.update({
            "running": True, "stop": threading.Event(), "target": host,
            "completed": 0, "total": 65536, "results": [],
            "started": time.monotonic(), "error": None,
        })

    threading.Thread(target=run_scan, args=(host, timeout, workers), daemon=True).start()
    return jsonify(message="Scan started", target=host)


@app.post("/api/stop")
def stop():
    with lock:
        if state["running"] and state["stop"]:
            state["stop"].set()
    return jsonify(message="Stop requested")


@app.get("/api/status")
def status():
    with lock:
        elapsed = time.monotonic() - state["started"] if state["started"] else 0
        return jsonify({
            "running": state["running"], "target": state["target"],
            "completed": state["completed"], "total": state["total"],
            "open_ports": sorted(state["results"]), "elapsed": round(elapsed, 1),
            "error": state["error"],
        })


@app.get("/api/export")
def export():
    with lock:
        ports = sorted(state["results"])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Port", "State", "TCP Service"])
    for port in ports:
        try:
            service = socket.getservbyport(port, "tcp")
        except OSError:
            service = "Unknown"
        writer.writerow([port, "OPEN", service])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=open_ports.csv"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
