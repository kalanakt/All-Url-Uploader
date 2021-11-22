from pyrogram import Client
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

plugins = dict(root="megadl/modules")
TMWADbot = Client(
        "All Url Uploader",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        plugins=plugins
    )
