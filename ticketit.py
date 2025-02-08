import json

filmlistfile = "check.json"
ticketpath="/home/moi/mediaHD1/Servarr/TranscodingTickets"

with open(filmlistfile, 'r') as file:
    filmlist = json.load(file)

for film in filmlist:
    if film["todo"] :
        mapfilter=""
        print(f"{film['fileindex']} - {film['filename']} - {film['comment']}")
        for stream in film["streams"]:
            print(json.dumps(stream, ensure_ascii=False))
            if stream["remove"]:
                mapfilter += f"-map -0:{stream['index']} "
                # print(f"    {stream['index']} - {stream['codec']} - {stream['profile']} - {stream['resolution']} - {stream['language']}")
        with open(ticketpath+"/"+film["filename"]+".txt", "w") as f:
            f.write(f"filename=\"{film["filename"]}\"\nmapfilter=\"{mapfilter}\"\n")
