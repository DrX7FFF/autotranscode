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
    "audio": {"language": ["tags", "language"], "title": ["tags", "title"]},
    "subtitle": {"language": ["tags", "language"], "title": ["tags", "title"]}
}

mapping_mkvmerge = {
    "common": {"index": ["id"], "type": ["type"]},
    "video": {},
    "audio": {"language": ["properties", "language"], "title": ["properties", "track_name"]},
    "subtitle": {"language": ["properties", "language"], "title": ["properties", "track_name"]}
}

mapping_fields = {  "ffprobe": mapping_ffprobe, 
                    "mkvmerge": mapping_mkvmerge}

mapping_cmd = {     "ffprobe": ["ffprobe", "-v", "error", "-show_streams", "-print_format", "json"], 
                    "mkvmerge": ["mkvmerge", "-J"]}

mapping_streams = { "ffprobe": "streams", 
                    "mkvmerge": "tracks"}

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

def get_media_info(filepath,cmd):
    cmdloc = cmd.copy()
    cmdloc.append(filepath)
    result = subprocess.run(cmdloc, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Error get_media_info")
        return None
    return json.loads(result.stdout)

def analyse_media(filepath):
    filestats = os.stat(filepath)
    res = {
        "size": round(filestats.st_size / (1024 * 1024), 3),
        "modif": datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "type": None
    }
    tool = "mkvmerge"
    media_info = get_media_info(filepath, mapping_cmd[tool])
    res["type"] = get_value(media_info, ["container", "type"])

    # if media_info:
    res["streams"] = [convert_stream(stream, mapping_fields[tool]) for stream in media_info.get(mapping_streams[tool], [])]
    return res

movieslist = {}

for filename in os.listdir(moviespath):
    fullfilename = os.path.join(moviespath, filename)
    if os.path.isfile(fullfilename):
        print(fullfilename)
        # movieslist_ffprobe[filename] = analyse_media(fullfilename, "ffprobe")
        movieslist[filename] = analyse_media(fullfilename)
        
# with open("movieslist_ffprobe.json", "w") as f:
#     json.dump(movieslist_ffprobe, f, indent=4)

db_save(movieslist)
