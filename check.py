import os
import sys
import subprocess
import json
import datetime

separator = "|"

moviespath = "/home/moi/mediaHD1/Films"
# moviespath = "/home/moi/mediaHD1/Servarr/ToDo"
ticketpath = "/home/moi/mediaHD1/Servarr/TranscodingTickets"


def get_media_info(filepath):
    """Utilise ffprobe pour récupérer les infos du fichier."""
    cmd = [ "ffprobe", "-v", "quiet", "-show_format", "-show_streams", "-print_format", "json", filepath ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)

def analyse_media(filename, filepath):
    filestats = os.stat(filepath)

    res = {"filename": filename, "statut": "", "toencode":"No", "toclean":"No", "size": int(filestats.st_size/(1024*1024))/1000,  "resolution": "", "video_codec": "", "bitrate": "", "profile": "", "audio_codec":"", "sub":"", "comment":"", "modif": datetime.datetime.fromtimestamp(filestats.st_mtime).strftime("%d/%m/%Y %H:%M")}

    media_info = get_media_info(filepath)
    if not media_info:
        res["statut"] = "Err"
        res["comment"] = "Erreur lors de l'analyse du fichier"
        return res

    video_streams = [s for s in media_info.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams:
        res["statut"] = "Err"
        res["comment"] = "Pas de flux vidéo"
        return res
    if len(video_streams) > 1:
        res["statut"] = "Err"
        res["comment"] = "Plusieurs flux vidéo"
        return res

    ## Traitement vidéo
    # 4320p (8K) : 7 680 x 4 320.
    # 2160p (4K) : 3 840 x 2 160.
    # 1440p (2K) : 2 560 x 1 440.
    # 1080p (HD) : 1 920 x 1 080.
    # 720p (HD) : 1 280 x 7 20.
    # 480p (SD) : 854 x 480.
    # 360p (SD) : 640 x 360.
    # 240p (SD) : 426 x 240.

    width =video_streams[0].get('width', 0)
    match width:
        case 1920:
            res["resolution"] = "1080p"
        case 1280:
            res["resolution"] = "720p"
        case 854:
            res["resolution"] = "480p"
        case 640:
            res["resolution"] = "360p"
        case 426:
            res["resolution"] = "240p"
        case default:
            res["resolution"] = str(width)

    res["video_codec"] = video_streams[0].get("codec_name", "???").lower()
    res["profile"] = video_streams[0].get("profile", "???").lower()
    res["bitrate"] = int(video_streams[0].get("bit_rate", "0"))
    if res["bitrate"] == 0:
        res["bitrate"] = int(media_info.get("format").get("bit_rate","0"))
    res["bitrate"]=int(res["bitrate"]/1000)

    if res["video_codec"] == "h264" and res["resolution"] == "1080p" and res["bitrate"] > 20000:
        res["toencode"] = "Yes"

    ## Traitement audio
    audio_streams = [s for s in media_info.get("streams", []) if s.get("codec_type") == "audio"]
    frenchfound = False
    otherfound = False
    for audio_stream in audio_streams:
        tags = audio_stream.get("tags", {})
        language = tags.get("language", "???")
        languagetitle = tags.get("title", "???")
        res["audio_codec"] += f"{language}:{audio_stream.get("codec_name", "???")} "
        if language == "fre":
            frenchfound = True
        else:
            otherfound = True
    if frenchfound and otherfound:
            res["toclean"] = "Yes"

    ## traitement sous-titre
    sub_streams = [s for s in media_info.get("streams", []) if s.get("codec_type") == "subtitle"]
    for sub_stream in sub_streams:
        language = sub_stream.get("tags", {}).get("language", "???")
        res["sub"] += f"{language} "
        # if language != "fre":
        #     res["toclean"] = "Yes"

    ## conclusion
    if filename.find("[3D]") != -1:
        res["statut"] = "Ignore"
        res["comment"] = "Film 3D"
    elif res["toencode"] == "Yes":
        res["statut"] = "ToEncode"
    elif res["toclean"] == "Yes":
        res["statut"] = "ToClean"
    elif res["video_codec"] == "hevc" and res["resolution"] == "1080p":
        res["statut"]="Good"
    else:
        res["statut"]=""

    ## Génération du ticket
    # if res["statut"] == "ToEncode" or res["statut"] == "ToClean":
    if res["statut"] == "ToClean" and res['resolution'] == "1080p":
        with open(ticketpath+"/"+filename+".txt", "w") as f:
            f.write(f"action=\"{res["statut"]}\"\nfilename=\"{filename}\"\nfilepath=\"{filepath}\"\nvideo_codec=\"{res['video_codec']}\"\nresolution=\"{res['resolution']}\"\nbitrate=\"{res['bitrate']}\"\nprofile=\"{res['profile']}\"\n")

    return res

filmlist = []
for filename in os.listdir(moviespath) :
    fullfilename = os.path.join(moviespath, filename)
    if os.path.isfile(fullfilename):
        print(fullfilename)
        res = analyse_media(filename, fullfilename)
        filmlist.append(res)

with open("check.csv", "w") as f:
    if len(filmlist) > 0:
        f.write(separator.join(filmlist[0].keys())+"\n")
        for film in filmlist:
            f.write(separator.join(str(val) for val in film.values())+"\n")