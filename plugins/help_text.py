#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K | @Edit By Hash Minner

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import asyncio
import sqlite3

# the secret configuration specific things
from sample_config import Config

# the Strings used for this "thing"
from translation import Translation
from pyrogram import Client
from pyrogram import filters
from database.adduser import AddUser
from database.footerdb import get_footer, remove_footer, update_footer, add_footer
from pyrogram.types import Message
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

FOOTER_TEXT = """
Use Correct Method:

**Add Footer**

/footer your footer text

ex: /footer Join @TMWAD For More Bots

**Update Footer**

/updatefooter your footer text

ex: /updatefooter Join @TMWAD For Bots Updates

**Remove Footer**

Send /removefooter Command

"""
@Client.on_message(filters.private & filters.command(["help"]))
async def help_user(bot, update):
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )

@Client.on_message(filters.command("footer") & filters.private) 
async def footer(bot, cmd):
	chat_id = cmd.chat.id
	if (" " in cmd.text) and (cmd.text is not None):
		cmdtxt, footer = cmd.text.split(" ", 1)
		await add_footer(chat_id, footer)
    footer = await get_footer(chat_id)
		await cmd.reply_text(f"your footer saved ✔. \nuse /updatefooter NEW FOOTER for update your api. \nEg:- /updatefooter Join @TMWAD For More Updates \nUse /removefooter For delete footer. \nNew Footer is \n\n{footer}")
        
	else:
		await cmd.reply_text(
			FOOTER_TEXT, 
			disable_web_page_preview=True
			)

@Client.on_message(filters.command("updatefooter") & filters.private)
async def updatefooter(bot, cmd):
	chat_id = cmd.chat.id
	if (" " in cmd.text) and (cmd.text is not None):
		cmdtxt, footer = cmd.text.split(" ", 1)
		await update_footer(chat_id, footer)
    footer = await get_footer(chat_id)
		await cmd.reply_text(f"your footer updated ✔. Use /removefooter For delete footer \nNew Footer is \n\n{footer}")
        
	else:
		await cmd.reply_text(
			FOOTER_TEXT, 
			disable_web_page_preview=True
			)

@Client.on_message(filters.command("removefooter") & filters.private)
async def removefooter(bot, cmd):
	chat_id = cmd.chat.id
	await remove_footer(chat_id)
	await cmd.reply_text("your footer is removed ✔. Use /footer NEW FOOTER For add new footer")
    
@Client.on_message(filters.private & filters.command(["start"]))
async def start(bot, message):
  await bot.send_message(
    chat_id=message.chat.id,
    text=Translation.START_TEXT.format(message.from_user.mention),
    reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Comment", url="https://t.me/TMWAD/18"),
                    InlineKeyboardButton("🤖 Updates", url="https://t.me/TMWAD")
                ]
            ]
        ),
    reply_to_message_id=message.message_id
  )
