START_TEXT = """Hi, <b>{name}</b>

I can take a direct file link or a supported media URL, download it, and upload the result back to Telegram.

<b>What you can send</b>
- direct file URLs
- YouTube and other supported `yt-dlp` links
- `url|filename`
- `url|filename|username|password`
- `url * filename`

Use the buttons below for a quick tour, or send a link to get started."""

HELP_TEXT = """<b>How to use this bot</b>

Send a message containing any of these formats:

1. <b>Direct link</b>
   <code>https://example.com/file.mp4</code>

2. <b>Direct link with a custom file name</b>
   <code>https://example.com/file.mp4|my-video.mp4</code>

3. <b>Protected URL with login details</b>
   <code>https://example.com/file|my-file.mp4|username|password</code>

4. <b>Alternate custom-name format</b>
   <code>https://example.com/file.mp4 * renamed.mp4</code>

<b>Extra commands</b>
- <code>/thumb</code> shows your saved thumbnail
- <code>/delthumb</code> removes your saved thumbnail

If the source supports multiple formats, I will show you a selection menu before uploading."""

ABOUT_TEXT = """<b>All Url Uploader</b>

Built with <a href="https://docs.aiogram.dev/">aiogram 3</a> and <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a>.

<b>Repository</b>
<a href="https://github.com/kalanakt/All-Url-Uploader">github.com/kalanakt/All-Url-Uploader</a>

<b>What it does</b>
- downloads supported media from direct URLs and `yt-dlp` sources
- lets you choose formats when the source exposes multiple options
- uploads video, audio, and documents back to Telegram
- supports custom per-user thumbnails

Send a supported link whenever you are ready."""

THUMB_SAVED = "Your custom thumbnail is saved."
THUMB_MISSING = "You do not have a thumbnail yet. Send a JPG image to save one."
THUMB_REMOVED = "Your thumbnail was removed successfully."

PROCESSING = "Processing your link..."
FORMAT_SELECTION = "Choose the format you want."
DOWNLOAD_START = "Downloading <b>{name}</b>"
UPLOAD_START = "Uploading <b>{name}</b>"
QUICK_CHOICE = "Choose how you want this YouTube link downloaded."
YOUTUBE_AUDIO_LABEL = "Audio"
YOUTUBE_VIDEO_LABEL = "Video"
RATE_LIMIT = (
    "Please wait before starting another request. Try again in about {minutes} minute(s)."
)
DOWNLOAD_FAILED = "I could not process that link."
DIRECT_DOWNLOAD_FAILED = "I could not download that file."
REQUEST_EXPIRED = "That request has expired. Send the link again."
FILE_TOO_LARGE = (
    "Downloaded in {seconds} seconds.\nDetected file size: {size}\n"
    "I cannot upload files larger than Telegram allows."
)
DONE = "Downloaded in {download_seconds} seconds.\nUploaded in {upload_seconds} seconds."


def upload_caption(name: str) -> str:
    return UPLOAD_START.format(name=name)


def download_caption(name: str) -> str:
    return DOWNLOAD_START.format(name=name)
