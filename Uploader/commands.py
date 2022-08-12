# MIT License

# Copyright (c) 2022 Hash Minner

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

import os

from pyrogram import Client, filters
from pyrogram.types import Message
from Uploader.script import Translation

if bool(os.environ.get("WEBHOOK")):
    from Uploader.config import Config
else:
    from sample_config import Config


@Client.on_message(
    filters.command("start") & filters.private,
)
async def start_bot(_, m: Message):
    return await m.reply_text(
        Translation.START_TEXT.format(m.from_user.first_name),
        reply_markup=Translation.START_BUTTONS,
        disable_web_page_preview=True,
        quote=True,
    )


@Client.on_message(
    filters.command("help") & filters.private,
)
async def help_bot(_, m: Message):
    return await m.reply_text(
        Translation.HELP_TEXT,
        reply_markup=Translation.HELP_BUTTONS,
        disable_web_page_preview=True,
    )


@Client.on_message(
    filters.command("about") & filters.private,
)
async def aboutme(_, m: Message):
    return await m.reply_text(
        Translation.ABOUT_TEXT,
        reply_markup=Translation.ABOUT_BUTTONS,
        disable_web_page_preview=True,
    )
