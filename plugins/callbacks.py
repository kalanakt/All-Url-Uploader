import os
import ast

from pyrogram import Client as kinu
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# that's kind of shit, :) stuck here so long
from translation import Translation

@kinu.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "help_user":
        buttons = [[
            InlineKeyboardButton('Updates', url="https://t.me/TMWAD"),
            InlineKeyboardButton('Comments', url="https://t.me/TMWAD/17")
            ],[
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Translation.HELP_USER.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    
    elif query.data == "close_data":
        await query.message.delete()
            
                

    
    
    

