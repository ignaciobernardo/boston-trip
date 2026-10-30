#!/usr/bin/env python3
"""data/basemap.json (raw Overpass) -> docs/basemap.json (small, drawable).

Needs shapely. Water and the built-up field are unioned so nothing overlaps:
- sea: coastline + bbox edge are polygonized; OSM keeps water on the right of
  each coastline way, which tells sea faces from land faces.
- built-up: landuse polygons, plus a band around streets in the city core,
  minus water and parks, so parks read as blank paper.
Detail drops outside the area the trip actually uses, to keep the file small.
"""
import json, os
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box, mapping
from shapely.ops import polygonize, unary_union
from shapely.prepared import prep

raw = json.load(open('data/basemap.json'))
S, W, N, E = map(float, raw['bbox'].split(','))
AREA = box(W, S, E, N)
CORE = box(-71.20, 42.31, -71.00, 42.42)   # full detail here
PREP_CORE = prep(CORE)
FINE, COARSE = 0.00003, 0.00022            # simplify tolerance in degrees

def polys(items):
    out = []
    for rings in items:
        if len(rings[0]) < 4: continue
        p = Polygon(rings[0], [r for r in rings[1:] if len(r) >= 4])
        if not p.is_valid: p = p.buffer(0)
        if not p.is_empty: out.append(p)
    return out

def parts(g):
    if g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    return [x for x in getattr(g, 'geoms', []) if x.geom_type == 'Polygon']

# --- sea ---
coast = [LineString(c).intersection(AREA) for c in raw['coast'] if len(c) > 1]
lines = [g for c in coast for g in (c.geoms if hasattr(c, 'geoms') else [c]) if g.geom_type == 'LineString' and g.length > 0]
faces = list(polygonize(unary_union(lines + [AREA.boundary])))
votes = [0] * len(faces)
for c in raw['coast']:
    for (x1, y1), (x2, y2) in zip(c[::4], c[1::4]):
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** .5
        if not L: continue
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        right = Point(mx + dy / L * 1e-4, my - dx / L * 1e-4)
        left = Point(mx - dy / L * 1e-4, my + dx / L * 1e-4)
        for i, f in enumerate(faces):
            if f.contains(right): votes[i] += 1
            if f.contains(left): votes[i] -= 1
sea = [f for f, v in zip(faces, votes) if v > 0]
print('coast faces', len(faces), 'sea', len(sea))

water = unary_union(polys(raw['water']) + sea).intersection(AREA)
parks = unary_union(polys(raw['parks'])).buffer(0)

# --- built-up field ---
streets = [LineString(r['p']) for r in raw['roads'] if r['c'] in 'pst' and len(r['p']) > 1]
street_band = unary_union(streets).buffer(0.0013, quad_segs=2).intersection(CORE)
land = unary_union(polys(raw['builtup']) + [street_band])
land = land.buffer(0.0005, quad_segs=2).buffer(-0.0005, quad_segs=2)
built = land.difference(parks).difference(water).intersection(AREA)

def area_out(g, min_core, min_far):
    res = []
    for p in parts(g):
        far = not PREP_CORE.intersects(p)
        if p.area < (min_far if far else min_core): continue
        q = p.simplify(COARSE if far else FINE)
        for x in parts(q):
            rings = [x.exterior] + [r for r in x.interiors if Polygon(r).area > min_core]
            res.append({'r': [[[round(a, 5), round(b, 5)] for a, b in r.coords] for r in rings]})
    return res

def line_out(p, keep_far=True):
    ls = LineString(p)
    if not PREP_CORE.intersects(ls):
        if not keep_far: return None
        ls = ls.simplify(COARSE)
    else:
        ls = ls.simplify(FINE)
    return [[round(a, 5), round(b, 5)] for a, b in ls.coords]

out = {
    'bbox': [W, S, E, N],
    'water': area_out(water, 2e-7, 3e-6),
    'builtup': area_out(built, 2e-7, 4e-6),
    'roads': [],
    'rail': [],
}
for r in raw['roads']:
    if len(r['p']) < 2: continue
    p = line_out(r['p'], keep_far=r['c'] in 'mkp')
    if p: out['roads'].append({'c': r['c'], 'p': p})
for r in raw['rail']:
    if len(r['p']) < 2: continue
    out['rail'].append({'u': r['u'], 'p': line_out(r['p'])})

json.dump(out, open('docs/basemap.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in out.items()}, os.path.getsize('docs/basemap.json') // 1024, 'KB')
