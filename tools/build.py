#!/usr/bin/env python3
"""Assemble docs/index.html from src/index.html by inlining the seed data,
the Chalkboard font and Leaflet's stylesheet, so the page is one file."""
import base64, json, os, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / 'src/index.html').read_text()
data = json.dumps(json.load(open(ROOT / 'data/itinerary.json')), ensure_ascii=False)
font = base64.b64encode((ROOT / 'fonts/Chalkboard-Regular.ttf').read_bytes()).decode()

css_path = ROOT / 'src/leaflet.min.css'
if not css_path.exists():
    req = urllib.request.Request(
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
        headers={'User-Agent': 'boston-trip-map build'})
    css_path.write_bytes(urllib.request.urlopen(req).read())
leaflet_css = css_path.read_text()

out = (src.replace('/*{{LEAFLET_CSS}}*/', leaflet_css)
          .replace('{{FONT_B64}}', font)
          .replace('/*{{SEED}}*/null', data))
os.makedirs(ROOT / 'docs', exist_ok=True)
(ROOT / 'docs/index.html').write_text(out)
print('docs/index.html', len(out) // 1024, 'KB')
