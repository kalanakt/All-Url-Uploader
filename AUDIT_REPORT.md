# AUDIT REPORT - All-Url-Uploader

**Date:** 2026-10-25  
**Repository:** D:\pro\All-Url-Uploader  
**Audited by:** Kilo AI Engineer

## Executive Summary

All-Url-Uploader is a Telegram bot built with aiogram 3.x that downloads media from direct URLs and yt-dlp supported sites, with 2GB upload support via a local Telegram Bot API server. The architecture is relatively clean with good separation of concerns, but there are several security, performance, and maintainability issues that need attention, and no analytics dashboard exists currently.

## Architecture Overview

### Core Components
```
bot.py -> app.py (bot setup, dispatcher, session with local Bot API)
config.py (settings from env)
routers/ (commands, intake, callbacks, thumbnails)
services/ (downloaders, uploaders, stores, cooldown, progress)
utils/ (models, logging, keyboards, text)
```

### Request Lifecycle
1. User sends message with URL in private chat → `routers/intake.py`
2. Link extraction via `services/parsing.py` (supports `|`, `*` separators, entities)
3. Cooldown check via `services/cooldown.py` (per-user, except auth users/owner)
4. For YouTube URLs: immediate quick choices (Audio/Video); for others: `yt-dlp` probe, fallback to direct download
5. User selects format via callback → `routers/callbacks.py` routes to appropriate downloader
6. Download to isolated work directory → `services/request_store.py` manages state
7. Upload via `services/telegram_uploads.py` with progress simulation, metadata extraction
8. Cleanup temp files in finally block

### Technology Stack
- **Bot Framework:** aiogram 3.21+ (async)
- **HTTP Client:** aiohttp 3.14+
- **Media Download:** yt-dlp 2026.6.9+
- **Media Metadata:** hachoir 3.3.0+
- **Deployment:** Docker + supervisord (bot + local telegram-bot-api)
- **Storage:** File-based (JSON for request state, files for thumbnails)
- **Python:** 3.11

## Component Inventory

| Component | Purpose | Status |
|-----------|---------|--------|
| bot.py, app.py | Entry point & bot initialization | Good |
| config.py | Environment config | Minimal, needs validation |
| routers/commands.py | /start, /help, /about, UI callbacks | Basic |
| routers/intake.py | URL parsing, cooldown, option generation | Core logic |
| routers/callbacks.py | Request processing orchestration | Core logic |
| routers/thumbnails.py | Custom thumbnail management | Simple |
| services/ytdlp.py | yt-dlp probe/download with options | Core |
| services/direct_downloads.py | Direct HTTP downloads with progress | Core |
| services/telegram_uploads.py | Upload to Telegram with progress simulation | Core |
| services/request_store.py | File-based request state & work dirs | Simple |
| services/thumbnail_store.py | User thumbnail storage | Simple |
| services/cooldown.py | In-memory per-user cooldown | Simple (lost on restart) |
| services/progress.py | Progress/formatting utilities | Good |
| services/parsing.py | URL/format parsing | Good |
| utils/models.py | Dataclasses for data structures | Good |
| utils/logging_config.py | Logging setup + redaction | Good basics |
| Dockerfile, supervisord.conf | Container orchestration | Good for 2GB support |

## Security Findings

### HIGH SEVERITY

#### 1. No SSRF Protection
- **Files:** `services/direct_downloads.py:83-88`, `services/ytdlp.py:78`
- **Issue:** No validation of user-supplied URLs against private/internal/loopback addresses
- **Risk:** Server-Side Request Forgery
- **Recommendation:** Implement URL allowlist/blocklist, DNS resolution checks, IP validation

#### 2. Credentials in Logs/Exposure
- **Files:** `services/direct_downloads.py:68-69`, `routers/callbacks.py:140`
- **Issue:** Basic auth passed, exceptions logged/exposed to users
- **Risk:** Credential leakage, information disclosure
- **Recommendation:** Enhance redaction, sanitize error messages

#### 3. Path Traversal Risk
- **Files:** `services/direct_downloads.py:52-54,99`
- **Issue:** Custom filenames from user input used without sanitization
- **Risk:** Writing outside intended directories
- **Recommendation:** Sanitize filenames, use Path.name, reject paths with separators

#### 4. Insecure SSL Handling
- **Files:** `services/direct_downloads.py:63-66`
- **Issue:** Disables SSL verification when proxy used
- **Risk:** MITM
- **Recommendation:** Fix proxy handling

### MEDIUM SEVERITY

#### 5. No Authentication/Authorization
- **Issue:** Only cooldown bypass uses auth_users; no admin features protected
- **Recommendation:** Add proper authorization

#### 6. Unbounded Caches
- **Files:** `services/cooldown.py:10`
- **Issue:** Memory grows unbounded
- **Recommendation:** Add cleanup/TTL

#### 7. Exception Leakage
- **Files:** `routers/callbacks.py:140`
- **Issue:** Raw exceptions shown to users
- **Recommendation:** Generic messages, detailed logging

## Performance Findings

### HIGH IMPACT
1. **Blocking I/O in async context** - `direct_downloads.py` writes synchronously
2. **No connection pooling** - new session per download
3. **Unbounded cooldown cache** - memory leak
4. **No concurrency control** - unlimited parallel requests

### MEDIUM IMPACT
5. **Inefficient file discovery** in yt-dlp downloads
6. **No subprocess timeouts**

## Recommended Upgrades (Priority)
**P0:** SSRF protection, path traversal prevention, exception sanitization, SSL fix  
**P1:** Async I/O, connection pooling, bounded concurrency, cache cleanup, subprocess timeouts  
**P2:** Dashboard with auth, analytics DB, health checks  
**P3:** Better error handling, tests, docs

## Next Steps
Start with P0 security fixes, then performance improvements, then dashboard implementation.
