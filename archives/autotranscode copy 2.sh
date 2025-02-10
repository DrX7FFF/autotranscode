#!/bin/bash
set -u
ticketpath="/home/moi/mediaHD1/Servarr/TranscodingTickets"
transcodingpath="/home/moi/mediaHD1/Servarr/Transcoding"

mkdir -p "log"

for ticket in "$ticketpath"/*; do
    if [[ -f "$ticket" ]]; then
        source "$ticket"
        echo "ticket:$ticket"
        logfile="./log/$(basename "$ticket").log"
        echo ">>>>>> $(date) Begin \"$filename\"" >> "$logfile"

        outfile="$transcodingpath/$filename"
        echo "ticket:$ticket" >> "$logfile"
        echo "action:$action" >> "$logfile"
        echo "filename:$filename" >> "$logfile"
        echo "filepath:$filepath" >> "$logfile"
        # echo "video_codec:$video_codec"
        # echo "resolution:$resolution"
        # echo "bitrate:$bitrate"
        # echo "profile:$profile"
        echo "outfile:$outfile" >> "$logfile"

        # # plus rien avec 
        # -loglevel warning
        # # Error avec le filtre :
        # -vf 'format=nv12,hwupload'
        # -vf 'format=hwupload' \

        # peut être avoir besoin de ça juste avant videohw  (voir les valeurs entre 10 et 100):
        # -analyzeduration 100M -probesize 100M

        if [[ "$action" == "ToEncode" ]]; then
            echo "Action : Transcode"
            videohw="-hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi"
            videoaction="-c:v hevc_vaapi -qp 20"
        else 
            echo "Action : Clean"
            videohw=""
            videoaction="-c:v copy"
        fi

        #https://ffmpeg.org/ffmpeg.html#Generic-options:%7E:text=.-,%2Dreport,-Dump%20full%20command
        # 24 = warning
        # FFREPORT=file="$logfile":level=24

        time ffmpeg -hide_banner -loglevel warning -stats \
        $videohw \
        -i "$filepath" \
        -map_metadata 0 -map_chapters 0 \
        -map 0:v -map 0:m:language:fra:? -map 0:m:language:fre \
        $videoaction \
        -c:a copy \
        -c:s copy \
        "$outfile"

        if [[ $? -ne 0 ]]; then
            echo "Error : $action failed"
            exit 1
        fi

        sizeBefore=$(du -BM "$filepath" | cut -f1 | sed 's/M//')
        sizeAfter=$(du -BM "$outfile" | cut -f1 | sed 's/M//')
        echo "Size: $sizeBefore => $sizeAfter = $(($sizeBefore - $sizeAfter)) Mo" >> "$logfile"

        mv -f "$outfile" "$filepath"
        if [[ $? -ne 0 ]]; then
            echo "Error : Impossible to move "$oufile" to "$filepath" failed" >> "$logfile"
            echo "Aborting $filename"
            exit 1
        fi

        rm -f "$ticket"
        echo ">>>>>> $(date) Done \"$filename\"" >> "$logfile"
        exit 0
    fi
done
