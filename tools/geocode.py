#!/usr/bin/env python3
"""Geocode every stop and lodging in data/itinerary.json with Nominatim.

One request per second, with a User-Agent, as the usage policy asks.
Results are written back into the file (lat, lng, geocodeStatus) and a
table is printed. Already-geocoded entries are skipped unless --force.
"""
import json, sys, time, math, urllib.parse, urllib.request

PATH = 'data/itinerary.json'
UA = 'boston-trip-map/0.1 (personal trip planner; contact: natochi.cv)'
# Rough centre of Cambridge/Boston; anything > 12 km away is suspicious.
CENTER = (42.3601, -71.0942)
FORCE = '--force' in sys.argv
# Nominatim struggles with "Business, Neighbourhood, City" strings; these
# overrides use the street address so the pin lands on the real door.
OVERRIDES = {
    'Boston Logan International Airport, Boston, MA': (42.3656, -71.0096),
    'Clover Food Lab, Harvard Square, Cambridge, MA': '1326 Massachusetts Ave, Cambridge, MA',
    'Harvard Yard, Cambridge, MA': (42.3744, -71.1169),
    'Michette Bakery, Inman Square, Cambridge, MA': '1251 Cambridge St, Cambridge, MA',
    'Fenway Victory Gardens, Boston, MA': (42.3435, -71.0953),
    'Commonwealth Avenue Mall, Boston, MA': (42.3523, -71.0760),
    'Union Park, Boston, MA': (42.3425, -71.0710),
    'Louisburg Square, Boston, MA': (42.3581, -71.0686),
    'Acorn St, Boston, MA': (42.3579, -71.0690),
    'Boston Public Garden, Boston, MA': (42.3541, -71.0704),
    'One Kendall Square, Cambridge, MA': (42.3668, -71.0905),
    'Copley Square, Boston, MA': (42.3499, -71.0776),
    '10 1/2 Beacon St, Boston, MA': (42.3579, -71.0618),
    '1 Museum of Science Driveway, Boston, MA': (42.3677, -71.0709),
}

def dist_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371*math.asin(math.sqrt(h))

def nominatim(q):
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(
        {'q': q, 'format': 'json', 'limit': 1, 'countrycodes': 'us'})
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.load(r)
    time.sleep(1.1)
    if not res:
        return None
    return float(res[0]['lat']), float(res[0]['lon']), res[0].get('display_name', '')

def resolve(addr):
    ov = OVERRIDES.get(addr)
    if isinstance(ov, tuple):
        return ov[0], ov[1], 'manual', 'ok'
    q = ov or addr
    hit = nominatim(q)
    if not hit:
        return None, None, '', 'check'
    lat, lng, name = hit
    status = 'ok' if dist_km((lat, lng), CENTER) < 12 else 'check'
    return lat, lng, name, status

data = json.load(open(PATH))
rows = []
def handle(item, label):
    if not item.get('address'):
        item['lat'] = item['lng'] = None
        item['geocodeStatus'] = 'check'
        rows.append((label, item['name'], None, None, 'check', 'no address'))
        return
    if not FORCE and item.get('lat') and item.get('geocodeStatus') == 'ok':
        rows.append((label, item['name'], item['lat'], item['lng'], 'ok', 'cached'))
        return
    lat, lng, name, status = resolve(item['address'])
    item['lat'], item['lng'], item['geocodeStatus'] = lat, lng, status
    rows.append((label, item['name'], lat, lng, status, name[:60]))

for l in data['lodging']:
    handle(l, 'lodging')
for d in data['days']:
    for s in d['stops']:
        handle(s, d['date'][5:])

json.dump(data, open(PATH, 'w'), indent=2, ensure_ascii=False)
json.dump(data, open(PATH, 'w'), indent=2, ensure_ascii=False)

print(f"{'day':7} {'name':48} {'lat':9} {'lng':10} {'st':5} match")
for r in rows:
    lat = f"{r[2]:.5f}" if r[2] else '-'
    lng = f"{r[3]:.5f}" if r[3] else '-'
    print(f"{r[0]:7} {r[1][:48]:48} {lat:9} {lng:10} {r[4]:5} {r[5]}")
bad = [r for r in rows if r[4] != 'ok']
print(f"\n{len(rows)} entries, {len(bad)} to check")
for r in bad:
    print('  CHECK:', r[0], r[1])
