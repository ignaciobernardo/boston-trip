# Boston & Cambridge trip map

Interactive plan for the Oct 30 to Nov 5, 2026 trip, live at natochi.cv/boston. Built from `HANDOUT.md`.

- `data/itinerary.json`: the seed plan with coordinates (`tools/geocode.py`, Nominatim, 1 request per second).
- `src/index.html`: the page. `tools/build.py` inlines the seed and Leaflet's CSS into `docs/index.html`, which GitHub Pages serves.
- Four views of the same plan: Sentence (the day as one sentence), One at a time (one stop fills the panel, Next rolls into the next day), Week (`#week`, every stop as a block with its time, price and the leg to the next stop; click to open, drag to reorder or move to another day) and Checklist (`#checklist`, bookings plus every stop, with every stop on the map). A stop marked done shows as done everywhere.
- After a move, a stop's planned leg no longer applies, so the page shows a walking estimate from the distance. Reset order restores every stop's original day, order and time.
- Edits live in `localStorage` (`bostonTrip.v1`). Backup copies them out as text and restores them.

"Creator happy hour" (Sun Nov 1) has no address yet, so it has no pin. Add it as your own stop, or set its `address` and rerun `python3 tools/geocode.py`.

Rebuild with `python3 tools/build.py`.

## Basemap

No tiles. `tools/fetch_basemap.py` pulls roads, rail, water, built-up land and parks from Overpass into `data/basemap.json` for a wide area around the city (Waltham to Nahant, Quincy to Lynn). `tools/simplify_basemap.py` (needs `shapely`) unions and simplifies them, builds the sea from the coastline, and writes `docs/basemap.json`.

The page draws it on canvas tiles: whole x stitches for built-up land that keep clear of roads and rail, diagonal hatch for water, solid roads, ladder ticks for rail and the T above ground. The map's minimum zoom and pan limits follow the data's edge, so the sheet never runs out.
