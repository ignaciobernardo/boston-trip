#!/usr/bin/env python3
"""Inline data/itinerary.json into every docs/v/*/index.html that carries the /*ITINERARY*/ marker."""
import glob, json, re
seed = json.dumps(json.load(open('data/itinerary.json')), separators=(',', ':'))
for p in glob.glob('docs/v/*/index.html'):
    s = open(p).read()
    if '/*ITINERARY*/' not in s: continue
    s = re.sub(r'/\*ITINERARY\*/(?:null|\{.*?\});\n</script>', lambda m: '/*ITINERARY*/' + seed + ';\n</script>', s, count=1, flags=re.S)
    open(p, 'w').write(s); print('inlined', p)
