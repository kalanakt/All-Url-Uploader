import os
import ast
import re
import asyncio

from pyrogram import Client as kinu
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# that's kind of shit, :) stuck here so long
from translation import Translation

@kinu.on_callback_query()
async def cb_handler(client: kinu, query: CallbackQuery):
    if query.data == "help_user":
        buttons = [[
            InlineKeyboardButton('Updates', url="https://t.me/TMWAD"),
            InlineKeyboardButton('About', callback_data='about')
            ],[
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Translation.HELP_USER.format(query.from_user.mention),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode='html'
        )
    
    elif query.data == "close_data":
        await query.message.delete()
        
       
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('Help', callback_data='help_user'),
            InlineKeyboardButton('🤖 Updates', url="https://t.me/TMWAD")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Translation.START_TEXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode='html'
        )
        
       
    if query.data == "about":
        buttons = [[
            InlineKeyboardButton('🦸 Deverloper', url='https://github.com/kalanakt')
            ],[
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Translation.ABOUT_MSG.format(query.from_user.mention),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode='html'
        )
