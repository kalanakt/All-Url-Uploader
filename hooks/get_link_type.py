def get_link_type(url):
    if url.endswith(('.exe', '.zip', '.mp4')):
        return 'type_direct'
    elif 'youtube' in url or 'youtu' in url:
        return 'type_youtube'
    elif 'drive.google.com' in url and '/file/d/' in url:
        return 'type_google_drive'
    elif 'mega.nz' in url and '/file/' in url:
        return 'type_mega_drive'
    elif 'onedrive.live.com' in url and '/download?' in url:
        return 'type_one_drive'
    elif 'vimeo.com' in url:
        return 'type_vimeo'
    else:
        return 'Unknown Link Type'
