import os
import shutil
import threading
import uuid
import zipfile
from flask import Flask, request, jsonify, send_from_directory, render_template
import yt_dlp

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
JOBS_DIR = os.path.join(BASE, "jobs")
os.makedirs(JOBS_DIR, exist_ok=True)

jobs = {}


def run_job(job_id, url, container):
    job = jobs[job_id]
    out_dir = os.path.join(JOBS_DIR, job_id, "videos")
    os.makedirs(out_dir, exist_ok=True)

    def hook(d):
        if d["status"] == "downloading":
            info = d.get("info_dict", {}) or {}
            idx = info.get("playlist_index")
            total = info.get("n_entries")
            pct = d.get("_percent_str", "").strip()
            title = info.get("title", "")
            job["log"] = (job["log"][-1:] if job["log"] else []) + [f"[{idx}/{total}] {title} :: {pct}"]
            if total:
                job["percent"] = min(99, int(((idx or 1) - 1) / total * 100))
        elif d["status"] == "finished":
            job["log"].append("segment complete, merging...")

    ydl_opts = {
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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.listdir(out_dir):
            raise RuntimeError("No videos downloaded — check the playlist URL and try again.")

        job["log"].append("packing archive...")
        zip_path = os.path.join(JOBS_DIR, job_id, "playlist.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in os.listdir(out_dir):
                zf.write(os.path.join(out_dir, f), f)
        shutil.rmtree(out_dir)

        job["percent"] = 100
        job["state"] = "done"
        job["log"].append("archive ready.")
    except Exception as e:
        job["state"] = "error"
        job["log"].append(f"ERROR: {e}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    container = data.get("container") or "mp4"
    if container not in ("mp4", "mkv"):
        container = "mp4"
    if not url:
        return jsonify({"error": "no url provided"}), 400

    job_id = uuid.uuid4().hex[:10]
    jobs[job_id] = {"state": "running", "percent": 0, "log": ["initializing download..."]}
    threading.Thread(target=run_job, args=(job_id, url, container), daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"state": "error", "percent": 0, "log": ["unknown job id"]})
    return jsonify(job)


@app.route("/download/<job_id>")
def download(job_id):
    path = os.path.join(JOBS_DIR, job_id)
    if not os.path.exists(os.path.join(path, "playlist.zip")):
        return "not ready", 404
    return send_from_directory(path, "playlist.zip", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=False, port=5000)
