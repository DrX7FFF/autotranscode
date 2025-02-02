#!/bin/bash

# Dossier contenant les films
DOSSIER_FILMS="$1"

# Fichier de résultat
FICHIER_RESULTAT="resultats_films_audio.txt"

# En-têtes du fichier de résultat
echo -e "Nom du Film\tStatut\tRésolution\tEncodage\tPistes Audio\tTaille (Go)" > "$FICHIER_RESULTAT"

# Fonction pour analyser chaque film
analyse_film() {
    echo "Analyse du film : $1"
    local film="$1"
    
    # Récupération du nom du film sans extension
    local nom_film=$(basename "$film" | cut -d. -f1)

    # Analyse du fichier vidéo avec ffprobe
    local resolution=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$film")
    local codec=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$film")
    local bitrate=$(ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=p=0 "$film")
    local audio_tracks=$(ffprobe -v error -select_streams a -show_entries stream=codec_name,channels,language -of csv=p=0 "$film")
    
    # Taille du fichier en Go
    local taille=$(du -BG "$film" | cut -f1 | sed 's/G//')

    # Vérification de la résolution
    IFS='x' read -r largeur hauteur <<< "$resolution"

    # Détermination du statut
    local statut="Reload"  # Par défaut, il faut retélécharger

    # Test si le film est déjà en bon format (HEVC avec bitrate acceptable)
    if [[ "$codec" == "hevc" && "$bitrate" -le 7000000 && "$largeur" -eq 1920 && "$hauteur" -eq 1080 ]]; then
        statut="Bon"  # Film déjà en X265 et dans la plage de bitrate
    # Test si le film est un REMUX et peut être converti
    elif [[ "$codec" == "hevc" && "$bitrate" -gt 7000000 ]]; then
        statut="ToDo"  # Film en REMUX mais à convertir
    fi

    # Création de la ligne de résultat
    local pistes_audio=""
    while IFS=',' read -r codec_audio channels language; do
        # Déterminer le type de canal (stéréo, 5.1, etc.)
        if [ "$channels" -eq 2 ]; then
            type_audio="Stéréo"
        elif [ "$channels" -eq 6 ]; then
            type_audio="5.1"
        else
            type_audio="Inconnu"
        fi
        # Ajouter la piste audio à la liste
        pistes_audio+="$language ($type_audio, $codec_audio), "
    done <<< "$audio_tracks"

    # Retirer la dernière virgule et espace
    pistes_audio=$(echo "$pistes_audio" | sed 's/, $//')

    # Écriture dans le fichier de résultats
    echo -e "$nom_film\t$statut\t$resolution\t$codec\t$pistes_audio\t$taille" >> "$FICHIER_RESULTAT"
}

# Scan du dossier et analyse de chaque film
for film in "$DOSSIER_FILMS"/*.mkv; do
    if [[ -f "$film" ]]; then
        analyse_film "$film"
    fi
done

echo "Analyse terminée, résultats dans $FICHIER_RESULTAT."
