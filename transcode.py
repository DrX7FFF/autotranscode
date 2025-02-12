# import json
import datetime as dt
import subprocess
import sys
import os
import shutil
import select
from common import *
import time

temppath="/home/moi/mediaHD1/Servarr/Transcoding"
logfile="log.txt"

def logmessage(level, message):
    with open(logfile, 'a') as file:
        file.write(f"{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [{level}] {message}\n")

def run_ffmpeg(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    errors = []
    # Lire stdout et stderr en parallèle
    while process.poll() is None:  # Tant que le processus tourne
        ready, _, _ = select.select([process.stdout, process.stderr], [], [])

        for stream in ready:
            line = stream.readline().strip()  # Lire une ligne dispo

            if stream == process.stderr:
                if len(line)>0:
                    print(f"\n❌ Erreur détectée : #{line}#", file=sys.stderr)
                    errors.append(line)  # Stocker l'erreur
                    process.terminate()  # Arrêter immédiatement ffmpeg
                    # process.wait()  # Attendre la fin complète du processus avant de quitter
                    # sys.stdout.flush()  # Forcer l'affichage de tout le buffer stdout
            elif stream == process.stdout:
                code = line.partition('=')[0]
                if code == "progress":
                    sys.stdout.write('          \r')
                elif code in ["out_time","dup_frames","drop_frames","speed"]:
                    sys.stdout.write(line + ' ')  # Afficher stdout en direct

        sys.stdout.flush()
        time.sleep(0.01)  # Évite de surcharger la boucle
    print("\r\n")
    return errors

### Begin
logmessage("INFO", ">>>> Begin")
todolist = loadjson(todo_file)

count = 0
for film in todolist:
    if film["todo"] :
        count += 1

        begindt = dt.datetime.now()
        logmessage("INFO", film['filename'])
        print(f"{film['filename']}")

        infile=moviespath+"/"+film["filename"]
        outfile=temppath+"/"+film["filename"]
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
        # "-stats",
        # "-t", "30",
        # , "-progress", "pipe:1"
        # "-hide_banner", 
        cmd = ["ffmpeg", "-y", "-loglevel", "warning", "-progress", "pipe:1"] + cmd_extra + ["-i", infile, "-map_metadata", "0", "-map_chapters", "0", "-map", "0"] + mapfilter + [ "-c:v", "copy", "-c:a", "copy", "-c:s", "copy", outfile]
        logmessage("INFO", ' '.join(cmd))
        errors = run_ffmpeg(cmd)
        if len(errors)>0:
            for errmsg in errors:
                logmessage("ERROR", errmsg)
            os.remove(outfile)
            film["todo"]=False
            film["comment"]="Error durring processing"
        else:
            sizebefore = os.stat(infile).st_size
            sizeafter = os.stat(outfile).st_size
            gain = int((sizeafter - sizebefore)/(1024*1024))/1000
            shutil.move(outfile, infile)
            duration = divmod((dt.datetime.now() - begindt).seconds, 60)
            logmessage("INFO", f"gain={gain} Go duration={duration}")
            film["todo"]=False
            film["comment"]="Done :-)"

        save_todo(todolist)
        logmessage("INFO", "---------------------------------------")
        if count >=20 :
            break
logmessage("INFO", ">>>> End")
