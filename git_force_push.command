#!/bin/bash
cd /Users/macbookairjordi/.gemini/antigravity/scratch/taulerarqui

echo "=== Eliminant lock si existeix ==="
rm -f .git/index.lock

echo "=== Estat actual ==="
git log --oneline -3

echo "=== Force push a GitHub ==="
git push --force-with-lease origin main

echo ""
echo "=== FET! ==="
