import os
import sys
from pathlib import Path

execpath = os.path.dirname(sys.argv[0])

dbfilename = execpath + "/data/db.json"
dbfilenameMKV = execpath + "/data/dbMKV.json"
todofilename = execpath + "/data/check.json"
todofilenameMKV = execpath + "/data/checkMKV.json"
exportfilename = execpath + "/data/export.csv"
exportfilenameMKV = execpath + "/data/exportMKV.csv"
logfile= execpath + "/data/log.txt"
moviespath = "/home/moi/mediaHD1/Films"
temppath="/tmp/transcode"
dockermode=False
testmode=True

audio_language_remove = ['eng', 'dan', 'dut', 'ita', 'spa']
audio_title_remove = ['VFQ', 'AD', 'SDH', 'QUEBECOIS']

subtitle_language_remove = ['eng', 'spa', 'ita', 'por', 'ger', 'dut', 'dan', 'fin', 'ice', 'kor', 'nor', 'swe']
# on garde 'jpn' et 'chi' pour kill bill
subtitle_title_remove = ['VFQ', 'AD', 'SDH', 'QUEBECOIS']

Path(execpath + "/data").mkdir(parents=True, exist_ok=True)
