#!/usr/bin/env python3
"""Pull the raw basemap geometry from Overpass once into data/basemap.json.

Kinds: roads, rail, water, coast, builtup, parks. Parks are kept only to be
subtracted from the built-up field, so they read as blank paper on the map.
Run tools/simplify_basemap.py afterwards.
"""
import json, os, sys, time, urllib.request, urllib.parse

BBOX = '42.18,-71.42,42.54,-70.78'  # south,west,north,east
UA = 'boston-trip-map/0.1 (personal trip planner; contact: natochi.cv)'
HOSTS = ('https://overpass-api.de/api/interpreter', 'https://z.overpass-api.de/api/interpreter',
         'https://overpass.kumi.systems/api/interpreter', 'https://overpass.private.coffee/api/interpreter')
PARTS = [
    f'way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]({BBOX});',
    f'way["railway"~"^(rail|subway|light_rail)$"]["service"!~"."]({BBOX});',
    f'(way["natural"="water"]({BBOX}); relation["natural"="water"]({BBOX}); way["natural"="coastline"]({BBOX}););',
    f'(way["landuse"~"^(residential|commercial|retail|industrial)$"]({BBOX}); relation["landuse"~"^(residential|commercial|retail|industrial)$"]({BBOX}););',
    f'(way["leisure"~"^(park|golf_course|nature_reserve)$"]({BBOX}); relation["leisure"~"^(park|golf_course|nature_reserve)$"]({BBOX}); way["landuse"~"^(cemetery|recreation_ground|forest)$"]({BBOX}); relation["landuse"~"^(cemetery|recreation_ground|forest)$"]({BBOX}););',
]
ROAD = {'motorway': 'm', 'trunk': 'k', 'primary': 'p', 'secondary': 's', 'tertiary': 't'}

def one(q):
    for attempt in range(12):
        host = HOSTS[attempt % len(HOSTS)]
        try:
            req = urllib.request.Request(host, data=urllib.parse.urlencode({'data': q}).encode(), headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)['elements']
        except Exception as e:
            print('retry', host, e, file=sys.stderr); time.sleep(8)
    sys.exit('overpass failed')

def pts(geom):
    return [[round(p['lon'], 5), round(p['lat'], 5)] for p in geom]

def stitch(ways):
    rings, pool = [], ways[:]
    while pool:
        ring = pool.pop(0)
        changed = True
        while changed and ring[0] != ring[-1]:
            changed = False
            for i, w in enumerate(pool):
                if w[0] == ring[-1]: ring += w[1:]; pool.pop(i); changed = True; break
                if w[-1] == ring[-1]: ring += w[::-1][1:]; pool.pop(i); changed = True; break
                if w[-1] == ring[0]: ring = w + ring[1:]; pool.pop(i); changed = True; break
                if w[0] == ring[0]: ring = w[::-1] + ring[1:]; pool.pop(i); changed = True; break
        rings.append(ring)
    return rings

out = {'bbox': BBOX, 'water': [], 'builtup': [], 'parks': [], 'roads': [], 'rail': [], 'coast': []}
def kind(t):
    if t.get('natural') == 'water': return 'water'
    if t.get('leisure') or t.get('landuse') in ('cemetery', 'recreation_ground', 'forest'): return 'parks'
    return 'builtup'

for part in PARTS:
    for el in one('[out:json][timeout:120];' + part + 'out body geom;'):
        t = el.get('tags', {})
        if el['type'] == 'way':
            g = pts(el.get('geometry', []))
            if len(g) < 2: continue
            if 'highway' in t: out['roads'].append({'c': ROAD[t['highway']], 'p': g})
            elif 'railway' in t: out['rail'].append({'u': 1 if t.get('tunnel') == 'yes' else 0, 'p': g})
            elif t.get('natural') == 'coastline': out['coast'].append(g)
            elif g[0] == g[-1]: out[kind(t)].append([g])
        elif el['type'] == 'relation':
            outers, inners = [], []
            for m in el.get('members', []):
                if m['type'] == 'way' and 'geometry' in m:
                    (inners if m.get('role') == 'inner' else outers).append(pts(m['geometry']))
            for ring in stitch(outers):
                if ring[0] == ring[-1]:
                    out[kind(t)].append([ring] + [r for r in inners if r[0] == r[-1]])
    print('part ok', {k: len(v) for k, v in out.items() if isinstance(v, list)}, file=sys.stderr)

json.dump(out, open('data/basemap.json', 'w'), separators=(',', ':'))
print('data/basemap.json', os.path.getsize('data/basemap.json') // 1024, 'KB')
