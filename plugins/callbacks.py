import os
import ast

from pyrogram import Client as kinu
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# that's kind of shit, :) stuck here so long
from translation import Translation

@kinu.on_callback_query()
async def cd_handler(client, query):
    
    
    if query.data == "help_user":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                InlineKeyboardButton(
                        "🤖 Updates", url="https://t.me/TMWAD"),
                InlineKeyboardButton(
                        "😊 About Me", callback_data="about_msg")
            ]
        )
        
        await query.message.edit_text(
            Translation.HELP_USER,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    
    elif query.data == "about_msg":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🤖 Help", url="https://t.me/TMWAD"),
                    InlineKeyboardButton(
                        "🦸 Deverlpoer", url="https://github.com/kalanakt")
                ],
                [
                    InlineKeyboardButton("BACK", callback_data="help_user"),
                    InlineKeyboardButton("CLOSE", callback_data="close_data"),
                ]
            ]
        )
        
        await query.message.edit_text(
            Translation.ABOUT_MSG,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    
    elif query.data == "close_data":
        await query.message.delete()
            
                

    
    
    

