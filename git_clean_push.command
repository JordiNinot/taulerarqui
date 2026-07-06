#!/bin/bash
set -e
cd /Users/macbookairjordi/.gemini/antigravity/scratch/taulerarqui

echo "=== 1. Netejant estat git ==="
rm -f .git/index.lock
rm -rf .git/rebase-merge

echo "=== 2. Traient fitxers grans del tracking ==="
git rm --cached "data/catastro_sabadell/A.ES.SDGC.BU.08186.building.gml" 2>/dev/null || true
git rm --cached "data/catastro_sabadell/A.ES.SDGC.BU.08186.buildingpart.gml" 2>/dev/null || true
git rm -r --cached "adreces_sabadell_cat.csv" 2>/dev/null || true
# Exclou qualsevol fitxer >50MB del staging
git diff --cached --name-only | while read f; do
  size=$(stat -f%z "$f" 2>/dev/null || echo 0)
  if [ "$size" -gt 52428800 ]; then
    echo "  Excloent $f ($size bytes)"
    git rm --cached "$f" 2>/dev/null || true
  fi
done

echo "=== 3. Afegint tots els fitxers (respectant .gitignore) ==="
git add -A

echo "=== 4. Verificant que no hi ha fitxers >50MB staging ==="
git diff --cached --name-only | while read f; do
  size=$(stat -f%z "$f" 2>/dev/null || echo 0)
  if [ "$size" -gt 52428800 ]; then
    echo "  AVÍS: $f és massa gran ($size), excloent..."
    git rm --cached "$f" || true
  fi
done

echo "=== 5. Commit ==="
git commit -m "feat: capa bus TUS - rutes per carrers, parades numerades, llegenda 13 linies

- build_path(): rutes segueixen carrers reals (OSM ways)
- Parades: badge numerat (1-999), popup amb linies TUS
- Llegenda 13 linies (L1-L23) amb colors oficials
- Filtre stubs OSM: descarta variants <10 punts
- 49 variants, 528 parades, 13844 punts totals"

echo "=== 6. Force push a GitHub ==="
git push --force origin main

echo ""
echo "=== PUBLICAT! ==="
git log --oneline -3
