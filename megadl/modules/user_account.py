import json
import os
import time
import wget


from pyrogram import Client, filters
from pyrogram.methods import password
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from hurry.filesize import size
from functools import partial
from asyncio import get_running_loop

from megadl.helpers_nexa.account import email, password, m
from .mega_dl import basedir
from megadl.helpers_nexa.mega_help import progress_for_pyrogram, humanbytes, send_errors, send_logs
from config import Config

def USER_ACC_INFO():
  try:
    get_user = m.get_user()
    imported_user = json.dumps(get_user)
    uacc_info = json.loads(imported_user)
    acc_email = uacc_info['email']
    acc_name = uacc_info['name']
    acc_quota = m.get_quota()
    js_acc_space = m.get_storage_space()
    acc_space_f = json.dumps(js_acc_space)
    acc_space = json.loads(acc_space_f)
    btotal_space = acc_space['total']
    bused_space = acc_space['used']
    bfree_space = btotal_space - bused_space
    total_space = size(btotal_space)
    used_space = size(bused_space)
    free_space = size(bfree_space)
    USER_ACC_INFO.info = f"""
**~ Your User Account Info ~**

✦ **Account Name:** `{acc_name}`
✦ **Email:** `{acc_email}`
✦ **Storage,**
    - **Total:** `{total_space}`
    - **Used:** `{used_space}`
    - **Free:** `{free_space}`
✦ **Quota:** `{acc_quota} MB`
"""
  except Exception as e:
    send_errors(e)

@Client.on_message(filters.command("info") & filters.private)
async def accinfo(client: Client, message: Message):
  if message.from_user.id not in Config.AUTH_USERS:
    await message.reply_text("**Sorry this bot isn't a Public Bot 🥺! But You can make your own bot ☺️, Click on Below Button!**", reply_markup=GITHUB_REPO)
    return
  acc_info_msg = await message.reply_text("`Processing ⚙️...`")
  if email and password is None:
    await acc_info_msg.edit("`Setup an User Account to Use this Feature!`")
    return
  loop = get_running_loop()
  await loop.run_in_executor(None, partial(USER_ACC_INFO))
  await acc_info_msg.edit(USER_ACC_INFO.info)


# Upload files from telegram to Mega.nz
public_link = None

def UploadToMega(toupload, megaupmsg):
  global public_link
  try:
    uploadfile = m.upload(f"{toupload}", upstatusmsg=megaupmsg)
    public_link = m.get_upload_link(uploadfile)
  except Exception as e:
    send_errors(e)


@Client.on_message(filters.command("upload") & filters.private)
async def uptomega(client: Client, message: Message):
  the_uid = message.from_user.id
  the_cid = message.chat.id
  if the_uid not in Config.AUTH_USERS:
    await message.reply_text("**Sorry this bot isn't a Public Bot 🥺! But You can make your own bot ☺️, Click on Below Button!**", reply_markup=GITHUB_REPO)
    return
  megauplaod_msg = await message.reply_text("`Processing ⚙️...`")
  if email and password is None:
    await megauplaod_msg.edit("`Setup an User Account to Use this Feature!`")
    return
  todownfile = message.reply_to_message
  if todownfile is None:
    await megauplaod_msg.edit("**Please reply to a Media File or Direct Link to Upload!**")
    return
  if todownfile.media is None:
    try:
      direct_link_path = f"{basedir}/{the_uid}"
      url = todownfile.text
      if os.path.isdir(direct_link_path):
        await megauplaod_msg.edit("`Already One Process is Going On. Please wait until it's finished!`")
        return
      else:
        os.makedirs(direct_link_path)
        megaupmsg = await megauplaod_msg.edit("**Starting to Download The Content to My Server! This may take while 😴**")
        send_logs(user_id=the_uid, mchat_id=the_cid, mega_url=url, upload_logs=True)
        toupload = wget.download(url, out=direct_link_path)
        loop = get_running_loop()
        await loop.run_in_executor(None, partial(UploadToMega, toupload, megaupmsg, the_uid, the_cid, direct_url=url))
        link = public_link
        await megaupmsg.edit(f"**Successfully Uploaded To Mega.nz** \n\n**Link:** `{link}` \n\n**Powered by @NexaBotsUpdates**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📥 Mega.nz Link 📥", url=f"{link}")]]))
        os.remove(toupload)
      return
    except Exception as e:
      await send_errors(e=e)
      return
  try:
    start_time = time.time()
    await megauplaod_msg.delete()
    megaupmsg = await message.reply_text("**Starting to Download The Content to My Server! This may take while 😴**")
    await send_logs(user_id=the_uid, mchat_id=the_cid, up_file=todownfile, upload_logs=True)
    toupload = await client.download_media(message=todownfile, progress=progress_for_pyrogram, progress_args=("**Trying to Download!** \n", megaupmsg, start_time))
    await megaupmsg.edit("**Successfully Downloaded the File!**")
    await megaupmsg.edit("**Trying to Upload to Mega.nz! This may take while 😴**")
    loop = get_running_loop()
    await loop.run_in_executor(None, partial(UploadToMega, toupload, megaupmsg))
    link = public_link
    await megaupmsg.edit(f"**Successfully Uploaded To Mega.nz** \n\n**Link:** `{link}` \n\n**Powered by @NexaBotsUpdates**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📥 Mega.nz Link 📥", url=f"{link}")]]))
    os.remove(toupload)
  except Exception as e:
    await megaupmsg.edit(f"**Error:** `{e}`")
    await send_errors(e=e)
    try:
      os.remove(toupload)
    except Exception as e:
      await send_errors(e=e)


# Import files from a public url
@Client.on_message(filters.command("import") & filters.private)
async def importurlf(client: Client, message: Message):
  if message.from_user.id not in Config.AUTH_USERS:
    await message.reply_text("**Sorry this bot isn't a Public Bot 🥺! But You can make your own bot ☺️, Click on Below Button!**", reply_markup=GITHUB_REPO)
    return
  importing_msg = await message.reply_text("`Processing ⚙️...`")
  reply_msg = message.reply_to_message
  try:
    if reply_msg:
      replied_txt_msg = reply_msg.text
      if "mega.nz" not in replied_txt_msg:
        await importing_msg.edit("Send me a **Valid Mega.nz** Link to Import 😏!")
        return
      else:
        msg_text = replied_txt_msg
    else:
      msg_txt_url = message.text
      if "mega.nz" not in msg_txt_url:
        await importing_msg.edit("Send me a **Valid Mega.nz** Link to Import 😏!")
        return
      else:
        msg_text = msg_txt_url
  except Exception as e:
    await importing_msg.edit("Hmmm... Looks like there is something other than text! Mind if check it again 🤔?")
    return
  else:
    try:
      await send_logs(user_id=message.from_user.id, mchat_id=message.chat.id, mega_url=msg_text, import_logs=True)
      import_file = m.import_public_url(msg_text)
      imported_link = m.get_upload_link(import_file)
      await importing_msg.delete()
      await message.reply_text(f"**Successfully Imported 😌** \n\n**Link:** `{imported_link}` \n\n**Powered by @NexaBotsUpdates**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📥 Imported Link 📥", url=f"{imported_link}")]]))
    except Exception as e:
      await message.reply_text(f"**Error:** `{e}`")
      await send_errors(e=e)
