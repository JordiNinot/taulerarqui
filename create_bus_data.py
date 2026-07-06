#!/usr/bin/env python3
"""
Genera data/bus_data.js amb rutes i parades de bus de Sabadell (Overpass API).
Versió 3: només línies TUS urbanes (L1-L23), geometria completa de carrers.
    python3 create_bus_data.py
"""
import json, os, re, urllib.request, urllib.parse

BASE = 'https://overpass-api.de/api/interpreter'

# Filtra directament per operador TUS — evita baixar rutes regionals
Q_ROUTES = (
    '[out:json][timeout:120];'
    'area["name"="Sabadell"]["admin_level"="8"]->.a;'
    '('
    'relation["type"="route"]["route"="bus"]["operator"~"TUS",i](area.a);'
    'relation["type"="route"]["route"="bus"]["network"~"TUS",i](area.a);'
    'relation["type"="route"]["route"="bus"]["ref"~"^L(44|55|80)$"](area.a);'
    ');'
    'out geom;'
)
Q_STOPS = (
    '[out:json][timeout:60];'
    'area["name"="Sabadell"]["admin_level"="8"]->.a;'
    '('
    'node["highway"="bus_stop"](area.a);'
    'node["public_transport"="stop_position"]["bus"="yes"](area.a);'
    ');out body;'
)

# Refs TUS oficials confirmats a tus.es (juliol 2026)
TUS_REFS = {
    'L1','L2','L3','L4','L5','L7','L8',
    'L10','L11','L12','L14','L15','L23',
    'L44','L55','L80'
}
RE_TUS = re.compile(r'^L\d{1,2}$', re.IGNORECASE)

def is_tus(ref):
    return ref in TUS_REFS or bool(RE_TUS.match(ref or ''))

def overpass(query):
    data = ('data=' + urllib.parse.quote(query)).encode()
    req  = urllib.request.Request(BASE, data=data, method='POST')
    req.add_header('User-Agent', 'taulerarqui/3.0')
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode('utf-8'))

