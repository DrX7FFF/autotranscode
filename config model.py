import os
import sys
from pathlib import Path

execpath = os.path.dirname(sys.argv[0])

dbfilename = execpath + "/data/db.json"
todofilename = execpath + "/data/check.json"
exportfilename = execpath + "/data/export.csv"
logfile= execpath + "/data/log.txt"

moviespath = "/media/HD1/Films"
temppath = "/media/HD1/Transcoding"
fasttemppath = "/storage/.config/dockers/mkvtoolnix"

dockermoviespath = "/storage/Films"
dockertemppath="/storage/Transcoding"
dockerfasttemppath = "/config"
fastsize = 5000

dockercmd = ["docker", "exec", "mkvtoolnix"]

dockermode=True
testmode=True

audio_language_remove = ['eng', 'dan', 'dut', 'ita', 'spa']
audio_title_remove = ['VFQ', 'AD', 'SDH', 'QUEBECOIS']

subtitle_language_remove = ['eng', 'spa', 'ita', 'por', 'ger', 'dut', 'dan', 'fin', 'ice', 'kor', 'nor', 'swe']
# on garde 'jpn' et 'chi' pour kill bill
subtitle_title_remove = ['VFQ', 'AD', 'SDH', 'QUEBECOIS']

Path(execpath + "/data").mkdir(parents=True, exist_ok=True)
