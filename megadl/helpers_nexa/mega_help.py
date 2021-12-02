import math
import os
import time

from megadl import meganzbot as client
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config


# Credits: SpEcHiDe's AnyDL-Bot for Progress bar
async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \n**Process**: {2}%\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\n**Speed:** {2}/s\n**ETA:** {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n {} \n\n**Powered by @NexaBotsUpdates**".format(
                    ud_type,
                    tmp
                )
            )
        except:
            pass


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


# Checking log channel
def check_logs():
    if Config.LOGS_CHANNEL != -1234567:
        c_info = client.get_chat(chat_id=Config.LOGS_CHANNEL)
        if c_info.type != "channel":
            print(ERROR_TEXT.format("Chat is not a channel"))
            return
        elif c_info.username is not None:
            print(ERROR_TEXT.format("Chat is not private"))
            return
        else:
            client.send_message(chat_id=Config.LOGS_CHANNEL, text="`Mega.nz-Bot has Successfully Started!` \n\n**Powered by @NexaBotsUpdates**")
    else:
        print("No Log Channel ID is Given. Anyway I'm Trying to Start!")
        pass


# Send Download or Upload logs in log channel
async def send_logs(user_id, mchat_id, up_file=None, mega_url=None, download_logs=False, upload_logs=False, import_logs=False):
    # Log type
    download_logs = download_logs
    upload_logs = upload_logs
    import_logs = import_logs
    # Things needed to send logs
    mega_url = mega_url
    up_file = up_file
    if download_logs is True:
        try:
            if Config.LOGS_CHANNEL != -1234567:
                await client.send_message(chat_id=Config.LOGS_CHANNEL, text=f"**#DOWNLOAD_LOG** \n\n**User ID:** `{user_id}` \n**Chat ID:** `{mchat_id}` \n**Url:** {mega_url}")
            else:
                print(f"DOWNLOAD_LOG \nUser ID: {user_id} \n\nChat ID: {mchat_id} \nUrl: {mega_url}")
        except Exception as e:
            await send_errors(e=e)
    elif upload_logs is True:
        try:
            if Config.LOGS_CHANNEL != -1234567:
                if up_file is not None:
                    gib_details = await up_file.forward(Config.LOGS_CHANNEL)
                    await gib_details.reply_text(f"**#UPLOAD_LOG** \n\n**User ID:** `{user_id}` \n**Chat ID:** `{mchat_id}`")
                elif mega_url is not None:
                    await client.send_message(chat_id=Config.LOGS_CHANNEL, text=f"**#UPLOAD_LOG** \n\n**User ID:** `{user_id}` \n**Chat ID:** `{mchat_id}` \n**Url:** {mega_url}")
            else:
                if up_file is not None:
                    print(f"UPLOAD_LOG \nUser ID: {user_id} \n\nChat ID: {mchat_id}")
                elif mega_url is not None:
                    print(f"UPLOAD_LOG \nUser ID: {user_id} \n\nChat ID: {mchat_id} \nUrl: {mega_url}")
        except Exception as e:
            await send_errors(e=e)
    elif import_logs is True:
        try:
            if Config.LOGS_CHANNEL != -1234567:
                await client.send_message(chat_id=Config.LOGS_CHANNEL, text=f"**#IMPORT_LOG** \n\n**User ID:** `{user_id}` \n**Chat ID:** `{mchat_id}` \n**Origin Url:** {mega_url}")
            else:
                print(f"IMPORT_LOG \nUser ID: {user_id} \n\nChat ID: {mchat_id} \nOrigin Url: {mega_url}")
        except Exception as e:
            await send_errors(e=e)

# Send or print errors
async def send_errors(e):
    if Config.LOGS_CHANNEL != -1234567:
        await client.send_message(Config.LOGS_CHANNEL, f"**#Error** \n`{e}`")
    else:
        print(ERROR_TEXT.format(e))
