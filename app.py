import os
import re
import shutil
import threading
import uuid
import zipfile
from urllib.parse import urlparse

import yt_dlp
from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
JOBS_DIR = os.path.join(BASE, "jobs")
PUBLIC_DIR = os.path.join(BASE, "public")
JOB_ID_PATTERN = re.compile(r"^[a-f0-9]{12}$")
ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
MAX_URL_LENGTH = 2048

os.makedirs(JOBS_DIR, exist_ok=True)

jobs = {}
jobs_lock = threading.Lock()


def get_job(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        return dict(job) if job else None


def update_job(job_id, **changes):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(changes)


def append_log(job_id, message):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id]["log"].append(message)
            jobs[job_id]["log"] = jobs[job_id]["log"][-80:]


def is_supported_playlist_url(url):
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    hostname = (parsed.hostname or "").lower().rstrip(".")
    return parsed.scheme in {"http", "https"} and hostname in ALLOWED_HOSTS


def run_job(job_id, url, container):
    job_dir = os.path.join(JOBS_DIR, job_id)
    out_dir = os.path.join(job_dir, "videos")
    os.makedirs(out_dir, exist_ok=True)

    def hook(download):
        if download["status"] == "downloading":
            info = download.get("info_dict", {}) or {}
            index = info.get("playlist_index") or 1
            total = info.get("n_entries")
            percent = download.get("_percent_str", "").strip()
            title = info.get("title", "untitled")
            append_log(job_id, f"[{index}/{total or '?'}] {title} :: {percent}")
            if total:
                update_job(job_id, percent=min(99, int((index - 1) / total * 100)))
        elif download["status"] == "finished":
            append_log(job_id, "segment complete, merging...")

    options = {
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "merge_output_format": container,
        "outtmpl": os.path.join(out_dir, "%(playlist_index)03d - %(title)s.%(ext)s"),
        "concurrent_fragment_downloads": 8,
        "ignoreerrors": True,
        "quiet": True,
        "noprogress": True,
        "progress_hooks": [hook],
    }

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])

        files = sorted(
            filename for filename in os.listdir(out_dir)
            if os.path.isfile(os.path.join(out_dir, filename))
        )
        if not files:
            raise RuntimeError("No videos downloaded. Check the playlist URL and try again.")

        append_log(job_id, "packing archive...")
        zip_path = os.path.join(job_dir, "playlist.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for filename in files:
                archive.write(os.path.join(out_dir, filename), filename)

        shutil.rmtree(out_dir, ignore_errors=True)
        update_job(job_id, percent=100, state="done")
        append_log(job_id, "archive ready.")
    except Exception as error:
        shutil.rmtree(out_dir, ignore_errors=True)
        update_job(job_id, state="error")
        append_log(job_id, f"ERROR: {error}")


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/manus-routes.json")
def route_manifest():
    return send_from_directory(PUBLIC_DIR, "manus-routes.json", mimetype="application/json")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/start")
def start():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    container = data.get("container", "mp4")

    if not isinstance(url, str) or not url.strip():
        return jsonify({"error": "Paste a playlist URL first."}), 400
    url = url.strip()
    if len(url) > MAX_URL_LENGTH or not is_supported_playlist_url(url):
        return jsonify({"error": "Enter a valid YouTube playlist URL."}), 400
    if container not in {"mp4", "mkv"}:
        container = "mp4"

    job_id = uuid.uuid4().hex[:12]
    with jobs_lock:
        jobs[job_id] = {
            "state": "running",
            "percent": 0,
            "log": ["initializing download..."],
        }

    worker = threading.Thread(
        target=run_job,
        args=(job_id, url, container),
        daemon=True,
        name=f"ytpulse-{job_id}",
    )
    worker.start()
    return jsonify({"job_id": job_id})


@app.get("/status/<job_id>")
def status(job_id):
    if not JOB_ID_PATTERN.fullmatch(job_id):
        return jsonify({"state": "error", "percent": 0, "log": ["unknown job id"]}), 404
    job = get_job(job_id)
    if not job:
        return jsonify({"state": "error", "percent": 0, "log": ["unknown job id"]}), 404
    return jsonify(job)


@app.get("/download/<job_id>")
def download(job_id):
    if not JOB_ID_PATTERN.fullmatch(job_id):
        return "not ready", 404
    archive = os.path.join(JOBS_DIR, job_id, "playlist.zip")
    if not os.path.isfile(archive):
        return "not ready", 404
    return send_from_directory(os.path.dirname(archive), "playlist.zip", as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "3000")))
