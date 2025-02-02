#!/bin/bash
set -u
ticketpath="/home/moi/mediaHD1/Servarr/TranscodingTickets"
transcodingpath="/home/moi/mediaHD1/Servarr/Transcoding"

for ticket in "$ticketpath"/*; do
    if [[ -f "$ticket" ]]; then
        source "$ticket"

        outfile="$transcodingpath/$filename"
        echo "ticket:$ticket"
        echo "action:$action"
        echo "filename:$filename"
        echo "filepath:$filepath"
        echo "video_codec:$video_codec"
        echo "resolution:$resolution"
        echo "bitrate:$bitrate"
        echo "profile:$profile"
        echo "outfile:$outfile"

        # # plus rien avec 
        # -loglevel warning
        # # Error avec le filtre :
        # -vf 'format=nv12,hwupload'
        # -vf 'format=hwupload' \

        if [[ "$action" == "ToEncode" ]]; then
            echo "Action : Transcode"
            videohw="-hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi"
            videoaction="-c:v hevc_vaapi -qp 20"
        else 
            echo "Action : Clean"
            videohw=""
            videoaction="-c:v copy"
        fi

        ffmpeg -hide_banner -loglevel warning -stats \
        $videohw \
        -i "$filepath" \
        -map 0:v -map 0:m:language:fre \
        $videoaction \
        -c:a copy \
        -c:s copy \
        "$outfile"
    fi
done
