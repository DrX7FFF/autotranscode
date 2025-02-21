#!/usr/bin/env python
import sys
import json
import re
import unicodedata
from common import *

movieslist = loadjson(allfilename, {})

audio_langs = []
audio_titles = []
subtitle_langs = []
subtitle_titles = []

for filename, moviedef in movieslist.items():
    for stream in moviedef["streams"]:
        if stream.get("type") == "audio":
            if not stream["language"] in audio_langs:
                audio_langs.append(stream["language"])
            if not stream["title"] in audio_titles:
                    audio_titles.append(stream["title"])
        if stream.get("type") == "subtitle":
            if not stream["language"] in subtitle_langs:
                subtitle_langs.append(stream["language"])
            if not stream["title"] in subtitle_titles:
                subtitle_titles.append(stream["title"])

print("Liste des langues audio :")           
print(audio_langs)

print("Liste des titres audio :")
print(audio_titles)

print("Liste des langues sous-titres :")
print(subtitle_langs)

print("Liste des titres sous-titres :")
print(subtitle_titles)