<p align="center">
  <a href="https://github.com/Seis05640/All-Url-Uploader">
    <img src="https://iili.io/BOeHp5J.jpg" alt="All Url Uploader banner" width="100%"/>
  </a>
</p>

<div align="center">

# All Url Uploader (2GB Upload Support)

**Download direct links and web media, then upload files up to 2GB to Telegram.**

Built with `aiogram 3`, `yt-dlp`, `uv`, and an embedded local **Telegram Bot API server** in a single Docker container.

[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3110/)
[![License](https://img.shields.io/github/license/Seis05640/All-Url-Uploader)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Seis05640/All-Url-Uploader?style=flat)](https://github.com/Seis05640/All-Url-Uploader/stargazers)

[Features](#key-features) · [Quick Start](#quick-start) · [Environment Variables](#environment-variables) · [Deployment](#docker--render-deployment)

</div>

---

**All Url Uploader** is an advanced Telegram bot designed to fetch files from direct URLs, YouTube, MediaFire, Google Drive, Mega, and other `yt-dlp` compatible sites, sending them back to Telegram with rich metadata, custom thumbnails, and full file-type retention.

By integrating a **self-hosted Telegram Bot API server** inside the container running alongside the bot via `supervisord`, file upload limits are expanded from the standard 50MB HTTP limit up to **2000MB (2GB)**!

---

## ⚡ Key Features

- 🚀 **2GB Upload Limit**: Bundles the official `telegram-bot-api` binary in local mode (`is_local=True`), bypassing HTTP payload limits and enabling direct local filesystem transfers.
- 📊 **Live Download & Upload Progress**: Real-time progress bars for both downloading and uploading operations, displaying speed (MB/s), transferred size, percentage, and dynamic ETA calculation.
- 🌐 **Robust Direct Downloading**: Preserves native file extensions (e.g., `.bin`, `.mkv`, `.iso`), includes browser-like `User-Agent` headers to prevent server blockades, and supports Basic Authentication.
- 🎥 **Rich Media Processing**: Automatic extraction of video dimensions, audio duration, and video note length, along with thumbnail generation.
- 🖼️ **Per-User Thumbnails**: Save and manage custom thumbnails using `/thumb` and `/delthumb`.
- ⚙️ **Single-Container Deployment**: Orchestrated with `supervisord` for zero-friction deployment on cloud platforms like Render, Railway, or VPS.

---

## 🔗 Supported Link Formats

| Format | Syntax Example | Description |
| :--- | :--- | :--- |
| **Standard Link** | `https://example.com/video.mp4` | Downloads with original file name & extension |
| **Custom File Name** | `https://example.com/file|my_video.mp4` | Saves and uploads with specified name |
| **Protected Download** | `https://example.com/file|video.mp4|user|pass` | Direct download with HTTP Basic Auth |
| **Media Links** | `https://youtu.be/...` | Uses `yt-dlp` for quick audio/video or format selection |

---

## 🤖 Bot Commands

- `/start` — Welcome message, status overview, and usage guidance.
- `/help` — Detailed description of supported link formats and options.
- `/about` — System information, host details, and repository link.
- `/thumb` — View your currently saved custom upload thumbnail.
- `/delthumb` — Delete your saved custom upload thumbnail.

---

## ⚙️ Environment Variables

Set the following environment variables in your `.env` file or cloud platform settings:

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `BOT_TOKEN` | **Yes** | — | Telegram Bot API token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | **Yes** | — | Telegram user ID of the bot administrator |
| `TELEGRAM_API_ID` | **Yes** | — | Telegram API ID from [my.telegram.org](https://my.telegram.org) (for local API server) |
| `TELEGRAM_API_HASH` | **Yes** | — | Telegram API Hash from [my.telegram.org](https://my.telegram.org) (for local API server) |
| `AUTH_USERS` | No | — | Comma-separated user IDs allowed to bypass cooldown restrictions |
| `DOWNLOAD_LOCATION` | No | `./DOWNLOADS` | Base directory for temporary download storage |
| `CHUNK_SIZE` | No | `128` | Direct-download chunk size (in KB if `<1024`) |
| `HTTP_PROXY` | No | — | HTTP/HTTPS proxy URL for downloading requests |
| `PROCESS_MAX_TIMEOUT` | No | `3700` | Process execution and upload session timeout in seconds |

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Configure

```bash
git clone https://github.com/Seis05640/All-Url-Uploader.git
cd All-Url-Uploader
```

Create a `.env` file in the root directory:

```dotenv
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuVWXyz
OWNER_ID=123456789
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=your_api_hash_here
DOWNLOAD_LOCATION=./DOWNLOADS
PROCESS_MAX_TIMEOUT=3700
```

### 2. Install Dependencies

Using `uv` (recommended):

```bash
uv sync --group dev
```

### 3. Run the Bot

```bash
uv run python bot.py
```

*Note: For local testing without supervisor, uploads will be handled via standard Telegram API limits (50MB) unless a local `telegram-bot-api` binary is running on port 8081.*

---

## 🐳 Docker & Render Deployment

The included multi-stage `Dockerfile` combines the official `aiogram/telegram-bot-api` binary with Python 3.11 Alpine, running both the API server and bot concurrently via `supervisord`.

### Docker CLI

```bash
docker build -t all-url-uploader .
docker run -d --name url_uploader --env-file .env all-url-uploader
```

### Deploying to Render

1. Create a new **Web Service** or **Background Worker** on [Render](https://render.com).
2. Connect your GitHub repository (`Seis05640/All-Url-Uploader`).
3. Select **Docker** as the Environment.
4. Add the required Environment Variables (`BOT_TOKEN`, `OWNER_ID`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`).
5. Deploy! `supervisord` will automatically launch the local API server on port 8081 and start the bot service.

---

## 🧪 Running Tests

```bash
uv run pytest
uv run pylint $(git ls-files '*.py')
```

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).
