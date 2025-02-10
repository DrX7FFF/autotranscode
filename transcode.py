# import json
import datetime as dt
import subprocess
import os
import shutil
from common import *

inpath="/home/moi/mediaHD1/Films"
outpath="/home/moi/mediaHD1/Servarr/Transcoding"
logfile="log.txt"

def logmessage(level, message):
    with open(logfile, 'a') as file:
        file.write(f"{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [{level}] {message}\n")

def run_ffmpeg(command):
    errorcount = 0
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        # Afficher l'avancement ou les informations pertinentes
        print(line.strip())
        logmessage("INFO", line.strip())

    # Capturer les erreurs si nécessaire
    for line in process.stderr:
        print(line.strip())
        logmessage("ERROR", line.strip())
        errorcount +=1

    process.wait()  # Attendre la fin du processus
    return errorcount

logmessage("INFO", ">>>> Begin")
filmlist = loadfilmlist(filmlistfile)

count = 0
for film in filmlist:
    if film["todo"] :
        count += 1

        begindt = dt.datetime.now()
        logmessage("INFO", film['filename'])
        print(f"{film['filename']}")

        infile=inpath+"/"+film["filename"]
        outfile=outpath+"/"+film["filename"]
        mapfilter=[]
        for stream in film["streams"]:
            if stream["remove"]:
                # print(json.dumps(stream, ensure_ascii=False))
                mapfilter.append("-map")
                mapfilter.append(f"-0:{stream['index']}")

        has_pgs_subtitles = any(
            stream.get("codec_type") == "subtitle" and stream.get("codec_name") == "hdmv_pgs_subtitle"
            for stream in film["streams"])
        if has_pgs_subtitles:
            cmd_extra = ["-analyzeduration", "2000M", "-probesize", "4000M"]
        else:
            cmd_extra = []
        
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning"] + cmd_extra + ["-i", infile, "-map_metadata", "0", "-map_chapters", "0", "-map", "0"] + mapfilter + [ "-c:v", "copy", "-c:a", "copy", "-c:s", "copy", outfile]
        # print(cmd)
        logmessage("INFO", ' '.join(cmd))
        errorcount = run_ffmpeg(cmd)
        if errorcount>0:
            logmessage("ERROR", "Abandon conversion")
            os.remove(outfile)
        else:
            sizebefore = os.stat(infile).st_size
            sizeafter = os.stat(outfile).st_size
            shutil.move(outfile, infile)

            gain = int((sizeafter - sizebefore)/(1024*1024))/1000

            duration = divmod((dt.datetime.now() - begindt).seconds, 60)
            logmessage("INFO", f"gain={gain}Mo duration={duration}")
            logmessage("INFO", "---------------------------------------")
            film["todo"]=False
            film["comment"]="Cleaned"
            savefilmlist(filmlistfile,filmlist)

        if count >=5 :
            break
logmessage("INFO", ">>>> End")
