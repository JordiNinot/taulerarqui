#!/bin/bash
cd /Users/macbookairjordi/.gemini/antigravity/scratch/taulerarqui

echo "=== Avortant rebase ==="
git rebase --abort || true

echo "=== Afegint tots els fitxers ==="
git add -A

echo "=== Commit ==="
git commit -m "feat: capa bus TUS - rutes per carrers, parades numerades, llegenda 13 linies"

echo "=== Push a GitHub ==="
git push origin main

echo ""
echo "=== FET! ==="
