#!/bin/bash

INPUT_DIR="/media/HD1/Films"
OUTPUT_FILE="resultats_scan.csv"

# En-tête du fichier CSV
echo "Nom du fichier|Resolution|Codec Video|Audio (Langue - Format - Config)|Taille (Mo)|Statut|Erreur" > "$OUTPUT_FILE"

# Parcours des fichiers
find "$INPUT_DIR" -type f | while read -r FILE; do

  # Affichage de l'avancement
  # echo "Traitement de : $FILE"

  # Un seul appel à ffprobe pour récupérer toutes les infos
  FFPROBE_OUTPUT=$(./ffprobe -v error -show_format -show_streams -of json "$FILE" 2>&1)

  RESOLUTION_LABEL=""
  CODEC_VIDEO=""
  FILE_SIZE_MB=""
  AUDIO_INFO=""

  # Gestion des erreurs ffprobe
  if [ $? -ne 0 ]; then
    echo "$FILE" >> error.log
    STATUT="ERR"
  else
    # Extraction des informations avec jq
    WIDTH=$(echo "$FFPROBE_OUTPUT" | jq -r '.streams[] | select(.codec_type=="video") | .width' | head -n 1)

    # Interprétation de la résolution
    if [[ "$WIDTH" == "1920" ]]; then
      RESOLUTION_LABEL="1080p"
    elif [[ "$WIDTH" == "1280" ]]; then
      RESOLUTION_LABEL="720p"
    elif [[ "$WIDTH" == "720" ]]; then
      RESOLUTION_LABEL="480p"
    else
      RESOLUTION_LABEL="$WIDTH"
    fi

    CODEC_VIDEO=$(echo "$FFPROBE_OUTPUT" | jq -r '.streams[] | select(.codec_type=="video") | .codec_name' | head -n 1)
    FILE_SIZE_MB=$(echo "$FFPROBE_OUTPUT" | jq -r '.format.size' | awk '{print $1 / 1024 / 1024}')
    AUDIO_INFO=$(echo "$FFPROBE_OUTPUT" | jq -r '.streams[] | select(.codec_type=="audio") | "\(.tags.language)-\(.codec_name)-\(.channels)ch"' | paste -sd ";" -)

    # Détermination du statut
    # STATUT="Reload"
    # if [[ "$CODEC_VIDEO" == "hevc" && "$RESOLUTION_LABEL" == "1080p" ]]; then
    #   STATUT="Bon"
    # elif [[ "$RESOLUTION_LABEL" == "1080p" && "$CODEC_VIDEO" != "hevc" ]]; then
    #   STATUT="ToDo"
    # fi
  fi

  # Écriture des résultats dans le CSV
  echo "$(basename "$FILE")|$RESOLUTION_LABEL|$CODEC_VIDEO|$AUDIO_INFO|$(printf %.2f "$FILE_SIZE_MB")|$STATUT|" >> "$OUTPUT_FILE"
done
