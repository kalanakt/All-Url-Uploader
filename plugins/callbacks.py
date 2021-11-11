import os
import ast

from pyrogram import Client as kinu
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from translation import translation

@kinu.on_callback_query()
async def cd_handler(client, query):
    
    if query.data == "start_data":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Command Help", callback_data="help_data")
                ]
            ]
        )

        await query.message.edit_text(
            Script.START_MSG.format(query.from_user.mention),
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    
    elif query.data ==  "HELP_USER":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                InlineKeyboardButton(
                        "🤖 Updates", url="https://t.me/TMWAD"),
                InlineKeyboardButton(
                        "😊 About Me", callback_data="about_data")
            ]
        )
        
        await query.message.edit_text(
            translation.help_user,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    
    elif query.data == "about_data":
        await query.answer()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🤖 Help", url="https://t.me/TMWAD"),
                    InlineKeyboardButton(
                        "🦸 Deverlpoer", url="https://github.com/kalanakt")
                ],
                [
                    InlineKeyboardButton("BACK", callback_data="help_data"),
                    InlineKeyboardButton("CLOSE", callback_data="close_data"),
                ]
            ]
        )
        
        await query.message.edit_text(
            translation.about_msg,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    
    elif query.data == "close_data":
        await query.message.delete()
       
    
    
    
            
    
    
    
            
                

    
    
    

