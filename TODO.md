# YTPULSE hosted website

- Preserve the neon terminal-style interface and established frontend interactions.
- Accept a pasted YouTube playlist URL and let users select MP4 or MKV output.
- Run yt-dlp and ffmpeg on the hosted server with video quality capped at 720p.
- Process playlist downloads as background jobs so requests remain responsive.
- Poll live download progress and server logs in the existing interface.
- Keep playlist items numbered in playlist order and package completed downloads as a ZIP archive.
- Provide a browser download for the completed ZIP and handle temporary job files safely.
- Retain the Flask route structure while adding production-safe validation, error handling, and job isolation.
- Deploy with a persistent production web runtime suitable for Flask, yt-dlp, ffmpeg, long-running jobs, and concurrent users.
- Preserve attribution and distribution terms under the MIT license.
