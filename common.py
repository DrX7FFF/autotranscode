filmlistfile = "check.json"

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

def savefilmlist(filename, films) :
    with open(filename, 'w', encoding="utf-8") as file:
        file.write('[\n')
        file.write(',\n'.join(custom_json_format(obj, 1) for obj in films))
        file.write('\n]\n')

# with open(filmlistfile, "w", encoding="utf-8") as file:
#     json.dump(filmlist, file, indent=2, ensure_ascii=False)

# with open("check.json", 'w') as file:
#     json.dump(filmlist, file, ensure_ascii=False, separators=(',', ':'))
    # json.dump(filmlist, file, indent=2, ensure_ascii=False, separators=(',', ':'))

# with open("check.json", 'w') as file:
#     for obj in filmlist:
#         file.write(json.dumps(obj, ensure_ascii=False) + "\n")

def loadfilmlist(filename)
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)