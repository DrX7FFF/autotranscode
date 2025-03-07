import os
import sys
import json
import csv
from config import *
from pathlib import Path

execpath = os.path.dirname(sys.argv[0])

allfilename = execpath + "/data/all.json"
todofilename = execpath + "/data/todo.json"
errorfilename = execpath + "/data/error.json"
exportfilename = execpath + "/data/export.csv"
logfile= execpath + "/data/log.txt"

Path(execpath + "/data").mkdir(parents=True, exist_ok=True)

# def db_save(obj, filename):
#     with open(filename, "w", encoding="utf-8") as file:
#         json.dump(obj, file)

def loadjson(filename, default=None):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        print(f"No file : {filename}")
        return default

def custom_json_format(obj, level=0):
    """Formate le JSON pour qu'il soit compact mais avec des retours à la ligne pour chaque objet."""
    if isinstance(obj, dict):
        items = [f'"{k}":{custom_json_format(v, level+1)}' for k, v in obj.items()]
        return '{ ' + ',\t'.join(items) + ' }'
    elif isinstance(obj, list):
        items = [custom_json_format(v, level+1) for v in obj]
        return '[\n\t' + ',\n\t'.join(items) + ']'
    else:
        return json.dumps(obj, ensure_ascii=False)

def save_todo(movieslist, filename) :
    with open(filename, 'w', encoding="utf-8") as file:
        file.write('{\n')
        first=True
        for key, obj in movieslist.items():
            if first:
                first=False
            else:
                file.write(',\n')
            file.write(f'"{key}": {custom_json_format(obj, 1)}')
        # file.write(',\n'.join(key + ":" + custom_json_format(obj, 1) for key,obj in movieslist))
        file.write('\n}\n')

# with open("check.json", 'w') as file:
#     json.dump(filmlist, file, ensure_ascii=False, separators=(',', ':'))
    # json.dump(filmlist, file, indent=2, ensure_ascii=False, separators=(',', ':'))

# with open("check.json", 'w') as file:
#     for obj in filmlist:
#         file.write(json.dumps(obj, ensure_ascii=False) + "\n")


def export_to_csv(data, filename=exportfilename):
    """ Exporte une structure JSON dynamique en CSV tout en respectant l'ordre des clés. """

    # Collecter toutes les clés sans modifier l'ordre
    first_level_keys = []
    stream_keys = []

    for item in data:
        for key in item.keys():
            if key not in first_level_keys and key != "streams":
                first_level_keys.append(key)
        for stream in item.get("streams", []):
            for key in stream.keys():
                if key not in stream_keys:
                    stream_keys.append(key)

    all_keys = first_level_keys + stream_keys

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()

        for item in data:
            # Transformer les streams en un format aplati
            for stream in item.get("streams", [{}]):
                row = {key: item.get(key, "") for key in first_level_keys}
                row.update({key: stream.get(key, "") for key in stream_keys})
                writer.writerow(row)