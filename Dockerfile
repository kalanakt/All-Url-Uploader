FROM aiogram/telegram-bot-api:latest AS api-source

FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies for the bot, the Bot API server, and supervisor
RUN apk add --no-cache \
    curl \
    ffmpeg \
    supervisor \
    libstdc++ \
    libssl3 \
    zlib \
    ca-certificates

# Copy the precompiled Telegram Bot API binary
COPY --from=api-source /usr/local/bin/telegram-bot-api /usr/local/bin/telegram-bot-api

# Install uv using the official standalone installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Pre-sync dependencies to leverage caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy supervisord config and remains of source code
COPY supervisord.conf /etc/supervisord.conf
COPY . .
RUN uv sync --frozen --no-dev

# Prepare local data directory for the Bot API server storage
RUN mkdir -p /data/telegram-bot-api && chmod 777 /data/telegram-bot-api

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
