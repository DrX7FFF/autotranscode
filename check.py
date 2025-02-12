#!/usr/bin/env python
import sys
import json
import re
import unicodedata
from common import *

resolution_map = {
    range(1900, 1940): '1080p',
    range(1260, 1300): '720p',
    range(834, 874): '480p',
    range(620, 660): '360p',
    range(406, 446): '240p'
}

def normalize_string(s):
    return (''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))).upper()

def stream_treatment(stream):
    resultat = {"remove": False}
    resultat.update(stream)
    pattern = r"\b(VFQ|AD|SDH|QUEBECOIS)\b"
    match resultat["codec_type"]:
        case "video":
            resultat["resolution"] = f"{resultat['width']}x{resultat['height']}"
            for r, res in resolution_map.items():
                if resultat["width"]  in r:
                    resultat["resolution"] = res
                    break
            if resultat["codec_name"] in ["mjpeg", "png"] or resultat["frame_rate"] == "0/0":
                resultat["remove"] = True
        case "audio":
            if not resultat["language"] in ["fre", "fra", "und", "mis", "", None]:
                resultat["remove"] = True
            else:
                if resultat["title"] != None:
                    match = re.findall(pattern, normalize_string(resultat["title"]))
                    if match:
                        resultat["remove"]=True
        case "subtitle":
            if not resultat["language"] in ["fre", "fra", "und", "mis", "", None]:
                resultat["remove"] = True
            else:
                if resultat["title"] != None:
                    match = re.findall(pattern, normalize_string(resultat["title"]))
                    if match:
                        resultat["remove"]=True
        case default:
            resultat["remove"] = True
    return resultat


def analyse_media(filename, moviedef):
    res = {"todo":False, "filename": filename, "status":"", "comment":"", "streams": []}
    res["streams"] = [stream_treatment(stream) for stream in moviedef["streams"]]

    ### Check video stream
    video_streams = [s for s in res["streams"] if s.get("codec_type") == "video" and not s.get("remove")]
    audio_streams = [s for s in res["streams"] if s.get("codec_type") == "audio" and not s.get("remove")]
    subtitle_streams_removed = [s for s in res["streams"] if s.get("codec_type") == "subtitle" and s.get("remove")]
    subtitle_streams_keeped = [s for s in res["streams"] if s.get("codec_type") == "subtitle" and not s.get("remove")]

    if filename.find("[3D]") != -1:
        res["status"] = "Ign"
        res["comment"] = "Film 3D"
    elif not video_streams:
        res["status"] = "Err"
        res["comment"] = "Pas de flux vidéo"
    elif len(video_streams) > 1:
        res["status"] = "Err"
        res["comment"] = "Plusieurs flux vidéo"
    ### Check audio stream
    elif not audio_streams:
        res["status"] = "Err"
        res["comment"] = "Pas de flux audio"
    elif len(subtitle_streams_removed)>0 and len(subtitle_streams_keeped)==0:
        res["status"] = "Err"
        res["comment"] = "Plus de soustitres"
    else:
        streams_remove = [s for s in res["streams"] if s.get("remove")==True]
        if len(streams_remove) > 0:
            res["comment"] = "To clean"
            res["status"] = "ToDo"
            res["todo"] = True
    # if res["video_codec"] == "h264" and res["resolution"] == "1080p" and res["bitrate"] > 20000:
    #     res["toencode"] = "Yes"


    ## conclusion

    # elif res["toencode"] == "Yes":
    #     res["statut"] = "ToEncode"
    # elif res["toclean"] == "Yes":
    #     res["statut"] = "ToClean"
    # elif res["video_codec"] == "hevc" and res["resolution"] == "1080p":
    #     res["statut"]="Good"

    ## Génération du ticket
    # if res["statut"] == "ToEncode" or res["statut"] == "ToClean":

    return res

try:
    movieslist = loadjson(dbfilename)
except:
    print("No DB, run dbupdate.py first")
    exit

todolist = []
for filename, moviedef in movieslist.items():
    todolist.append(analyse_media(filename, moviedef))

save_todo(todolist)
export_to_csv(todolist)
