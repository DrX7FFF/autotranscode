#!/usr/bin/env python
import os
import sys
import subprocess
import json
import datetime
from common import *


to_keep = {
    "common": {"index": "id", "codec_type": "type", "codec_name": "codec"},
    "video": {"resolution": "", "width": "width", "height": "height", "frame_rate": "frame_rate", "profile": "properties/profile"},
    "audio": {"language": "properties/language", "title": "properties/name", "channel": "properties/channels"},
    "subtitle": {"language": "properties/language", "title": "properties/name"}
}

def get_value(data, path):
    if isinstance(path, str):
        keys = path.split("/")
        for key in keys:
            data = data.get(key, {})
        return data if data else None
    return data.get(path)

def convert_stream(stream):
    result = {}
    
    for new_key, old_key in to_keep["common"].items():
        result[new_key] = get_value(stream, old_key)
    
    stream_type = result["codec_type"]
    if stream_type in to_keep:
        for new_key, old_key in to_keep[stream_type].items():
            result[new_key] = get_value(stream, old_key)
    
    return result

def get_media_info(filepath):
    cmd = ["mkvmerge", "-J", filepath]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)

def analyse_media(filepath):
    filestats = os.stat(filepath)
    res = {
        "size": round(filestats.st_size / (1024 * 1024), 3),
        "modif": datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "streams": []
    }
    
    media_info = get_media_info(filepath)
    if not media_info:
        print("Erreur lors de l'analyse du fichier")
        return None
    
    res["streams"] = [convert_stream(stream) for stream in media_info.get("tracks", [])]
    return res

movieslist = {}
for filename in os.listdir(moviespath):
    fullfilename = os.path.join(moviespath, filename)
    if os.path.isfile(fullfilename):
        print(fullfilename)
        res = analyse_media(fullfilename)
        if res:
            movieslist[filename] = res

db_save(movieslist,dbfilenameMKV)
