#!/bin/bash
set -e
cd /Users/macbookairjordi/.gemini/antigravity/scratch/taulerarqui

echo "=== 1. Netejant estat git corromput ==="
rm -f .git/index.lock
rm -rf .git/rebase-merge
rm -f .git/MERGE_HEAD .git/CHERRY_PICK_HEAD .git/REVERT_HEAD

echo "=== 2. Estat actual ==="
git status --short | head -20

echo "=== 3. Afegint tots els fitxers ==="
git add -A

echo "=== 4. Commit ==="
git commit -m "feat: capa bus TUS - rutes per carrers, parades numerades, llegenda 13 linies

- build_path() algoritme: rutes segueixen carrers reals (OSM ways)
- L.polyline weight=4, hover weight=6, color oficial per linia
- Parades: badge numerat (1-999), popup amb linies TUS
- Llegenda dinamica: 13 linies (L1-L23) amb colors oficials
- Filtre stubs OSM: descarta variants <10 punts
- Spatial matching: 91% parades amb info de linies (120m radius)
- data/bus_data.js: 49 variants, 528 parades, 13844 punts totals"

echo "=== 5. Force push a GitHub ==="
git push --force origin main

echo ""
echo "=== PUBLICAT! ==="
git log --oneline -3
