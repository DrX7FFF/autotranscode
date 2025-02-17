#!/usr/bin/env python
# import json
import datetime as dt
import subprocess
import sys
import os
import shutil
import select
import time
from common import *

def logmessage(level, message):
    with open(logfile, 'a') as file:
        file.write(f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}\n")

def run_ffmpeg(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    res = {"errors":[], "dup_frames":"", "drop_frames":"", "speed":""}
    errors_detected = False  # Flag global pour arrêter ffmpeg après avoir tout lu

    while process.poll() is None:  # Tant que le processus tourne
        # Lire stdout et stderr en parallèle
        ready, _, _ = select.select([process.stdout, process.stderr], [], [], 30) # timeout de 30 secondes
        for stream in ready:
            for line in iter(stream.readline, ''):  # Lire tout ce qui est dispo
                line = line.strip()
                if not line:
                    continue

                if stream == process.stderr:
                    print(f"\n❌ Erreur détectée : #{line}#", file=sys.stderr)
                    res["errors"].append(line)  # Stocker l'erreur
                    errors_detected = True  # Marquer qu'une erreur a été détectée

                elif stream == process.stdout:
                    code = line.partition('=')
                    if code[0] == "progress":
                        sys.stdout.write('          \r')
                    elif code[0] in ["out_time","dup_frames","drop_frames","speed"]:
                        sys.stdout.write(line + ' ')  # Afficher stdout en direct
                        res[code[0]] = code[2]

        sys.stdout.flush()
        if errors_detected:  # Vérifier après avoir tout traité dans cette itération
            process.terminate()  # Stoppe ffmpeg une fois qu'on a bien tout lu

    print("\r\n")
    return res

### Begin
if len(sys.argv)>1 :
    maxiter = int(sys.argv[1])
else:
    maxiter = 1

logmessage(f"INFO", ">>>> Begin for {maxiter} iter")
todolist = loadjson(todofilename)

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
        cmd = [
                "ffmpeg", "-y", "-loglevel", "warning", "-progress", "pipe:1", "-stats_period", "2"
                ] + cmd_extra + [
                "-i", infile, 
                "-map_metadata", "0", "-map_chapters", "0", "-map", "0"
                ] + mapfilter + [
                "-c:v", "copy", 
                "-c:a", "copy", 
                "-c:s", "copy", 
                outfile
            ]
        logmessage("INFO", ' '.join(cmd))
        res = run_ffmpeg(cmd)
        ["out_time","dup_frames","drop_frames","speed"]
        logmessage("INFO", f"speed={res['speed']} / dup_frames={res['dup_frames']} / drop_frames={res['drop_frames']}")
        if len(res["errors"])>0:
            for errmsg in res["errors"]:
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
        if count >=maxiter :
            break
logmessage("INFO", ">>>> End")
