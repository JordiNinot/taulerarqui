#!/bin/bash
# Doble clic per executar — genera data/bus_data.js des d'Overpass API
cd "$(dirname "$0")"
echo "========================================"
echo "  Generant data/bus_data.js..."
echo "========================================"
python3 create_bus_data.py
echo ""
echo "✓ Fet! Ara recarrega index.html al navegador."
echo "Prem Retorn per tancar..."
read
