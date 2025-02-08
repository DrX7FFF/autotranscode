import os
import sys
import subprocess
import json
import datetime
import csv

modetest = False

if modetest:
    moviespath = "./examples"
else:
    moviespath = "/home/moi/mediaHD1/Films"
# moviespath = "/home/moi/mediaHD1/Servarr/ToDo"
ticketpath = "/home/moi/mediaHD1/Servarr/TranscodingTickets"

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
    "common":{"index":"index", "remove":"", "type":"codec_type", "codec":"codec_name"}, 
    "video": {  "resolution":"width", "frame_rate": "avg_frame_rate", "profile":"profile"}, 
    "audio": {   "language":["tags","language"], "title":["tags","title"], "channel":"channel_layout"}, 
    "subtitle": {"language":["tags","language"], "title":["tags","title"]}
    }

# def filtrer_json(data):
#     tokeep = ["index", "codec_type", "codec_name", "codec_long_name"] 
#     if data["codec_type"] in to_keep.keys():
#         tokeep += to_keep[data["codec_type"]]
#     res = {k: v for k, v in data.items() if k in tokeep}
#     return res

    ## Traitement vidéo
    # 4320p (8K) : 7 680 x 4 320.
    # 2160p (4K) : 3 840 x 2 160.
    # 1440p (2K) : 2 560 x 1 440.
    # 1080p (HD) : 1 920 x 1 080.
    # 720p (HD) : 1 280 x 7 20.
    # 480p (SD) : 854 x 480.
    # 360p (SD) : 640 x 360.
    # 240p (SD) : 426 x 240.

resolution_map = {
    range(1900, 1940): '1080p',
    range(1260, 1300): '720p',
    range(834, 874): '480p',
    range(620, 660): '360p',
    range(406, 446): '240p'
}

def stream_treatment(stream):
    match stream["type"]:
        case "video":
            if stream["frame_rate"] == "0/0":
                stream["remove"] = True
            else:
                for r, res in resolution_map.items():
                    if stream["resolution"]  in r:
                        stream["resolution"] = res
        case "audio":
            if not stream["language"] in ["fre", "fra","", None]:
                stream["remove"] = True
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

def filter_stream(stream):
    """ Filtre un stream selon les clés définies dans to_keep. """
    result = {}
    
    # Ajouter les valeurs communes
    for new_key, old_key in to_keep["common"].items():
        result[new_key] = get_value(stream, old_key)
    
    # Ajouter les valeurs spécifiques au type de stream
    stream_type = result["type"]
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

def analyse_media(filename, filepath):
    filestats = os.stat(filepath)

    res = {"filename": filename, "comment":"", "size": int(filestats.st_size/(1024*1024))/1000, "bitrate": "", "modif": datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M"), "streams": []}

    media_info = get_media_info(filepath)
    if not media_info:
        res["comment"] = "Erreur lors de l'analyse du fichier"
        return res

    streams = media_info.get("streams", [])
    res["streams"] = [filter_stream(stream) for stream in streams]
    

    video_streams = [s for s in res["streams"] if s.get("type") == "video"]
    if not video_streams:
        res["comment"] = "Pas de flux vidéo"
        return res
    if len(video_streams) > 1:
        res["comment"] = "Plusieurs flux vidéo"
        return res

    res["bitrate"] = int(video_streams[0].get("bit_rate", "0"))
    if res["bitrate"] == 0:
        res["bitrate"] = int(media_info.get("format").get("bit_rate","0"))
    res["bitrate"]=int(res["bitrate"]/1000)

    # if res["video_codec"] == "h264" and res["resolution"] == "1080p" and res["bitrate"] > 20000:
    #     res["toencode"] = "Yes"

    ## Traitement audio
    # audio_streams = [s for s in media_info.get("streams", []) if s.get("codec_type") == "audio"]
    # frenchfound = False
    # otherfound = False
    # for audio_stream in audio_streams:
    #     if language == "fre":
    #         frenchfound = True
    #     else:
    #         otherfound = True
    # if frenchfound and otherfound:
    #         res["toclean"] = "Yes"

    ## conclusion
    if filename.find("[3D]") != -1:
        res["comment"] = "Film 3D"
    # elif res["toencode"] == "Yes":
    #     res["statut"] = "ToEncode"
    # elif res["toclean"] == "Yes":
    #     res["statut"] = "ToClean"
    # elif res["video_codec"] == "hevc" and res["resolution"] == "1080p":
    #     res["statut"]="Good"

    ## Génération du ticket
    # if res["statut"] == "ToEncode" or res["statut"] == "ToClean":
    # if res["statut"] == "ToClean" and res['resolution'] == "1080p":
    #     with open(ticketpath+"/"+filename+".txt", "w") as f:
    #         f.write(f"action=\"{res["statut"]}\"\nfilename=\"{filename}\"\nfilepath=\"{filepath}\"\nvideo_codec=\"{res['video_codec']}\"\nresolution=\"{res['resolution']}\"\nbitrate=\"{res['bitrate']}\"\nprofile=\"{res['profile']}\"\n")

    return res

filmlist = []
for filename in os.listdir(moviespath) :
    fullfilename = os.path.join(moviespath, filename)
    if os.path.isfile(fullfilename):
        print(fullfilename)
        res = analyse_media(filename, fullfilename)
        filmlist.append(res)

# print(json.dumps(filmlist, indent=2, ensure_ascii=False))
with open("check.json", 'w') as file:
    json.dump(filmlist, file, indent=2, ensure_ascii=False)

export_to_csv(filmlist, "checktemp.csv")
