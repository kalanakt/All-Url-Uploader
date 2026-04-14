# Contributing

Thanks for helping improve All Url Uploader.

This project is a Telegram bot built with `aiogram`, `yt-dlp`, and `uv`. Contributions are welcome for bug fixes, tests, docs improvements, cleanup, and new features that fit the bot's current scope.

## Before You Start

- search existing [issues](https://github.com/kalanakt/All-Url-Uploader/issues) and [discussions](https://github.com/kalanakt/All-Url-Uploader/discussions) first
- open an issue or discussion before large changes so the direction is clear
- keep changes focused; avoid mixing refactors, docs edits, and feature work unless they are directly related

## Local Setup

1. Clone the repository:

```bash
git clone https://github.com/kalanakt/All-Url-Uploader.git
cd All-Url-Uploader
```

2. Create a `.env` file:

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

4. Run the bot locally:

```bash
uv run python bot.py
```

## Project Layout

- root runtime entrypoints: `bot.py`, `app.py`, `config.py`
- Telegram routers: `routers/`
- services and integrations: `services/`
- shared helpers, models, keyboards, and text: `utils/`
- automated tests: `tests/`
- external documentation site: `docs/`

## Development Guidelines

- follow the current `aiogram` 3.x structure and existing project patterns
- prefer small, reviewable pull requests
- add or update tests when behavior changes
- keep user-facing copy clear and consistent
- avoid reintroducing removed legacy runtime files or deployment assumptions

## Checks

Run these before opening a pull request:

```bash
uv run pytest
uv run pylint $(git ls-files '*.py')
cd docs && npm run build
```

If your change only touches Python code, the docs build is still a good final sanity check before you open the PR.

## Pull Requests

When opening a pull request:

- use a clear title and summary
- explain the user-facing impact
- mention any environment or deployment implications
- include screenshots only when the docs site or rendered output changed
- link the related issue or discussion when there is one

## Reporting Bugs

Bug reports are most useful when they include:

- what you tried to do
- what happened instead
- steps to reproduce
- logs or traceback output
- relevant environment details such as Python version, host platform, or proxy setup

## Code of Conduct

By participating in this project, you agree to follow the guidelines in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