def dist2(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

def build_path(members):
    """
    Construeix una polilínia contínua a partir dels ways membres d'una relació.
    Cada way es pot invertir si cal per connectar-lo amb l'anterior.
    """
    ways = []
    for m in members:
        if m.get('type') == 'way' and m.get('geometry'):
            geom = [(p['lat'], p['lon']) for p in m['geometry']]
            if len(geom) >= 2:
                ways.append(geom)
    if not ways:
        return []

    path = list(ways[0])
    used = {0}

    for _ in range(len(ways) - 1):
        last = path[-1]
        best_i   = None
        best_rev = False
        best_d   = float('inf')

        for i, w in enumerate(ways):
            if i in used:
                continue
            d_s = dist2(w[0],  last)
            d_e = dist2(w[-1], last)
            if d_s < best_d:
                best_d = d_s; best_i = i; best_rev = False
            if d_e < best_d:
                best_d = d_e; best_i = i; best_rev = True

        if best_i is None:
            break
        used.add(best_i)
        seg = ways[best_i]
        if best_rev:
            seg = seg[::-1]
        path.extend(seg[1:])

    return path

def enc(lat, lon):
    return [round((lat - 41) * 10000), round((lon - 2) * 10000)]

# ── Baixada de dades ──────────────────────────────────────────────────────────

print('Baixant rutes TUS de Sabadell…')
r_routes = overpass(Q_ROUTES)
all_routes = [e for e in r_routes.get('elements', []) if e.get('type') == 'relation']
# Filtre de seguretat addicional: nomes refs L1-L23
routes = [r for r in all_routes if is_tus(r.get('tags', {}).get('ref', ''))]
refs_trobats = sorted(set(r.get('tags',{}).get('ref','') for r in routes))
print(f'  {len(all_routes)} relacions baixades  →  {len(routes)} rutes TUS vàlides')
print(f'  Refs: {refs_trobats}')
falten = sorted(TUS_REFS - set(refs_trobats))
if falten:
    print(f'  FALTEN a OSM: {falten}')

print('Baixant parades de bus…')
r_stops = overpass(Q_STOPS)
stops = [e for e in r_stops.get('elements', []) if e.get('type') == 'node' and 'lat' in e]
print(f'  {len(stops)} parades trobades')

# ── Índex parada → línies ─────────────────────────────────────────────────────
stop_lines = {}
for rel in routes:
    ref = rel.get('tags', {}).get('ref', '')
    col = rel.get('tags', {}).get('colour', '#1a6bbf')
    for m in rel.get('members', []):
        if m.get('type') == 'node':
            nid = m['ref']
            if nid not in stop_lines:
                stop_lines[nid] = []
            if not any(x['r'] == ref for x in stop_lines[nid]):
                stop_lines[nid].append({'r': ref, 'c': col})

# Matching espacial: highway=bus_stop → stop_position
# Moltes parades OSM tenen dues entrades separades (15-30m de distància).
# Per a cada parada sense línies, cerca la més propera (dins 120m) que en tingui.
stop_pos_index = {}  # nid → (lat, lon, lines)
for node in stops:
    nid = node['id']
    lins = stop_lines.get(nid, [])
    if lins:
        stop_pos_index[nid] = (node['lat'], node['lon'], lins)

MATCH_DIST2 = (0.0012) ** 2  # ~120m en graus (≈0.001° per ~111m)

def latlon_dist2(lat1, lon1, lat2, lon2):
    dlat = lat1 - lat2
    dlon = (lon1 - lon2) * 0.75  # correcció longitud a lat~41
    return dlat*dlat + dlon*dlon

for node in stops:
    nid = node['id']
    if stop_lines.get(nid):
        continue  # ja té línies
    lat, lon = node['lat'], node['lon']
    best_d, best_lins = MATCH_DIST2, None
    for other_nid, (olat, olon, olins) in stop_pos_index.items():
        d = latlon_dist2(lat, lon, olat, olon)
        if d < best_d:
            best_d = d
            best_lins = olins
    if best_lins:
        stop_lines[nid] = best_lins

# ── Construcció de rutes seguint carrers ──────────────────────────────────────
BUS_ROUTES = []
for rel in routes:
    tags     = rel.get('tags', {})
    raw_path = build_path(rel.get('members', []))
    if len(raw_path) < 2:
        continue

    pts  = []
    prev = None
    for lat, lon in raw_path:
        p = enc(lat, lon)
        if p != prev:
            pts.append(p)
            prev = p

    if len(pts) < 2:
        continue

    BUS_ROUTES.append({
        'r': tags.get('ref', ''),
        'n': tags.get('name', ''),
        'c': tags.get('colour', '#1a6bbf'),
        'p': pts
    })

# ── Parades (nomes les que tenen almenys una línia TUS) ───────────────────────
BUS_STOPS = []
for node in stops:
    t    = node.get('tags', {})
    nid  = node['id']
    lins = stop_lines.get(nid, [])
    # Inclou totes les parades (també les sense línia TUS associada)
    BUS_STOPS.append([
        nid,
        round((node['lat'] - 41) * 10000),
        round((node['lon'] - 2) * 10000),
        t.get('name', ''),
        t.get('ref:TUS') or t.get('local_ref') or t.get('ref') or '',
        lins
    ])

# ── Sortida ───────────────────────────────────────────────────────────────────
output = (
    'var _BUS_ROUTES=' + json.dumps(BUS_ROUTES, ensure_ascii=False, separators=(',',':')) + ';\n'
    'var _BUS_STOPS='  + json.dumps(BUS_STOPS,  ensure_ascii=False, separators=(',',':')) + ';\n'
)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'bus_data.js')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(output)

total_pts = sum(len(r['p']) for r in BUS_ROUTES)
print(f'\nFitxer creat: {out_path}')
print(f'Mida: {len(output):,} bytes')
print(f'Rutes: {len(BUS_ROUTES)}  |  Parades: {len(BUS_STOPS)}  |  Punts totals: {total_pts:,}')
print(f'Punts/ruta de mitjana: {total_pts // max(len(BUS_ROUTES), 1)}')
