# YTPULSE

> A local-first web interface for downloading permitted YouTube playlists as numbered MP4 or MKV files packed into one ZIP archive.

[![Python](https://img.shields.io/badge/python-3.9%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-web%20application-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-ff0033?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)
[![License: MIT](https://img.shields.io/badge/license-MIT-f5c518?style=for-the-badge)](LICENSE)

YTPULSE wraps [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) in a simple neon terminal-style Flask interface. Users paste a playlist URL, choose an output format, monitor progress in the browser, and download a single ZIP archive when processing is complete.

## Choose how you want to use it

| Option | Best for | What you need |
| --- | --- | --- |
| **Hosted website** | Everyday users | A browser and the hosted YTPULSE link |
| **VS Code / local installation** | Developers and private local use | Git, Python, FFmpeg, and this repository |

GitHub stores the source code. It does not run the Flask application by itself. A hosted deployment is required for a browser-only experience; otherwise, clone the repository and run it locally.

## Features

- Download a complete playlist through a browser interface
- Select MP4 or MKV output
- Choose the best available streams up to 720p
- Fetch fragments concurrently for better throughput
- Show live playlist progress and download logs
- Preserve playlist order with names such as `001 - Video title.mp4`
- Package completed videos into one ZIP archive
- Run locally without sending job data to a third-party application server

## Requirements

Install these tools before starting a local copy:

- **Python 3.9 or newer**
- **Git**
- **FFmpeg** available on your system `PATH`
- **Visual Studio Code** — optional, but recommended for editing and running the project

### Install FFmpeg

Verify an existing installation first:

```bash
ffmpeg -version
```

If that command is not found, install FFmpeg using the instructions for your operating system:

- **Windows:** install it from the [official FFmpeg download page](https://ffmpeg.org/download.html), then add its `bin` directory to `PATH`.
- **macOS with Homebrew:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`

## Install and run with VS Code

### 1. Clone the repository

Open a terminal and run:

```bash
git clone https://github.com/rajatayyabb/playlist-pulse.git
cd playlist-pulse
code .
```

If the `code` command is unavailable, open VS Code manually and choose **File → Open Folder**, then select the cloned `playlist-pulse` folder.

### 2. Create a virtual environment

A virtual environment keeps YTPULSE's Python packages separate from your other projects.

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

When activated, your terminal usually displays `(.venv)` at the beginning of the prompt.

### 3. Install Python dependencies

Run this from the project root:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start YTPULSE

```bash
python app.py
```

The application starts on port `5000`. Open this address in your browser:

```text
http://localhost:5000
```

Keep the terminal window open while using the application. Press `Ctrl+C` in that terminal to stop the server.

## Use the application

1. Copy a YouTube playlist URL that you are permitted to download.
2. Paste it into the **TARGET INPUT** field.
3. Select **MP4** for broad compatibility or **MKV** for a remux-friendly container.
4. Click **INITIATE DOWNLOAD**.
5. Watch the live progress log while the playlist is processed.
6. When the progress reaches 100%, click **DOWNLOAD ARCHIVE (.zip)**.
7. Extract the ZIP archive to access the numbered video files.

Example output:

```text
001 - Introduction.mp4
002 - Setup guide.mp4
003 - Final walkthrough.mp4
```

## Project structure

```text
playlist-pulse/
├── app.py                 # Flask server, routes, background jobs, and ZIP creation
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Main browser interface
├── static/
│   ├── script.js          # Start jobs, poll status, and reveal downloads
│   └── style.css          # Neon terminal visual design
├── LICENSE                # MIT license
└── README.md              # This guide
```

## Troubleshooting

### `python` or `python3` is not recognized

Install Python from [python.org](https://www.python.org/downloads/) and enable the option to add Python to your system `PATH` during Windows installation. Restart VS Code after installing it.

### `ffmpeg` is not recognized

Run `ffmpeg -version`. If it fails, install FFmpeg and add its executable directory to `PATH`. Restart the terminal after changing `PATH`.

### `ModuleNotFoundError: No module named ...`

Activate the virtual environment, then reinstall the dependencies:

```bash
source .venv/bin/activate       # macOS/Linux
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

### Port 5000 is already in use

Stop the other application using port 5000, or change the final line of `app.py` to another port and open the matching address in your browser.

### The ZIP is empty or a playlist item fails

Confirm that the URL is an accessible playlist URL and that the content is available in your region. Large playlists also require sufficient free disk space because videos are downloaded temporarily before the ZIP archive is created.

## Privacy and responsible use

When run locally, YTPULSE processes downloads on the computer where you started the Flask server. The application still connects to YouTube to retrieve requested content. Use it only for videos you own, have permission to download, or are otherwise legally allowed to save. Respect copyright, YouTube's terms, and applicable law.

Do not expose a local development server directly to the public internet without adding authentication, access controls, and a production deployment configuration.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes locally.
4. Open a pull request with a clear description of the change.

## License

YTPULSE is released under the MIT License. See [LICENSE](LICENSE) for the complete terms.
