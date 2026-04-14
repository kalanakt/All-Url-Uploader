<p align="center">
  <a href="https://www.fiverr.com/share/kpLBoo"><img src="https://fiverr-res.cloudinary.com/images/t_main1,q_auto,f_auto,q_auto,f_auto/gigs/310030332/original/dea9a8cecd633a38d59659d455e8a7f46e914505/develop-a-telegram-bot-and-deployed-on-vercel-at-no-cost.jpg"/></a>
</p>

# All Url Uploader

All Url Uploader is a Telegram bot built with `aiogram` and `yt-dlp`. Send it a direct file URL or a supported media link, choose a format when needed, and the bot uploads the result back to Telegram.

## Features

- direct download links
- `url|filename`
- `url|filename|username|password`
- `url * filename`
- YouTube quick audio and video downloads
- format selection for supported `yt-dlp` sources
- custom per-user thumbnails with `/thumb` and `/delthumb`

## Project Layout

- root app runtime: `bot.py`, `app.py`, `config.py`
- request handlers: `routers/`
- shared services: `services/`
- shared helpers and UI text: `utils/`
- external documentation site: `docs/`

## Local Run

1. Create a `.env` file:

```env
BOT_TOKEN=
OWNER_ID=
AUTH_USERS=
DOWNLOAD_LOCATION=./DOWNLOADS
CHUNK_SIZE=128
HTTP_PROXY=
PROCESS_MAX_TIMEOUT=3700
```

2. Install dependencies and start the bot:

```bash
uv sync --group dev
uv run python bot.py
```

## Configuration Notes

- `BOT_TOKEN` and `OWNER_ID` are required.
- `AUTH_USERS` is optional. Authorized users bypass the per-request cooldown.
- `CHUNK_SIZE` values below `1024` are treated as kilobytes for compatibility with the older config style.

## Docker

Build and run:

```bash
docker build -t all-url-uploader .
docker run --env-file .env all-url-uploader
```

## Tests

Run the test suite with:

```bash
uv run pytest
```
