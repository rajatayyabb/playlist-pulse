# YTPULSE

> **A local-first playlist extraction console for creators, archivists, and power users.**

[![Status: local-only](https://img.shields.io/badge/status-local--only-00ff9c?style=for-the-badge)](#privacy)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-web%20app-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-f5c518?style=for-the-badge)](#license)

YTPULSE is a deliberately simple web UI around [`yt-dlp`](https://github.com/yt-dlp/yt-dlp). Paste a YouTube playlist URL, choose an output container, watch the live signal log, and download one numbered ZIP archive when the job is complete.

No accounts. No dashboard. No cloud queue. **Just a small local tool that runs on your machine.**

---

## What it does

```text
playlist URL  →  background download  →  720p merge  →  numbered files  →  ZIP archive
```

- **Playlist-first workflow** — process a full playlist from one URL.
- **720p ceiling** — selects the best available video/audio streams up to 720p.
- **MP4 or MKV** — choose a broadly compatible MP4 or a remux-friendly MKV container.
- **Live progress** — see the active playlist item, percentage, and job log in the browser.
- **Ordered output** — files are named `001 - Title.mp4`, `002 - Title.mp4`, and so on.
- **One-click delivery** — the completed playlist is packed into a single downloadable ZIP.
- **Local by default** — the Flask server and temporary job files stay on your machine.

## Quick start

### 1. Install prerequisites

- Python **3.9 or newer**
- [`ffmpeg`](https://ffmpeg.org/download.html) available on your system `PATH`

### 2. Install YTPULSE

```bash
git clone https://github.com/<your-username>/playlist-pulse.git
cd playlist-pulse
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

### 3. Launch the console

```bash
python app.py
```

Open **http://localhost:5000**, paste a playlist URL, select MP4 or MKV, and initiate the download.

## Configuration at a glance

| Setting | Current behavior |
| --- | --- |
| Video quality | Best available streams up to 720p |
| Fragment concurrency | 8 parallel fragments |
| Output naming | Zero-padded playlist index + title |
| Archive format | ZIP with DEFLATE compression |
| Server port | `5000` |
| Error handling | Failed items are skipped; empty jobs fail clearly |

## Project map

```text
.
├── app.py                 # Flask routes, background jobs, yt-dlp, ZIP creation
├── requirements.txt       # Python dependency pin/range
├── templates/index.html   # YTPULSE interface
└── static/
    ├── script.js          # Start job, poll status, reveal archive download
    └── style.css           # Neon terminal / scanline visual system
```

## API surface

The browser uses four small endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Render the YTPULSE interface |
| `POST` | `/start` | Start a playlist job with `url` and `container` (`mp4` or `mkv`) |
| `GET` | `/status/<job_id>` | Return job state, percentage, and log lines |
| `GET` | `/download/<job_id>` | Download the finished `playlist.zip` |

## Privacy and responsible use

YTPULSE is designed to run locally, but the underlying downloader still connects to YouTube to retrieve the content you request. **Use it only for videos you own, have permission to download, or are otherwise allowed to save.** Respect copyright, platform terms, and applicable law.

Temporary job data is written to the local `jobs/` directory and the completed archive is served back by the local Flask process. Do not expose the development server to the public internet without adding authentication, access controls, and a production deployment configuration.

## Troubleshooting

### `ffmpeg` not found

Install ffmpeg for your operating system and confirm it is discoverable:

```bash
ffmpeg -version
```

### The archive is empty

Check that the URL is a playlist URL, the playlist is accessible, and the requested videos can be downloaded in your region. YTPULSE skips individual download errors but reports an empty result as a failed job.

### Large playlists run slowly

That is expected: downloads use disk space before the final ZIP is assembled. Keep enough free space for the playlist’s extracted files plus the archive.

## Roadmap ideas

- [ ] Add a configurable quality ceiling
- [ ] Add cancel and cleanup controls for active jobs
- [ ] Add a persistent job history view
- [ ] Add optional authentication for LAN deployments
- [ ] Add automated tests around job lifecycle and archive naming

## License

MIT — see [LICENSE](LICENSE) when added to the project.

---

<div align="center">
  <sub>Built for quiet archives, long playlists, and people who prefer a terminal glow.</sub>
</div>
