#!/usr/bin/env python
import os
import subprocess
import json
import datetime
from common import *

# Mapping des clés pour chaque outil sous format homogène
# mapping_ffprobe = {
#     "common": {"index": ["index"], "type": ["codec_type"], "codec_name": ["codec_name"]},
#     "video": {"resolution": [], "width": ["width"], "height": ["height"], "frame_rate": ["avg_frame_rate"], "profile": ["profile"]},
#     "audio": {"language": ["tags", "language"], "title": ["tags", "title"], "channel": ["channel_layout"]},
#     "subtitle": {"language": ["tags", "language"], "title": ["tags", "title"]}
# }

# mapping_mkvmerge = {
#     "common": {"index": ["id"], "type": ["type"], "codec_name": ["codec"]},
#     "video": {"resolution": [], "width": ["properties", "width"], "height": ["properties", "height"], "frame_rate": ["properties", "frame_rate"], "profile": ["properties", "profile"]},
#     "audio": {"language": ["properties", "language_ietf"], "title": ["properties", "name"], "channel": ["properties", "channels"]},
#     "subtitle": {"language": ["properties", "language_ietf"], "title": ["properties", "name"]}
# }
mapping_ffprobe = {
    "common": {"index": ["index"], "type": ["codec_type"]},
    "video": {},
    "audio": {"language": ["tags", "language"], "title": ["tags", "title"], "channel": ["channel_layout"]},
    "subtitle": {"language": ["tags", "language"], "title": ["tags", "title"]}
}

mapping_mkvmerge = {
    "common": {"index": ["id"], "type": ["type"]},
    "video": {},
    "audio": {"language": ["properties", "language"], "title": ["properties", "track_name"], "channel": ["properties", "channels"]},
    "subtitle": {"language": ["properties", "language"], "title": ["properties", "track_name"]}
}

def get_value(data, path):
    res = None
    for key in path:
        if res is None:
            res = data
        res = res.get(key, None)
    return res

def convert_stream(stream, mapping):
    result = {}
    
    for new_key, old_key in mapping["common"].items():
        result[new_key] = get_value(stream, old_key)
    if result["type"] == "subtitles":
        result["type"] = "subtitle"
    
    stream_type = result["type"]
    if stream_type in mapping:
        for new_key, old_key in mapping[stream_type].items():
            result[new_key] = get_value(stream, old_key)
    
    return result

def get_media_info_ffprobe(filepath):
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-print_format", "json", filepath]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Error FFProbe")
        return None
    return json.loads(result.stdout)

def get_media_info_mkvmerge(filepath):
    cmd = ["mkvmerge", "-J", filepath]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Error MKV")
        return None
    return json.loads(result.stdout)

def analyse_media(filepath, tool):
    filestats = os.stat(filepath)
    res = {
        "size": round(filestats.st_size / (1024 * 1024), 3),
        "modif": datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "streams": []
    }
    
    if tool == "ffprobe":
        media_info = get_media_info_ffprobe(filepath)
        if media_info:
            res["streams"] = [convert_stream(stream, mapping_ffprobe) for stream in media_info.get("streams", [])]
    elif tool == "mkvmerge":
        media_info = get_media_info_mkvmerge(filepath)
        if media_info:
            res["streams"] = [convert_stream(stream, mapping_mkvmerge) for stream in media_info.get("tracks", [])]
            if len(media_info.get("warnings", [])) > 0:
                print(media_info.get("warnings", []))
    
    return res

movieslist_ffprobe = {}
movieslist_mkvmerge = {}

for filename in os.listdir(moviespath):
    fullfilename = os.path.join(moviespath, filename)
    if os.path.isfile(fullfilename):
        print(fullfilename)
        movieslist_ffprobe[filename] = analyse_media(fullfilename, "ffprobe")
        movieslist_mkvmerge[filename] = analyse_media(fullfilename, "mkvmerge")
        
with open("movieslist_ffprobe.json", "w") as f:
    json.dump(movieslist_ffprobe, f, indent=4)

with open("movieslist_mkvmerge.json", "w") as f:
    json.dump(movieslist_mkvmerge, f, indent=4)
