#!/bin/bash
VERSION="7"

appname="autotranscode"

tempfile="/tmp/myinstall.zip"
tempfolder="/tmp/myinstall"
destfolder="/storage/.kodi/tools/autotranscode"

echo "Installing $appname (setup version $VERSION)"

# Create tools folder
mkdir -p "$destfolder"

# Download and copy App
curl -L "https://github.com/DrX7FFF/$appname/archive/refs/heads/main.zip" -o "$tempfile"
unzip -o "$tempfile" -d "$tempfolder"
cp -rf "$tempfolder/$appname-main/." "$destfolder"
rm "$tempfile"
rm -r "$tempfolder"

# Make executable
chmod +x "$destfolder"/*.py
