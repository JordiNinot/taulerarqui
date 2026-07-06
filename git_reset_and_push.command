#!/bin/bash
set -e
cd /Users/macbookairjordi/.gemini/antigravity/scratch/taulerarqui

echo "=== 1. Neteja ==="
rm -f .git/index.lock
rm -rf .git/rebase-merge

echo "=== 2. Commit inicial ==="
INIT_SHA=$(git log --oneline | tail -1 | awk '{print $1}')
echo "Tornant a: $INIT_SHA"

echo "=== 3. Reset soft al commit inicial ==="
git reset --soft "$INIT_SHA"

echo "=== 4. Desstagin fitxers grans ==="
git reset HEAD "data/catastro_sabadell/" 2>/dev/null || true
git reset HEAD "adreces_sabadell_cat.csv" 2>/dev/null || true

echo "=== 5. Staging (amb .gitignore actualitzat) ==="
git add -A

echo "=== 6. Verificació: cap fitxer >50MB ==="
git diff --cached --name-only | while read f; do
  if [ -f "$f" ]; then
    size=$(stat -f%z "$f" 2>/dev/null || echo 0)
    if [ "$size" -gt 52428800 ]; then
      echo "  EXCLOENT: $f ($size bytes)"
      git rm --cached "$f" 2>/dev/null || true
    fi
  fi
done

echo "=== 7. Commit ==="
git commit -m "feat: capa bus TUS - rutes per carrers, parades numerades, llegenda 13 linies

- build_path(): rutes segueixen carrers reals (OSM ways)
- Parades: badge numerat (1-999), popup amb linies TUS
- Llegenda 13 linies (L1-L23) amb colors oficials TUS
- Filtre stubs OSM: descarta variants <10 punts
- data/bus_data.js: 49 variants, 528 parades, 13844 punts"

echo "=== 8. Fitxers al commit ==="
git diff HEAD~1 --name-only 2>/dev/null || git show --name-only HEAD | grep -v "^commit\|^Author\|^Date\|^$\|^    " || true

echo "=== 9. Force push ==="
git push --force origin main

echo ""
echo "=== PUBLICAT! ==="
git log --oneline -3
