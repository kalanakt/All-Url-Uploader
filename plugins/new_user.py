# (c) HashMinner

import os
import time, datetime
from pyrogram import filters
from pyrogram import Client as Clinton

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
    
from database.database import Database
db = Database()

@Clinton.on_callback_query()
async def __(c, m):
    await foo(c, m, cb=True)
    

@Clinton.on_message(filters.private)
async def _(c, m):
    await foo(c, m)
    
async def foo(c, m, cb=False):
    chat_id=update.message.chat.id,
    
    if not await db.is_user_exist(chat_id):
        await db.add_user(chat_id)
        await c.send_message(Config.LOG_CHANNEL, f"#New User \n {m.from_user.mention}.")
