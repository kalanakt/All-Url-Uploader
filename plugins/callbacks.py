import os
import ast
import re
import asyncio

from pyrogram import Client as kinu
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


from translation import Translation

@kinu.on_callback_query()
async def cb_handler(client: kinu, query: CallbackQuery):
    if query.data == "help_kt":
        buttons = [[
            InlineKeyboardButton('Updates', url="https://t.me/TMWAD"),
            InlineKeyboardButton('About', callback_data='about_kt')
            ],[
            InlineKeyboardButton('🏠 Home', callback_data='start_kt'),
            InlineKeyboardButton('🔐 Close', callback_data='close_kt')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Translation.HELP_USER.format(query.from_user.mention),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode='html'
        )
    
    elif query.data == "close_kt":
        await query.message.delete()
        
       
    elif query.data == "start_kt":
        buttons = [[
            InlineKeyboardButton('Help', callback_data='help_kt'),
            InlineKeyboardButton('🤖 Updates', url="https://t.me/TMWAD")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Translation.START_TEXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode='html'
        )
        
       
    if query.data == "about_kt":
        buttons = [[
            InlineKeyboardButton('🦸 Deverloper', url='https://github.com/kalanakt')
            ],[
            InlineKeyboardButton('🏠 Home', callback_data='start_kt'),
            InlineKeyboardButton('🔐 Close', callback_data='close_kt')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Translation.ABOUT_MSG.format(query.from_user.mention),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode='html'
        )
