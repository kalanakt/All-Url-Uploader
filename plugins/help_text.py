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
from pyrogram import Client as Clinton
from pyrogram import filters
from database.adduser import AddUser
from pyrogram.types import Message
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Clinton.on_message(filters.private & filters.command(["help"]))
async def help_user(bot, update):
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )


@Clinton.on_message(filters.private & filters.command(["start"]))
async def start(bot, message):
  await bot.send_message(
    chat_id=message.chat.id,
    text=Translation.START_TEXT.format(message.from_user.mention),
    reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("💁‍♂️support💁‍♂️", url="https://t.me/disneyteamchat"),
                    InlineKeyboardButton("🤖Update Channel🤖", url="https://t.me/ibomma1947") ,
                    InlineKeyboardButton("🧑‍💻Developer🧑‍💻" , url="https://t.me/unknown1947m")
                ]
            ]
        ),
    reply_to_message_id=message.message_id
  )
