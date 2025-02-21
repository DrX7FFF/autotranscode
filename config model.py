moviespath = "/media/HD1/Films"
temppath = "/media/HD1/Transcoding"
fasttemppath = "/storage/.config/dockers/mkvtoolnix"

dockermoviespath = "/storage/Films"
dockertemppath="/storage/Transcoding"
dockerfasttemppath = "/config"
fastsize = 8000

dockercmd = ["docker", "exec", "mkvtoolnix"]

dockermode=True
testmode=True

audio_language_remove = ['eng', 'dan', 'dut', 'ita', 'spa']
audio_title_remove = ['VFQ', 'AD', 'SDH', 'QUEBECOIS']

subtitle_language_remove = ['eng', 'spa', 'ita', 'por', 'ger', 'dut', 'dan', 'fin', 'ice', 'kor', 'nor', 'swe']
# on garde 'jpn' et 'chi' pour kill bill
subtitle_title_remove = ['VFQ', 'AD', 'SDH', 'QUEBECOIS']

