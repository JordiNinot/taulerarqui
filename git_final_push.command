#!/bin/bash
export GIT_PAGER=cat
set -e
cd /Users/macbookairjordi/.gemini/antigravity/scratch/taulerarqui

echo "=== 1. Neteja ==="
rm -f .git/index.lock
rm -rf .git/rebase-merge

echo "=== 2. Reset al commit inicial ==="
INIT_SHA=$(git log --oneline | tail -1 | awk '{print $1}')
echo "SHA inicial: $INIT_SHA"
git reset --soft "$INIT_SHA"

echo "=== 3. Destaging fitxers grans ==="
git reset HEAD "data/catastro_sabadell/" 2>/dev/null || true

echo "=== 4. Staging net (sense GML) ==="
git add -A

echo "=== 5. Verificar que el GML NO hi es ==="
COUNT=$(git diff --cached --name-only | grep "\.gml$" | wc -l | tr -d ' ')
if [ "$COUNT" -gt 0 ]; then
  echo "ERROR: GML files detectats al staging:"
  git diff --cached --name-only | grep "\.gml$"
  git rm --cached $(git diff --cached --name-only | grep "\.gml$") || true
fi

echo "=== 6. Commit ==="
git commit -m "feat: capa bus TUS - rutes per carrers, parades numerades, llegenda 13 linies"

echo "=== 7. Force push ==="
git push --force origin main

echo ""
echo "=== PUBLICAT! ==="
git log --oneline -3
