#!/usr/bin/env python3
"""Inline data/itinerary.json into page.html -> index.html for the walk-app variant."""
import json, pathlib
here = pathlib.Path(__file__).parent
root = here.parent.parent.parent
seed = json.dumps(json.load(open(root / 'data' / 'itinerary.json')), separators=(',', ':')).replace('</', '<\\/')
page = (here / 'page.html').read_text()
(here / 'index.html').write_text(page.replace('/*ITINERARY*/', seed))
print('built', here / 'index.html')
