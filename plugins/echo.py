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
import time
import json
import asyncio
import logging
from urllib.parse import urlparse, urlunparse
import ssl
import urllib.request

from opencc import OpenCC

from pyrogram.types import Thumbnail
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Uploader.script import Translation
from Uploader.functions.ran_text import random_char
from Uploader.functions.display_progress import humanbytes
from Uploader.functions.display_progress import humanbytes
from hooks.get_link_type import get_link_type
from config import Config
from core.direct_link import direct_link
from core.vimeo_link import vimeo_link


s2tw = OpenCC('s2tw.json').convert

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    link = update.text
    try:
        parsed_link = urlparse(link)
    except Exception as e:
        logger.error(e)
        return await update.reply_text("Sorry !. your link is not valid")

    base_url = urlunparse((parsed_link.scheme, parsed_link.netloc,
                          parsed_link.path.split('/', 2)[0], '', '', ''))

    if parsed_link.scheme == "https":
        context = ssl.create_default_context()
        # Set the context to not check the server's hostname or certificate
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        # Try to connect to the website
        try:
            with urllib.request.urlopen(base_url, context=context) as response:
                certificate = response.getpeercert()
                if not certificate:
                    return await update.reply_text("Sorry !. link not using SSL/TLS encryption protocol")
        except Exception as e:
            logger.warn(
                f"an error occurred while trying to connect to the website : {e}")
        uvew = await update.reply_text("Please Wait ...")

    elif parsed_link.scheme == "http":
        return await update.reply_text("Sorry !. link not using SSL/TLS encryption protocol")
    else:
        return await update.reply_text("Sorry !. link is using an unsupported protocol")

    link_type = get_link_type(link)

    if link_type == 'type_direct':
        return await direct_link(bot, update, uvew)
    elif link_type == 'type_vimeo':
        return await vimeo_link(bot, update, uvew)
