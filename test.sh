#!/bin/bash

# https://trac.ffmpeg.org/wiki/HWAccelIntro#PlatformAPIAvailability
# https://trac.ffmpeg.org/wiki/Hardware/VAAPI

ffmpeg -i "/mnt/mediacenter/HD1/Films/[ OxTorrent.com ] Escape Plan 2013 MULTI 1080p BluRay x264-CARPEDIEM.mkv" -c:v hevc_amf -preset slow -crf 20                -c:a copy -c:s copy "/mnt/mediacenter/HD1/Films/Escape Plan 2013.mkv"
ffmpeg -i "/mnt/mediacenter/HD1/Films/[ OxTorrent.com ] Escape Plan 2013 MULTI 1080p BluRay x264-CARPEDIEM.mkv" -c:v hevc     -preset fast -crf 20 -hwaccel vaapi -c:a copy -c:s copy "/mnt/mediacenter/HD1/Films/Escape Plan 2013.mkv"
ffmpeg -i "/mnt/mediacenter/HD1/Films/[ OxTorrent.com ] Escape Plan 2013 MULTI 1080p BluRay x264-CARPEDIEM.mkv" -c:v hevc     -preset fast -crf 20 -hwaccel vaapi -c:a copy -c:s copy "Escape Plan 2013.mkv"
ffmpeg -hwaccel vaapi          -i "/mnt/mediacenter/HD1/Films/[ OxTorrent.com ] Escape Plan 2013 MULTI 1080p BluRay x264-CARPEDIEM.mkv" -c:v hevc -preset fast -crf 20 -c:a copy -c:s copy "/mnt/mediacenter/HD1/Films/Escape Plan 2013.mkv"
ffmpeg -hwaccel vaapi -v debug -i "/mnt/mediacenter/HD1/Films/[ OxTorrent.com ] Escape Plan 2013 MULTI 1080p BluRay x264-CARPEDIEM.mkv" -c:v hevc -preset fast -crf 20 -c:a copy -c:s copy "Escape Plan 2013.mkv"
ffmpeg -hwaccel vaapi -v debug -i "/mnt/mediacenter/HD1/Films/[ OxTorrent.com ] Escape Plan 2013 MULTI 1080p BluRay x264-CARPEDIEM.mkv" -c:v hevc -preset fast -crf 20 -c:a copy -c:s copy "~/Escape Plan 2013.mkv"
OK
ffmpeg -hwaccel vaapi -i "[ OxTorrent.com ] Escape Plan 2013 MULTI 1080p BluRay x264-CARPEDIEM.mkv" -c:v hevc -preset fast -crf 20 -c:a copy -c:s copy "Escape Plan 2013.mkv"
ffmpeg -hwaccel vaapi -i "Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv" -c:v hevc -preset slow -crf 20 -c:a copy -c:s copy "Harry.Potter.and.the.Order.of.the.Phoenix.2007.[HECV.20.S.1080p].mkv"

ffmpeg -hwaccel vaapi -i "Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv" -c:v hevc -preset slow -crf 20 -c:a copy -c:s copy "Harry.Potter.and.the.Order.of.the.Phoenix.2007.[HECV.20.S.1080p].mkv"


./ffmpeg -hwaccel vaapi -i "/media/HD1/downloads/Red Rooms (2023).BDRemux.1080p.R.G. Goldenshara.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v libx265 -preset slower -crf 20 -c:a copy -c:s copy "/media/HD1/Fims/Red Rooms (2023) [x265.20.VS.1080p].mkv"
./ffmpeg -i "/media/HD1/downloads/Red Rooms (2023).BDRemux.1080p.R.G. Goldenshara.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v libx265 -preset slower -crf 20 -c:a copy -c:s copy "/media/HD1/Films/Red Rooms (2023) [x265.20.VS.1080p].mkv"
ffmpeg -hwaccel vaapi -i "/home/moi/mediaHD1/downloads/Red Rooms (2023).BDRemux.1080p.R.G. Goldenshara.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v libx265 -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Red Rooms (2023) [x265.20.VS.1080p].mkv"
frame=14916 fps=4.0 q=25.4 q=0.0 q=25.4 size=  283648kB time=00:10:25.15 bitrate=3716.9kbits/s speed=0.167x
ffmpeg -hwaccel vaapi -i "/home/moi/mediaHD1/downloads/Red Rooms (2023).BDRemux.1080p.R.G. Goldenshara.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v libx265 -preset slow -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Red Rooms (2023) [x265.20.VS.1080p].mkv"
frame= 7031 fps= 15 q=25.2 q=0.0 q=25.2 size=  119808kB time=00:04:55.45 bitrate=3321.9kbits/s speed=0.647x
ffmpeg -hwaccel vaapi -i "/home/moi/mediaHD1/downloads/Red Rooms (2023).BDRemux.1080p.R.G. Goldenshara.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v hevc -preset slow -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Red Rooms (2023) [x265.20.VS.1080p].mkv"
frame= 9025 fps= 15 q=23.6 q=0.0 q=23.6 size=  160256kB time=00:06:18.52 bitrate=3468.2kbits/s speed=0.631x 

ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi -i "/home/moi/mediaHD1/downloads/Red Rooms (2023).BDRemux.1080p.R.G. Goldenshara.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v hevc_vaapi -preset slow -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Red Rooms (2023) [x265.20.VS.1080p].mkv"
OK

ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi -i "/home/moi/mediaHD1/downloads/Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v hevc_vaapi -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Harry Potter and the Order of the Phoenix (2007) [x265.20.SR.1080p].mkv"
error
ffmpeg -hwaccel dxva2 -hwaccel_output_format dxva2_vld -i "/home/moi/mediaHD1/downloads/Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v av1_amf -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Harry Potter and the Order of the Phoenix (2007) [x265.20.SR.1080p].mkv"
unknow encoder 

