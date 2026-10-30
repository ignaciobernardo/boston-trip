
## Basemap

No tiles. `tools/fetch_basemap.py` pulls roads, rail, water, built-up land and parks from Overpass into `data/basemap.json` for a wide area around the city (Waltham to Nahant, Quincy to Lynn). `tools/simplify_basemap.py` (needs `shapely`) unions and simplifies them, builds the sea from the coastline, and writes `docs/basemap.json`.

The page draws it on canvas tiles: whole x stitches for built-up land that keep clear of roads and rail, diagonal hatch for water, ink roads, ladder ticks for rail and the T above ground. The map's minimum zoom and pan limits follow the data's edge, so the paper never runs out.
