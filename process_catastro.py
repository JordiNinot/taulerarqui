#!/usr/bin/env python3
"""
Processa el GML d'edificis del Catastro INSPIRE per Sabadell.
Extreu numberOfDwellings per edifici i fa matching amb adreces per coordenades.
Genera: data/habitatges_data.js  →  {codvia: {numcom: habitatges}}
"""

import csv, sys, math, json, re
from xml.etree import ElementTree as ET
from pyproj import Transformer
from scipy.spatial import KDTree
import numpy as np

GML   = '/sessions/stoic-eloquent-lovelace/mnt/taulerarqui/data/catastro_sabadell/A.ES.SDGC.BU.08186.building.gml'
CSV   = '/sessions/stoic-eloquent-lovelace/mnt/taulerarqui/adreces_sabadell_enriched.csv'
OUT   = '/sessions/stoic-eloquent-lovelace/mnt/taulerarqui/data/habitatges_data.js'

MAX_DIST_M = 80  # distància màxima per assignar edifici a adreça (metres)

print("1/4 Convertint coordenades: WGS84 → UTM 25831")
to_utm = Transformer.from_crs("EPSG:4326", "EPSG:25831", always_xy=True)

print("2/4 Parsejant GML (122 MB)...")
# Namespaces
NS = {
    'gml':     'http://www.opengis.net/gml/3.2',
    'bu-ext2d':'http://inspire.jrc.ec.europa.eu/schemas/bu-ext2d/2.0',
    'bu-core2d':'http://inspire.jrc.ec.europa.eu/schemas/bu-core2d/2.0',
}

# Parseig incremental per estalviar memòria
buildings = []  # [(cx_utm, cy_utm, n_dwellings), ...]

context = ET.iterparse(GML, events=('end',))
count = 0
skipped = 0
for event, elem in context:
    tag = elem.tag
    # Busquem elements Building
    if tag.endswith('}Building'):
        # bounding box
        bb = elem.find('.//{http://www.opengis.net/gml/3.2}Envelope')
        nd_el = elem.find('.//{http://inspire.jrc.ec.europa.eu/schemas/bu-ext2d/2.0}numberOfDwellings')
        if bb is not None and nd_el is not None:
            try:
                nd = int(nd_el.text or '0')
                lo = bb.find('{http://www.opengis.net/gml/3.2}lowerCorner').text.split()
                hi = bb.find('{http://www.opengis.net/gml/3.2}upperCorner').text.split()
                cx = (float(lo[0]) + float(hi[0])) / 2
                cy = (float(lo[1]) + float(hi[1])) / 2
                buildings.append((cx, cy, nd))
                count += 1
            except Exception:
                skipped += 1
        elem.clear()
    elif tag.endswith('}featureMember'):
        elem.clear()

print(f"   → {count} edificis llegits, {skipped} saltats")
print(f"   → edificis amb dwellings > 0: {sum(1 for b in buildings if b[2] > 0)}")

# KD-tree sobre centroids UTM
coords_utm = np.array([(b[0], b[1]) for b in buildings])
tree = KDTree(coords_utm)
dw   = np.array([b[2] for b in buildings])

print("3/4 Llegint CSV d'adreces i fent matching...")
result = {}  # {codvia: {numcom: habitatges}}
matched = 0
unmatched = 0

with open(CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            lat   = float(row['LAT'])
            lng   = float(row['LNG'])
            codvia = row['CODVIA'].strip()
            numcom = row['NUMCOM'].strip()
            # Convertim a UTM
            x, y = to_utm.transform(lng, lat)
            # Closest building
            dist, idx = tree.query([x, y])
            if dist <= MAX_DIST_M:
                nd = int(dw[idx])
                if nd > 0:
                    if codvia not in result:
                        result[codvia] = {}
                    result[codvia][numcom] = nd
                    matched += 1
            else:
                unmatched += 1
        except Exception as e:
            unmatched += 1

print(f"   → {matched} adreces amb habitatges assignats, {unmatched} sense")
print(f"   → {len(result)} carrers únics amb dades")

print("4/4 Generant habitatges_data.js...")
# Estadístiques
total_hab = sum(sum(v.values()) for v in result.values())
print(f"   → Total habitatges acumulats: {total_hab}")
print(f"   → Habitants estimats (×2.5): {total_hab * 2.5:,.0f}")

# Generar JS compacte
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('// Habitatges per adreça (Catastro INSPIRE, 08186 Sabadell)\n')
    f.write('// Format: {codvia: {numcom: numberOfDwellings}}\n')
    f.write('var _HABITATGES_DATA = ')
    json.dump(result, f, separators=(',',':'))
    f.write(';\n')

import os
size = os.path.getsize(OUT)
print(f"   → Fitxer generat: {size/1024:.1f} KB")
print("DONE!")