ffmpeg -hwaccel dxva2 -hwaccel_output_format dxva2_vld -i "/home/moi/mediaHD1/downloads/Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v hevc_vaapi -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Harry Potter and the Order of the Phoenix (2007) [x265.20.SR.1080p].mkv"
error

ffmpeg -i "/home/moi/mediaHD1/downloads/Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v hevc_vaapi -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Harry Potter and the Order of the Phoenix (2007) [x265.20.SR.1080p].mkv"
error

ffmpeg -i "/home/moi/mediaHD1/downloads/Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -vf scale=1280x720 -c:v hevc_vaapi -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Films/Harry Potter and the Order of the Phoenix (2007) [x265.20.SR.1080p].mkv"
??

ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi -i "/home/moi/mediaHD1/Servarr/ToDo/Escape Plan (2013).mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre -c:v hevc_vaapi -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Servarr/Transcoding/Escape Plan (2013).mkv"
ok


ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi -i "/home/moi/mediaHD1/Servarr/ToDo/input.mkv" -map 0:v -map 0:m:language:fre -map 0:s:m:language:fre                            -c:v hevc_vaapi -preset slower -crf 20 -c:a copy -c:s copy "/home/moi/mediaHD1/Servarr/Transcoding/output.mkv"
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi -i input.mkv                                                                                          -vf 'format=nv12,hwupload' -c:v hevc_vaapi -qp 18                                     output.mkv

#####

ffmpeg -hide_banner  \
-hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi \
-i "/home/moi/mediaHD1/Servarr/ToDo/Escape Plan (2013).mkv" \
-map 0:v -map 0:m:language:fre -map 0:s:m:language:fre \
-c:v hevc_vaapi -qp 20 -c:a copy -c:s copy \
"/home/moi/mediaHD1/Servarr/Transcoding/Escape Plan (2013).mkv"

# plus rien avec 
-loglevel warning
# Error avec le filtre :
-vf 'format=nv12,hwupload'

####

/home/moi/mediaHD1/downloads/Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRemux.1080p.mkv


encoded 2961 frames in 142.68s (20.75 fps), 5631.75 kb/s, Avg QP:24.86
Exiting normally, received signal 2.
96,9 Mo

echo $(basename "${~/HD1/Films/Apollo 13 (1995).mkv%.*}")
mkdir -p 
ln "$file" "$RADARR_DIR/$filename/"


ln "/media/HD1/Films/Apollo 13 (1995).mkv" "/media/HD1/FilmsTest/Films/Apollo 13 (1995)/Apollo 13 (1995).mkv"
ls -i "/media/HD1/Films/Apollo 13 (1995).mkv"
ls -i "/media/HD1/FilmsTest/Films/Apollo 13 (1995)"


ffprobe -v error -show_format -show_streams -of json "~/mediaHD1/Films/Apollo 13 (1995).mkv"
ffprobe -v error -show_format -show_streams -of json "/media/HD1/Films/Apollo 13 (1995).mkv"

ffprobe -v error -show_format -show_streams -of json "/media/HD1/downloads/Красные комнаты.2023.BDRemux.1080p.R.G. Goldenshara.mkv" > "/media/HD1/downloads/Красные комнаты.2023.BDRemux.1080p.R.G. Goldenshara.json"

#!/bin/bash

# Dossier à analyser
DIR="/chemin/vers/tes/films"

# Rechercher les fichiers avec plusieurs hard links
find "/media/HD1/Films" -type f -links +1 -printf "%n links -> %p\n"

ln -s "/home/moi/mediaHD1/Films/Armageddon (1998).mkv" "/home/moi/mediaHD1/Servarr/Films/Armageddon (1998)"