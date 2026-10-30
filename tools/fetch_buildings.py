#!/usr/bin/env python3
"""Pull building footprints with heights from Overpass for the core of the trip
(Harvard to the South End) into docs/buildings.json.

Output: {"bbox": "...", "b": [[height_m, [[lon, lat], ...]], ...]} with coordinates
rounded to 5 decimals and small sheds dropped. Height comes from `height`, else
`building:levels` * 3.2, else 9 m.
"""
import json, re, sys, time, urllib.request, urllib.parse

# south, west, north, east: Harvard Sq, Inman, Kendall, Beacon Hill, Back Bay, South End
BBOX = '42.335,-71.135,42.385,-71.045'
UA = 'boston-trip-map/0.1 (personal trip planner; contact: natochi.cv)'
HOSTS = ('https://overpass-api.de/api/interpreter', 'https://z.overpass-api.de/api/interpreter')
UNUSED_HOSTS = (
         'https://overpass.kumi.systems/api/interpreter', 'https://overpass.private.coffee/api/interpreter')

def one(q):
    for attempt in range(12):
        host = HOSTS[attempt % len(HOSTS)]
        try:
            req = urllib.request.Request(host, data=urllib.parse.urlencode({'data': q}).encode(), headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)['elements']
        except Exception as e:
            print('retry', host, e, file=sys.stderr); time.sleep(8)
    sys.exit('overpass failed')

def height(t):
    h = t.get('height') or t.get('building:height')
    if h:
        m = re.match(r'[\d.]+', h)
        if m:
            v = float(m.group())
            return round(v * 0.3048, 1) if h.strip().endswith(("'", 'ft')) else round(v, 1)
    lv = t.get('building:levels')
    if lv:
        m = re.match(r'[\d.]+', lv)
        if m: return round(float(m.group()) * 3.2, 1)
    return 9.0

def area(ring):
    a = 0
    for i in range(len(ring) - 1):
        a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
    return abs(a) / 2

out = {'bbox': BBOX, 'b': []}
# split the box in 4 so each query stays small
s, w, n, e = map(float, BBOX.split(','))
mid_lat, mid_lon = (s + n) / 2, (w + e) / 2
boxes = [f'{s},{w},{mid_lat},{mid_lon}', f'{s},{mid_lon},{mid_lat},{e}', f'{mid_lat},{w},{n},{mid_lon}', f'{mid_lat},{mid_lon},{n},{e}']
seen = set()
for bb in boxes:
    els = one(f'[out:json][timeout:180];way["building"]({bb});out body geom;')
    for el in els:
        if el['id'] in seen or 'geometry' not in el: continue
        seen.add(el['id'])
        ring = [[round(p['lon'], 5), round(p['lat'], 5)] for p in el['geometry']]
        if len(ring) < 4 or ring[0] != ring[-1]: continue
        if area(ring) < 2.5e-9: continue  # roughly < 25 m2
        out['b'].append([height(el.get('tags', {})), ring])
    print(bb, len(out['b']), file=sys.stderr)
    time.sleep(3)

json.dump(out, open('docs/buildings.json', 'w'), separators=(',', ':'))
print('buildings', len(out['b']), file=sys.stderr)
