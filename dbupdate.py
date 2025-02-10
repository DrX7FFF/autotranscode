import os
import sys
import subprocess
import json
import datetime
from common import *


to_keep = {
    "common":{"index":"index", "codec_type":"codec_type", "codec_name":"codec_name"}, 
    "video": {  "resolution":"", "width":"width", "height":"height", "frame_rate": "avg_frame_rate", "profile":"profile"}, 
    "audio": {   "language":["tags","language"], "title":["tags","title"], "channel":"channel_layout"}, 
    "subtitle": {"language":["tags","language"], "title":["tags","title"]}
    }

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
    
    return result


def get_media_info(filepath):
    """Utilise ffprobe pour récupérer les infos du fichier."""

    cmd = [ "ffprobe", "-v", "quiet", "-show_format", "-show_streams", "-print_format", "json", filepath ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)

def analyse_media(filepath):
    filestats = os.stat(filepath)

    res = {"size": int(filestats.st_size/(1024*1024))/1000, "modif": datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M"), "bitrate": "", "streams": []}

    media_info = get_media_info(filepath)
    if not media_info:
        print ("Erreur lors de l'analyse du fichier")
        return None

    res["bitrate"] = int(int(media_info.get("format").get("bit_rate","0"))/1000)
    res["streams"] = [convert_stream(stream) for stream in media_info.get("streams", [])]
   
    return res

movieslist = {}
for filename in os.listdir(moviespath) :
    fullfilename = os.path.join(moviespath, filename)
    if os.path.isfile(fullfilename):
        print(fullfilename)
        res = analyse_media(fullfilename)
        if res:
            movieslist[filename] = res

db_save(movieslist)