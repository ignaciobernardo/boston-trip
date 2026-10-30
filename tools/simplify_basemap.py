#!/usr/bin/env python3
"""data/basemap.json (raw Overpass) -> docs/basemap.json (small, drawable).

- Douglas-Peucker on every line/ring (tolerance in degrees, ~2.5 m).
- Coastline ways stitched into chains and closed along the bbox so the harbor
  becomes a water polygon (OSM coastline keeps land on the left, water on the right).
- Everything rounded to 5 decimals, bbox per feature for tile culling.
"""
import json, math

S, W, N, E = map(float, json.load(open('data/basemap.json'))['bbox'].split(','))
raw = json.load(open('data/basemap.json'))
TOL = 0.000025

def dp(pts, tol):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1e-12
    imax, dmax = 0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L if L > 1e-12 else math.hypot(x - x1, y - y1)
        if d > dmax: imax, dmax = i, d
    if dmax > tol:
        return dp(pts[:imax + 1], tol)[:-1] + dp(pts[imax:], tol)
    return [pts[0], pts[-1]]

def bbox(rings):
    xs = [p[0] for r in rings for p in r]; ys = [p[1] for r in rings for p in r]
    return [round(min(xs), 5), round(min(ys), 5), round(max(xs), 5), round(max(ys), 5)]

def inside(p): return W <= p[0] <= E and S <= p[1] <= N

# --- coastline -> sea polygons ---
chains = []
pool = [list(map(tuple, w)) for w in raw['coast']]
while pool:
    c = pool.pop(0); grew = True
    while grew:
        grew = False
        for i, w in enumerate(pool):
            if w[0] == c[-1]: c += w[1:]; pool.pop(i); grew = True; break
            if w[-1] == c[0]: c = w + c[1:]; pool.pop(i); grew = True; break
    chains.append(c)

def clip_to_bbox(chain):
    # keep maximal runs inside the bbox, with the crossing points pushed onto the edge
    runs, cur = [], []
    for i, p in enumerate(chain):
        if inside(p):
            if not cur and i > 0: cur.append(edge_point(chain[i - 1], p))
            cur.append(p)
        elif cur:
            cur.append(edge_point(p, cur[-1])); runs.append(cur); cur = []
    if cur: runs.append(cur)
    return runs

def edge_point(outside, ins):
    # walk from inside point toward outside point until the bbox edge
    (ox, oy), (ix, iy) = outside, ins
    t = 1.0
    for lo, hi, a, b in ((W, E, ix, ox), (S, N, iy, oy)):
        if b < lo: t = min(t, (a - lo) / (a - b))
        if b > hi: t = min(t, (hi - a) / (b - a))
    return (ix + (ox - ix) * t, iy + (oy - iy) * t)

def edge_pos(p):
    # clockwise position along bbox perimeter starting at SW corner going north
    x, y = p
    if abs(x - W) < 1e-9: return y - S
    if abs(y - N) < 1e-9: return (N - S) + (x - W)
    if abs(x - E) < 1e-9: return (N - S) + (E - W) + (N - y)
    return 2 * (N - S) + (E - W) + (E - x)
PER = 2 * (N - S) + 2 * (E - W)
CORNERS = [(0, (W, S)), ((N - S), (W, N)), ((N - S) + (E - W), (E, N)), (2 * (N - S) + (E - W), (E, S))]

def close_clockwise(run):
    # water is on the right of travel: from the run's end walk the perimeter clockwise to its start
    a, b = edge_pos(run[-1]), edge_pos(run[0])
    ring = list(run)
    pos = a
    while True:
        nxt = [c for c in CORNERS if (c[0] - pos) % PER > 1e-12]
        nxt.sort(key=lambda c: (c[0] - pos) % PER)
        dist_to_b = (b - pos) % PER
        if not nxt or (nxt[0][0] - pos) % PER >= dist_to_b: break
        ring.append(nxt[0][1]); pos = nxt[0][0]
    ring.append(run[0])
    return ring

sea = []
for c in chains:
    for run in clip_to_bbox(c):
        if len(run) < 2: continue
        if run[0] == run[-1]: sea.append([run])        # island-ish closed loop: land, skip
        else: sea.append([close_clockwise(run)])

out = {'water': [], 'builtup': [], 'roads': [], 'rail': []}
for poly in raw['water'] + sea:
    rings = [[tuple(p) for p in dp(r, TOL)] for r in poly if len(r) >= 4]
    if rings: out['water'].append({'r': [[list(p) for p in r] for r in rings]})
for poly in raw['builtup']:
    rings = [[tuple(p) for p in dp(r, TOL)] for r in poly if len(r) >= 4]
    if rings: out['builtup'].append({'r': [[list(p) for p in r] for r in rings]})
for w in raw['roads']:
    p = dp(w['p'], TOL)
    out['roads'].append({'c': w['c'], 'p': p})
for w in raw['rail']:
    p = dp(w['p'], TOL)
    out['rail'].append({'u': 1 if w['s'] else 0, 'p': p})

json.dump(out, open('docs/basemap.json', 'w'), separators=(',', ':'))
import os
print({k: len(v) for k, v in out.items()}, 'sea polys', len(sea), os.path.getsize('docs/basemap.json') // 1024, 'KB')
