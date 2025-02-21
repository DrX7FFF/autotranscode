#!/usr/bin/env python
import os
import subprocess
import json
import datetime
import re
import unicodedata
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
    "common": {"remove": [], "index": ["index"], "type": ["codec_type"]},
    "video": {},
    "audio": {"language": ["tags", "language"], "title": ["tags", "title"]},
    "subtitle": {"language": ["tags", "language"], "title": ["tags", "title"]}
}

mapping_mkvmerge = {
    "common": {"remove": [], "index": ["id"], "type": ["type"]},
    "video": {"dimension": ["properties", "pixel_dimensions"]},
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

def get_media_info(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Error get_media_info")
        return None
    return json.loads(result.stdout)

def analyse_media(filename):
    res = {
        "todo":False,
        "status": "",
        "comment": "",
        "size": None,
        "modif": None,
        "type": None,
        "streams": []
    }

    tool = "mkvmerge"
    if dockermode:
        cmd = dockercmd + mapping_cmd[tool] + [os.path.join(dockermoviespath, filename)]
    else: 
        cmd = mapping_cmd[tool] + [os.path.join(moviespath, filename)]
    
    media_info = get_media_info(cmd)

    res["type"] = get_value(media_info, ["container", "type"])
    res["streams"] = [convert_stream(stream, mapping_fields[tool]) for stream in media_info.get(mapping_streams[tool], [])]
    return res



audio_title_pattern = r"\b(" + "|".join(audio_title_remove) + r")\b"
subtitle_title_pattern = r"\b(" + "|".join(subtitle_title_remove) + r")\b"
# resolution_map = {
#     range(1900, 1940): '1080p',
#     range(1260, 1300): '720p',
#     range(834, 874): '480p',
#     range(620, 660): '360p',
#     range(406, 446): '240p'
# }

def normalize_string(s):
    return (''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))).upper()

def stream_treatment(stream):
    stream["remove"] = False
    match stream["type"]:
        # case "video":
        #     stream["resolution"] = f"{stream['width']}x{stream['height']}"
        #     for r, res in resolution_map.items():
        #         if stream["width"]  in r:
        #             stream["resolution"] = res
        #             break
        #     if stream["codec_name"] in ["mjpeg", "png"] or stream["frame_rate"] == "0/0":
        #         stream["remove"] = True
        case "audio":
            if stream["language"] in audio_language_remove:
                stream["remove"] = True
            else:
                if stream["title"] != None:
                    match = re.findall(audio_title_pattern, normalize_string(stream["title"]))
                    if match:
                        stream["remove"]=True
        case "subtitle":
            if stream["language"] in subtitle_language_remove:
                stream["remove"] = True
            else:
                if stream["title"] != None:
                    match = re.findall(subtitle_title_pattern, normalize_string(stream["title"]))
                    if match:
                        stream["remove"]=True
        # case default:
        #     stream["remove"] = True

def analyse_movie(filename, moviedef):
    if moviedef["type"] != "Matroska":
        moviedef["status"] = "Ignore"
        moviedef["comment"] = "Not MKV"
        return
    
    for stream in moviedef["streams"]:
        stream_treatment(stream)

    ### Check video stream
    video_streams = [s for s in moviedef["streams"] if s.get("type") == "video" and not s.get("remove")]
    audio_streams = [s for s in moviedef["streams"] if s.get("type") == "audio" and not s.get("remove")]
    subtitle_streams_removed = [s for s in moviedef["streams"] if s.get("type") == "subtitle" and s.get("remove")]
    subtitle_streams_keeped = [s for s in moviedef["streams"] if s.get("type") == "subtitle" and not s.get("remove")]

    if filename.find("[3D]") != -1:
        moviedef["status"] = "Ignore"
        moviedef["comment"] = "3D Movie"
    elif not video_streams:
        moviedef["status"] = "Error"
        moviedef["comment"] = "Pas de flux vidéo"
    elif len(video_streams) > 1:
        moviedef["status"] = "Error"
        moviedef["comment"] = "Plusieurs flux vidéo"
    elif not video_streams[0]["dimension"].startswith("1920x"):
        moviedef["status"] = "ToDownload"
        moviedef["comment"] = "Bad resoltion"
    elif not audio_streams:
        moviedef["status"] = "Error"
        moviedef["comment"] = "Pas de flux audio"
    elif len(subtitle_streams_removed)>0 and len(subtitle_streams_keeped)==0:
        moviedef["status"] = "Error"
        moviedef["comment"] = "Plus de soustitres"
    else:
        streams_remove = [s for s in moviedef["streams"] if s.get("remove")==True]
        if len(streams_remove) > 0:
            moviedef["status"] = "ToDo"
            moviedef["comment"] = "To clean"
            moviedef["todo"] = True
        else:
            moviedef["status"] = ""
            moviedef["comment"] = ""
    # if res["video_codec"] == "h264" and res["resolution"] == "1080p" and res["bitrate"] > 20000:
    #     res["toencode"] = "Yes"
    # elif res["video_codec"] == "hevc" and res["resolution"] == "1080p":
    #     res["statut"]="Good"

def check_files(movieslist,moviespath):
    moviesremoved = list(movieslist.keys())

    for filename in os.listdir(moviespath):
        filenamepath = os.path.join(moviespath, filename)
        if os.path.isfile(filenamepath):
            todo = False
            filestats = os.stat(filenamepath)
            filesize = round(filestats.st_size / (1024 * 1024), 3)
            filedate = datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M")

            if filename in movieslist.keys():
                moviesremoved.remove(filename)
                if filesize != movieslist[filename]["size"] or filedate != movieslist[filename]["modif"]:
                    print(f"{filename} changed")
                    todo = True
            else:
                todo = True
            if todo:
                movieslist[filename] = analyse_media(filename)
                movieslist[filename]["size"] = filesize
                movieslist[filename]["modif"] = filedate

    for name in moviesremoved:
        print(f"Remove {name}")
        del movieslist[name]


### MAIN
# Chargement de la base
movieslist = loadjson(allfilename,{})

# Scan du dossier
check_files(movieslist,moviespath)

# Analyse des fichiers
for filename, moviedef in movieslist.items():
    analyse_movie(filename, moviedef)
    # moviedef = analyse_movie(filename, moviedef)
    # if moviedef:
    #     movieslist[filename] = moviedef

# with open("movieslist_ffprobe.json", "w") as f:
#     json.dump(movieslist_ffprobe, f, indent=4)

save_todo(movieslist,allfilename)

todolist = {}
for filename, moviedef in movieslist.items():
    if moviedef["todo"]:
        todolist[filename] = moviedef
save_todo(todolist,todofilename)

errorlist = {}
for filename, moviedef in movieslist.items():
    if moviedef["status"] != "":
        errorlist[filename] = moviedef
save_todo(errorlist,errorfilename)
