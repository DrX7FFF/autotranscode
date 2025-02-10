#!/bin/bash
set -u
ticketpath="/home/moi/mediaHD1/Servarr/TranscodingTickets"
inpath="/home/moi/mediaHD1/Films"
outpath="/home/moi/mediaHD1/Servarr/Transcoding"
logfile="log.txt"

for ticket in "$ticketpath"/*; do
    if [[ -f "$ticket" ]]; then

        # videohw="-hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi"
        # videoaction="-c:v hevc_vaapi -qp 20"

        videohw=""
        videoaction="-c:v copy"
        mapfilter=""

        source "$ticket"
        echo "ticket:$ticket"
        
        infile="$inpath/$filename"
        outfile="$outpath/$filename"
        echo ">>>>>> $(date) Begin \"$ticket\"" >> "$logfile"
        echo "filename:$filename" >> "$logfile"
        echo "infile:$infile" >> "$logfile"
        echo "outfile:$outfile" >> "$logfile"
        echo "videohw:$videohw" >> "$logfile"
        echo "videoaction:$videoaction" >> "$logfile"
        echo "mapfilter:$mapfilter" >> "$logfile"

        # # plus rien avec 
        # -loglevel warning
        # # Error avec le filtre :
        # -vf 'format=nv12,hwupload'
        # -vf 'format=hwupload' \

        # peut être avoir besoin de ça juste avant videohw  (voir les valeurs entre 10 et 100):
        # -analyzeduration 100M -probesize 100M

        #https://ffmpeg.org/ffmpeg.html#Generic-options:%7E:text=.-,%2Dreport,-Dump%20full%20command
        # 24 = warning
        # FFREPORT=file="$logfile":level=24

        time ffmpeg -hide_banner -loglevel warning -stats \
        $videohw \
        -i "$infile" \
        -map_metadata 0 -map_chapters 0 -map 0 \
        $mapfilter \
        $videoaction \
        -c:a copy \
        -c:s copy \
        "$outfile"

        if [[ $? -ne 0 ]]; then
            echo "Error : $action failed"
            exit 1
        fi

        sizeBefore=$(du -BM "$infile" | cut -f1 | sed 's/M//')
        sizeAfter=$(du -BM "$outfile" | cut -f1 | sed 's/M//')
        echo "Size: $sizeBefore => $sizeAfter = $(($sizeBefore - $sizeAfter)) Mo" >> "$logfile"

        mv -f "$outfile" "$infile"
        if [[ $? -ne 0 ]]; then
            echo "Error : Impossible to move "$oufile" to "$infile" failed" >> "$logfile"
            echo "Aborting $filename"
            exit 1
        fi

        rm -f "$ticket"
        echo ">>>>>> $(date) Done \"$filename\"" >> "$logfile"
    fi
done
