from os import remove as osremove, path as ospath, walk
from json import loads as jsnloads
from subprocess import run as srun, check_output
from math import ceil

VIDEO_SUFFIXES = ("M4V", "MP4", "MOV", "FLV", "WMV", "3GP", "MPG", "WEBM", "MKV", "AVI")
TG_SPLIT_SIZE = 2097151000
EQUAL_SPLITS = False

def get_media_info(path):
    try:
        result = check_output(["./ffmpeg/ffprobe", "-hide_banner", "-loglevel", "error", "-print_format",
                                          "json", "-show_format", path]).decode('utf-8')
        fields = jsnloads(result)['format']
    except Exception as e:
        print(f"get_media_info: {e}")
        return 0, None, None
    try:
        duration = round(float(fields['duration']))
    except:
        duration = 0
    try:
        artist = str(fields['tags']['artist'])
    except:
        artist = None
    try:
        title = str(fields['tags']['title'])
    except:
        title = None
    return duration, artist, title
    
def get_path_size(path: str):
    if ospath.isfile(path):
        return ospath.getsize(path)
    total_size = 0
    for root, dirs, files in walk(path):
        for f in files:
            abs_path = ospath.join(root, f)
            total_size += ospath.getsize(abs_path)
    return total_size    

def split_file(path, size, file_, dirpath, split_size, start_time=0, i=1, inLoop=False):
    parts = ceil(size/TG_SPLIT_SIZE)
    flist = []
    if EQUAL_SPLITS and not inLoop:
        split_size = ceil(size/parts) + 1000
    if file_.upper().endswith(VIDEO_SUFFIXES):
        base_name, extension = ospath.splitext(file_)
        split_size = split_size - 2500000
        while i <= parts :
            parted_name = "{}.part{}{}".format(str(base_name), str(i).zfill(3), str(extension))
            out_path = ospath.join(dirpath, parted_name)
            srun(["./ffmpeg/ffmpeg", "-hide_banner", "-loglevel", "error", "-i",
                            path, "-ss", str(start_time), "-fs", str(split_size),
                            "-async", "1", "-strict", "-2", "-c", "copy", out_path])
            out_size = get_path_size(out_path)
            if out_size > 2097152000:
                dif = out_size - 2097152000
                split_size = split_size - dif + 2500000
                osremove(out_path)
                return split_file(path, size, file_, dirpath, split_size, start_time, i, inLoop=True)
            lpd = get_media_info(out_path)[0]
            if lpd <= 4 or out_size < 1000000:
                osremove(out_path)
                break
            start_time += lpd - 3
            i = i + 1
            flist.append(out_path)
    else:
        out_path = ospath.join(dirpath, file_ + ".")
        srun(["split", "--numeric-suffixes=1", "--suffix-length=3", f"--bytes={split_size}", path, out_path])
        flist.append(out_path)
    print(flist)   
    return flist 
    

