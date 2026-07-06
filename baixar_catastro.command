#!/bin/bash
DEST="$HOME/.gemini/antigravity/scratch/taulerarqui/data"
EXTRACT="$DEST/catastro_sabadell"
ZIP="$DEST/catastro_sabadell.zip"
URL="https://www.catastro.hacienda.gob.es/INSPIRE/Buildings/08/08186-SABADELL/A.ES.SDGC.BU.08186.zip"

# Si Chrome ja ha descarregat el fitxer a Downloads, l'aprofitem
CHROME_DL="$HOME/Downloads/A.ES.SDGC.BU.08186.zip"
if [ -f "$CHROME_DL" ]; then
  echo "Fitxer trobat a Downloads, copiant..."
  cp "$CHROME_DL" "$ZIP"
else
  echo "Baixant edificis Catastro Sabadell (~80 MB)..."
  curl -L --progress-bar "$URL" -o "$ZIP"
  if [ $? -ne 0 ]; then
    echo "ERROR en la descàrrega (codi $?)"
    read -n 1 -p "Prem qualsevol tecla per tancar..."; exit 1
  fi
fi

echo "Descomprimint..."
mkdir -p "$EXTRACT"
unzip -o "$ZIP" -d "$EXTRACT/"
echo ""
echo "Fet! Fitxers:"
ls "$EXTRACT/"
read -n 1 -p "Prem qualsevol tecla per tancar..."
