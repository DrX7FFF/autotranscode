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
            else:  # Autres messages
                print(line)
                res["msg"].append(line)  # Stocker l'erreur
            sys.stdout.flush()
 
    process.wait()
    res["rc"] = process.returncode
    return res

### Begin
if len(sys.argv)>1 :
    maxiter = int(sys.argv[1])
else:
    maxiter = 1

logmessage(f"INFO", f">>>> Begin for {maxiter} iter")
todolist = loadjson(todofilename)

for film in todolist:
    if film["todo"] :
        logmessage("INFO", film['filename'])

        sourcefilepath = os.path.join(moviespath, film['filename'])
        tempfilepath = os.path.join(temppath, "temp.mkv")

        sizebefore = os.stat(sourcefilepath).st_size

        # Check file size
        if dockermode:
            sourcefilepathcmd = os.path.join(dockermoviespath, film['filename'])
            if sizebefore > fastsize*1024*1024:
                logmessage("INFO", "HD temp file")
                tempfilepathcmd = os.path.join(dockertemppath, "temp.mkv")
            else:
                logmessage("INFO", "OS temp file")
                tempfilepathcmd = os.path.join(dockerfasttemppath, "temp.mkv")
                tempfilepath = os.path.join(fasttemppath, "temp.mkv")
        else:
            sourcefilepathcmd = sourcefilepath
            tempfilepathcmd = tempfilepath
        
        # Build cmd
        filtervideo=[]
        filteraudio=[]
        filtersubtitle=[]
        for stream in film["streams"]:
            if stream["remove"]:
                match stream["type"]:
                    case "video":
                        filtervideo.append(str(stream['index']))
                    case "audio":
                        filteraudio.append(str(stream['index']))
                    case "subtitle":
                        filtersubtitle.append(str(stream['index']))
        if dockermode:
            cmd = dockercmd
        else:
            cmd = []
        cmd = cmd + [ "mkvmerge", "-o", tempfilepathcmd, "--no-attachments", "--abort-on-warnings", "--flush-on-close" ]
        if len(filtervideo)>0:
            cmd.append("--video-tracks")
            cmd.append('!'+','.join(filtervideo))
        if len(filteraudio)>0:
            cmd.append("--audio-tracks")
            cmd.append('!'+','.join(filteraudio))
        if len(filtersubtitle)>0:
            cmd.append("--subtitle-tracks")
            cmd.append('!'+','.join(filtersubtitle))
        cmd.append(sourcefilepathcmd)

        logmessage("INFO", ' '.join(cmd))

        if testmode:
            logmessage("INFO", 'Test mode aborted')
        else:
            res = run_cmd(cmd)

            if res["rc"] != 0:
                logmessage("ERROR", "Return code : "+str(res["rc"]))
                for msg in res["msg"]:
                    logmessage("INFO", msg)
                try:
                    os.remove(tempfilepathcmd)
                except:
                    pass
                film["comment"]="Error durring processing"
            else:
                sizeafter = os.stat(tempfilepath).st_size
                gain = int((sizeafter - sizebefore)/(1024*1024))/1000

                logmessage("INFO", f"Moving {tempfilepath} to {sourcefilepath}")
                shutil.move(tempfilepath, sourcefilepath)

                logmessage("INFO", f"gain={gain} Go")
                film["comment"]="Done :-)"

            film["todo"]=False
            save_todo(todolist)
        logmessage("INFO", "---------------------------------------")
        maxiter -= 1
        if maxiter==0 :
            break
logmessage("INFO", ">>>> End")
