
# (c) @AbirHasan2005 | Modifieded By : @DC4_WARRIOR

import traceback
import os

from pyrogram import Client as Clinton
from pyrogram import filters

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
from database.access import clinton

@Clinton.on_message(filters.private & filters.command('total'))
async def sts(c, m):
    if m.from_user.id != Config.OWNER_ID:
        return 
    total_users = await clinton.total_users_count()
    await m.reply_text(text=f"Total user(s) {total_users}", quote=True)

