#!/usr/bin/env python3
"""Pull the basemap geometry for Boston/Cambridge from Overpass once and save
it as data/basemap.json. Four kinds only: water (hatched), builtup (× field),
roads (thick lines), rail (ladder). Coordinates are rounded to 5 decimals."""
import json, sys, time, urllib.request, urllib.parse

BBOX = '42.322,-71.175,42.412,-71.015'  # south,west,north,east
UA = 'boston-trip-map/0.1 (personal trip planner; contact: natochi.cv)'
Q = f"""
[out:json][timeout:120];
(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]({BBOX});
  way["railway"~"^(rail|subway|light_rail)$"]["service"!~"."]({BBOX});
  way["natural"="water"]({BBOX});
  relation["natural"="water"]({BBOX});
  way["natural"="coastline"]({BBOX});
  way["landuse"~"^(residential|commercial|retail|industrial)$"]({BBOX});
  relation["landuse"~"^(residential|commercial|retail|industrial)$"]({BBOX});
);
out body geom;
"""

HOSTS = ('https://overpass-api.de/api/interpreter', 'https://z.overpass-api.de/api/interpreter',
         'https://overpass.kumi.systems/api/interpreter', 'https://overpass.private.coffee/api/interpreter')
PARTS = [
    f'way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]({BBOX});',
    f'way["railway"~"^(rail|subway|light_rail)$"]["service"!~"."]({BBOX});',
    f'(way["natural"="water"]({BBOX}); relation["natural"="water"]({BBOX}); way["natural"="coastline"]({BBOX}););',
    f'(way["landuse"~"^(residential|commercial|retail|industrial)$"]({BBOX}); relation["landuse"~"^(residential|commercial|retail|industrial)$"]({BBOX}););',
]
def one(q):
    for attempt in range(8):
        host = HOSTS[attempt % len(HOSTS)]
        try:
            req = urllib.request.Request(host, data=urllib.parse.urlencode({'data': q}).encode(), headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)['elements']
        except Exception as e:
            print('retry', host, e, file=sys.stderr); time.sleep(8)
    sys.exit('overpass failed')
def fetch():
    els = []
    for part in PARTS:
        els += one('[out:json][timeout:90];' + part + 'out body geom;')
        print('part ok', len(els), file=sys.stderr)
    return {'elements': els}

def pts(geom):
    return [[round(p['lon'], 5), round(p['lat'], 5)] for p in geom]

def thin(line, step=1):
    return line if step == 1 else line[::step] + ([line[-1]] if (len(line) - 1) % step else [])

data = fetch()
out = {'bbox': BBOX, 'water': [], 'builtup': [], 'roads': [], 'rail': [], 'coast': []}
for el in data['elements']:
    t = el.get('tags', {})
    if el['type'] == 'way':
        g = pts(el.get('geometry', []))
        if len(g) < 2: continue
        if 'highway' in t: out['roads'].append({'c': {'motorway':'m','trunk':'k','primary':'p','secondary':'s','tertiary':'t'}[t['highway']], 'p': g})
        elif 'railway' in t: out['rail'].append({'s': t['railway'] == 'subway' and t.get('tunnel') == 'yes', 'p': g})
        elif t.get('natural') == 'water': out['water'].append([g])
        elif t.get('natural') == 'coastline': out['coast'].append(g)
        elif 'landuse' in t: out['builtup'].append([g])
    elif el['type'] == 'relation':
        outers, inners = [], []
        for m in el.get('members', []):
            if m['type'] != 'way' or 'geometry' not in m: continue
            (outers if m.get('role') != 'inner' else inners).append(pts(m['geometry']))
        # stitch outer way fragments into rings
        rings = []
        pool = outers[:]
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
        for ring in rings:
            poly = [ring] + [r for r in inners if r[0] == r[-1]]
            (out['water'] if t.get('natural') == 'water' else out['builtup']).append(poly)

json.dump(out, open('data/basemap.json', 'w'), separators=(',', ':'))
for k, v in out.items():
    if isinstance(v, list): print(f'{k:8} {len(v)}')
import os; print('data/basemap.json', os.path.getsize('data/basemap.json') // 1024, 'KB')
