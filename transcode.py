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

def run_cmd(command):
    res = {"msg": [], "rc": None}
    # errors_detected = False  # Flag global pour arrêter ffmpeg après avoir tout lu

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    for line in iter(process.stdout.readline, ''):  # Lire stderr en continu
        line = line.strip()
        if line:
            if "%" in line:  # Progression
                sys.stdout.write("\r" + line)
                sys.stdout.flush()
            else:  # Autres messages
                print(f"{line}", file=sys.stderr)
                res["msg"].append(line)  # Stocker l'erreur

    # while process.poll() is None:  # Tant que le processus tourne
    #     # Lire stdout et stderr en parallèle
    #     ready, _, _ = select.select([process.stdout, process.stderr], [], [], 30) # timeout de 30 secondes
    #     for stream in ready:
    #         for line in iter(stream.readline, ''):  # Lire tout ce qui est dispo
    #             line = line.strip()
    #             if not line:
    #                 continue

    #             if stream == process.stderr:
    #                 print(f"❌ Erreur détectée : #{line}#", file=sys.stderr)
    #                 res.append(line)  # Stocker l'erreur
    #                 # errors_detected = True  # Marquer qu'une erreur a été détectée

    #             elif stream == process.stdout:
    #                 if "%" in line:  # Détection de la progression de mkvmerge
    #                     sys.stdout.write(line)
    #                 else:
    #                     sys.stdout.write(line +'\n')
    #                     res.append(line)
    #     sys.stdout.flush()
        # if errors_detected:  # Vérifier après avoir tout traité dans cette itération
        #     process.terminate()  # Stoppe ffmpeg une fois qu'on a bien tout lu

    # while process.poll() is None:  # Tant que le processus tourne
    #     ready, _, _ = select.select([process.stdout], [], [], 30) # timeout de 30 secondes
    #     for stream in ready:
    #         for line in iter(stream.readline, ''):  # Lire tout ce qui est dispo
    #             line = line.strip()
    #             if not line:
    #                 continue

    #             if "%" in line:  # Détection de la progression de mkvmerge
    #                 sys.stdout.write(line)
    #             else:
    #                 sys.stdout.write(line +'\n')
    #                 res.append(line)
    #     sys.stdout.flush()
    process.wait()
    res["rc"] = process.returncode
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
        filtervideo=[]
        filteraudio=[]
        filtersubtitle=[]
        # --audio-tracks
        for stream in film["streams"]:
            if stream["remove"]:
                match stream["type"]:
                    case "video":
                        filtervideo.append(str(stream['index']))
                    case "audio":
                        filteraudio.append(str(stream['index']))
                    case "subtitle":
                        filtersubtitle.append(str(stream['index']))

        cmd = [ "mkvmerge", "-o", outfile, "--no-attachments", "--abort-on-warnings", "--flush-on-close" ]
        if len(filtervideo)>0:
            cmd.append("--video-tracks")
            cmd.append('!'+','.join(filtervideo))
        if len(filteraudio)>0:
            cmd.append("--audio-tracks")
            cmd.append('!'+','.join(filteraudio))
        if len(filtersubtitle)>0:
            cmd.append("--subtitle-tracks")
            cmd.append('!'+','.join(filtersubtitle))
        cmd.append(infile)

        logmessage("INFO", ' '.join(cmd))

        res = run_cmd(cmd)

        if res["rc"] != 0:
            logmessage("ERROR", "Return code : "+str(res["rc"]))
            for msg in res["msg"]:
                logmessage("INFO", msg)
            os.remove(outfile)
            film["comment"]="Error durring processing"
        else:
            sizebefore = os.stat(infile).st_size
            sizeafter = os.stat(outfile).st_size
            gain = int((sizeafter - sizebefore)/(1024*1024))/1000
            shutil.move(outfile, infile)
            duration = divmod((dt.datetime.now() - begindt).seconds, 60)
            logmessage("INFO", f"gain={gain} Go / duration={duration}")
            film["comment"]="Done :-)"

        film["todo"]=False
        save_todo(todolist)
        logmessage("INFO", "---------------------------------------")
        if count >=maxiter :
            break
logmessage("INFO", ">>>> End")
