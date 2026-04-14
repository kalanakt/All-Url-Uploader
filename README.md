<p align="center">
  <a href="https://www.fiverr.com/share/kpLBoo">
    <img src="https://iili.io/BOeHp5J.jpg" alt="All Url Uploader banner" width="100%"/>
  </a>
</p>

<div align="center">

# All Url Uploader

**Upload direct links and supported media sources back to Telegram.**

Built with `aiogram`, `yt-dlp`, and `uv` for a cleaner local workflow.

[![CI](https://github.com/kalanakt/All-Url-Uploader/actions/workflows/ci.yml/badge.svg)](https://github.com/kalanakt/All-Url-Uploader/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kalanakt/All-Url-Uploader/actions/workflows/codeql.yml/badge.svg)](https://github.com/kalanakt/All-Url-Uploader/actions/workflows/codeql.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3110/)
[![License](https://img.shields.io/github/license/kalanakt/All-Url-Uploader)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/kalanakt/All-Url-Uploader?style=flat)](https://github.com/kalanakt/All-Url-Uploader/stargazers)
[![All Contributors](https://img.shields.io/github/all-contributors/kalanakt/All-Url-Uploader?color=ee8449&style=flat-square)](#contributors)

[Docs](docs/README.md) · [Contributing](CONTRIBUTING.md) · [Docker](Dockerfile) · [Issues](https://github.com/kalanakt/All-Url-Uploader/issues) · [Discussions](https://github.com/kalanakt/All-Url-Uploader/discussions) 

</div>

All Url Uploader is a Telegram bot that accepts direct file URLs and supported media links, downloads them with the right tool for the job, and sends the result back to Telegram with the correct media type, metadata, and optional custom thumbnail.

## What It Handles

- direct file links
- `url|filename`
- `url|filename|username|password`
- `url * filename`
- YouTube quick audio and quick video downloads
- format selection for supported `yt-dlp` sources
- custom per-user thumbnails with `/thumb` and `/delthumb`

## Bot Commands

- `/start` - welcome message, shortcuts, and usage guidance
- `/help` - supported link formats and flow overview
- `/about` - runtime details, repo link, and project notes
- `/thumb` - show the currently saved custom thumbnail
- `/delthumb` - remove the saved custom thumbnail

## Quick Start

1. Clone the repository and move into it:

```bash
git clone https://github.com/kalanakt/All-Url-Uploader.git
cd All-Url-Uploader
```

2. Create a `.env` file in the project root:

```dotenv
BOT_TOKEN=
OWNER_ID=
AUTH_USERS=
DOWNLOAD_LOCATION=./DOWNLOADS
CHUNK_SIZE=128
HTTP_PROXY=
PROCESS_MAX_TIMEOUT=3700
```

3. Install dependencies:

```bash
uv sync --group dev
```

4. Start the bot:

```bash
uv run python bot.py
```

## Environment

- `BOT_TOKEN` - required Telegram bot token
- `OWNER_ID` - required Telegram user ID for the bot owner
- `AUTH_USERS` - optional comma-separated list of user IDs that bypass the cooldown
- `DOWNLOAD_LOCATION` - optional base directory for temporary downloads and uploads
- `CHUNK_SIZE` - optional direct-download chunk size; values below `1024` are treated as kilobytes for backward compatibility
- `HTTP_PROXY` - optional proxy URL passed to network requests and `yt-dlp`
- `PROCESS_MAX_TIMEOUT` - optional process timeout in seconds for external tools

## Project Layout

- root runtime entrypoints: `bot.py`, `app.py`, `config.py`
- routers: `routers/`
- services: `services/`
- shared helpers and models: `utils/`
- tests: `tests/`
- external documentation site: `docs/`

## Docker

Build and run the container with your existing `.env` file:

```bash
docker build -t all-url-uploader .
docker run --env-file .env all-url-uploader
```

## Checks

Run the same core checks used in GitHub Actions:

```bash
uv run pytest
uv run pylint $(git ls-files '*.py')
cd docs && npm run build
```

<!-- readme: contributors -start -->
<table>
	<tbody>
		<tr>
            <td align="center">
                <a href="https://github.com/kalanakt">
                    <img src="https://avatars.githubusercontent.com/u/86665964?v=4" width="100;" alt="kalanakt"/>
                    <br />
                    <sub><b>kalana kt</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/tromcho">
                    <img src="https://avatars.githubusercontent.com/u/113139586?v=4" width="100;" alt="tromcho"/>
                    <br />
                    <sub><b>tromcho</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/fzsouser">
                    <img src="https://avatars.githubusercontent.com/u/108298343?v=4" width="100;" alt="fzsouser"/>
                    <br />
                    <sub><b>Fzso</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/hybridvamp">
                    <img src="https://avatars.githubusercontent.com/u/48980248?v=4" width="100;" alt="hybridvamp"/>
                    <br />
                    <sub><b>HYBRID</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/Divarion-D">
                    <img src="https://avatars.githubusercontent.com/u/42798043?v=4" width="100;" alt="Divarion-D"/>
                    <br />
                    <sub><b>Danil</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/AvikaTrivedi">
                    <img src="https://avatars.githubusercontent.com/u/84050503?v=4" width="100;" alt="AvikaTrivedi"/>
                    <br />
                    <sub><b>Avika Trivedi</b></sub>
                </a>
            </td>
		</tr>
		<tr>
            <td align="center">
                <a href="https://github.com/libresoul">
                    <img src="https://avatars.githubusercontent.com/u/69932259?v=4" width="100;" alt="libresoul"/>
                    <br />
                    <sub><b>Damindu Dhananjitha</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/ImgBotApp">
                    <img src="https://avatars.githubusercontent.com/u/31427850?v=4" width="100;" alt="ImgBotApp"/>
                    <br />
                    <sub><b>Imgbot</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/satyanandatripathi">
                    <img src="https://avatars.githubusercontent.com/u/83153745?v=4" width="100;" alt="satyanandatripathi"/>
                    <br />
                    <sub><b>Parthiv Katapara </b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/IndrajeethY">
                    <img src="https://avatars.githubusercontent.com/u/79161058?v=4" width="100;" alt="IndrajeethY"/>
                    <br />
                    <sub><b>Indrajeeth</b></sub>
                </a>
            </td>
		</tr>
	<tbody>
</table>
<!-- readme: contributors -end -->
