
## Basemap

No tiles. `tools/fetch_basemap.py` pulls roads, rail, water and built-up polygons from Overpass into `data/basemap.json`; `tools/simplify_basemap.py` simplifies them, closes the harbor from the coastline, and writes `docs/basemap.json`, which the page draws on canvas tiles: × fields for built-up land, diagonal hatch for water, thick ink roads, ladder ticks for rail and the T.
