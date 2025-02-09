import os
import sys
import subprocess
import json
import datetime
import csv
import re
import unicodedata
from common import *

modetest = False

if modetest:
    moviespath = "./examples"
else:
    moviespath = "/home/moi/mediaHD1/Films"

def export_to_csv(data, filename="output.csv"):
    """ Exporte une structure JSON dynamique en CSV tout en respectant l'ordre des clés. """

    # Collecter toutes les clés sans modifier l'ordre
    first_level_keys = []
    stream_keys = []

    for item in data:
        for key in item.keys():
            if key not in first_level_keys and key != "streams":
                first_level_keys.append(key)
        for stream in item.get("streams", []):
            for key in stream.keys():
                if key not in stream_keys:
                    stream_keys.append(key)

    all_keys = first_level_keys + stream_keys

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()

        for item in data:
            # Transformer les streams en un format aplati
            for stream in item.get("streams", [{}]):
                row = {key: item.get(key, "") for key in first_level_keys}
                row.update({key: stream.get(key, "") for key in stream_keys})
                writer.writerow(row)

to_keep = {
    "common":{"remove":"", "index":"index", "codec_type":"codec_type", "codec_name":"codec_name"}, 
    "video": {  "resolution":"", "width":"width", "height":"height", "frame_rate": "avg_frame_rate", "profile":"profile"}, 
    "audio": {   "language":["tags","language"], "title":["tags","title"], "channel":"channel_layout"}, 
    "subtitle": {"language":["tags","language"], "title":["tags","title"]}
    }

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
    pattern = r"\b(VFQ|AD|QUEBECOIS)\b"
    stream["remove"] = False
    match stream["codec_type"]:
        case "video":
            for r, res in resolution_map.items():
                if stream["width"]  in r:
                    stream["resolution"] = res
                else:
                    stream["resolution"] = f"{stream["width"]}x{stream["height"]}"
            if stream["codec_name"] in ["mjpeg", "png"] or stream["frame_rate"] == "0/0":
                stream["remove"] = True
        case "audio":
            if not stream["language"] in ["fre", "fra", "und", "", None]:
                stream["remove"] = True
            else:
                if stream["title"] != None:
                    match = re.findall(pattern, normalize_string(stream["title"]))
                    if match:
                        stream["remove"]=True
        case "subtitle":
            if stream["language"] != "fre" and stream["language"] != "fra" and stream["language"] != "":
                stream["remove"] = True
        case default:
            stream["remove"] = True
    return stream

def get_value(data, path):
    """ Récupère une valeur dans un dictionnaire avec un chemin (liste de clés). """
    if isinstance(path, list):
        for key in path:
            data = data.get(key, {})
        return data if data else None
    return data.get(path)

def convert_stream(stream):
    """ Filtre un stream selon les clés définies dans to_keep. """
    result = {}
    
    # Ajouter les valeurs communes
    for new_key, old_key in to_keep["common"].items():
        result[new_key] = get_value(stream, old_key)
    
    # Ajouter les valeurs spécifiques au codec_type de stream
    stream_type = result["codec_type"]
    if stream_type in to_keep:
        for new_key, old_key in to_keep[stream_type].items():
            result[new_key] = get_value(stream, old_key)
    
    return stream_treatment(result)


def get_media_info(filepath):
    """Utilise ffprobe pour récupérer les infos du fichier."""

    if modetest:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data
    
    cmd = [ "ffprobe", "-v", "quiet", "-show_format", "-show_streams", "-print_format", "json", filepath ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)

def analyse_media(filename, filepath, index):
    filestats = os.stat(filepath)

    res = {"todo":False, "fileindex":index, "filename": filename, "status":"", "comment":"", "size": int(filestats.st_size/(1024*1024))/1000, "bitrate": "", "modif": datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M"), "streams": []}

    media_info = get_media_info(filepath)
    if not media_info:
        res["comment"] = "Erreur lors de l'analyse du fichier"
        res["status"] = "Err"
        return res

    res["bitrate"] = int(int(media_info.get("format").get("bit_rate","0"))/1000)
    res["streams"] = [convert_stream(stream) for stream in media_info.get("streams", [])]
   
    ### Check video stream
    video_streams = [s for s in res["streams"] if s.get("codec_type") == "video" and not s.get("remove")]
    audio_streams = [s for s in res["streams"] if s.get("codec_type") == "audio" and not s.get("remove")]

    if filename.find("[3D]") != -1:
        res["comment"] = "Film 3D"
        res["status"] = "Ign"
    elif not video_streams:
        res["comment"] = "Pas de flux vidéo"
        res["status"] = "Err"
    elif len(video_streams) > 1:
        res["comment"] = "Plusieurs flux vidéo"
        res["status"] = "Err"
    ### Check audio stream
    elif not audio_streams:
        res["comment"] = "Pas de flux audio"
        res["status"] = "Err"
    else:
        streams_remove = [s for s in res["streams"] if s.get("remove")==True]
        if len(streams_remove) > 1:
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

filmlist = []
for filename in os.listdir(moviespath) :
    fullfilename = os.path.join(moviespath, filename)
    if os.path.isfile(fullfilename):
        print(fullfilename)
        res = analyse_media(filename, fullfilename, len(filmlist))
        filmlist.append(res)

savefilmlist(filmlistfile,filmlist)


# export_to_csv(filmlist, "/home/moi/GoogleDrive/test/checktemp.csv")
export_to_csv(filmlist, "checktemp.csv")
