# Trip Map Website: Claude Code Handout

Oct 29, 2026 · @Trinidad

Hand this doc to Claude Code to build an interactive map of the Boston and Cambridge trip (Oct 30 to Nov 5) with a day-by-day side panel, costs, notes and custom activities.

## Prompt to paste into Claude Code

Copy this, then attach or paste the rest of this doc (especially the itinerary JSON) in the same message.

```markdown
Build me a single-page interactive trip planner for my Boston/Cambridge trip (Oct 30 to Nov 5, 2026).

Layout: a full-height map on one side and a side panel on the other. A day switcher at the top of the panel (Fri 30, Sat 31, Sun 1, Mon 2, Tue 3, Wed 4, Thu 5). Selecting a day shows that day's stops as numbered markers on the map, connected by a route line in order, and the panel lists the same stops as a timeline: time, name, address, why I'm going, cost, and the travel leg to the next stop. Clicking a stop in the panel pans the map to it and opens its popup; clicking a marker highlights the stop in the panel.

The panel also shows: the day's summary and spend, a running trip budget (activities and transport, from the data), and a "Book this" checklist. Each stop has a Google Maps link and the day has an "Open route in Google Maps" link.

I must be able to: add my own activities (name, time, day, address or click-on-map location, cost, note), edit or delete the ones I added, reorder stops within a day, write notes on any stop and a free-text note per day, and tick checklist items. All of that persists across reloads. Add export/import of my data as JSON so nothing is lost if browser storage is cleared.

Use the itinerary JSON in this doc as the seed data. Geocode the addresses once with a script (Nominatim, respecting its usage policy, 1 request/second, with a User-Agent), save the coordinates into the data file, and flag any stop that geocoded poorly so I can fix it. Do not invent coordinates.

Stack and constraints are in the "Tech approach" section. Make it work well on my phone, since I'll use it while walking. Read the whole doc first, then propose a short plan before writing code.
```

## What to build

One page, map plus side panel, driven by a JSON data file and saving my edits in the browser.

**Layout**

- Desktop: map fills the right \~60%, side panel on the left \~40%, both full height.
- Phone: map on top (\~45% of the screen), panel below as a scrollable sheet; a toggle to go full-map or full-panel.
- Day switcher as tabs or chips at the top of the panel; today's date auto-selected during the trip.

**Map**

- Numbered markers per stop for the selected day, colored by type (food, bookstore, museum, walk, transit, event, lodging).
- A line connecting stops in order; walking legs solid, transit and rides dashed.
- The three lodgings always visible as a distinct icon, labeled with their nights.
- Popup per marker: name, time, cost, a Google Maps link.
- "All days" view that shows every stop, colored by day.

**Side panel, per day**

- Header: day title, one-line summary, the day's spend, an "Open route in Google Maps" button.
- Timeline of stops: time, name, address (tappable map link), "Why", cost, and the travel leg to the next stop (mode, minutes, cost).
- Day notes box (free text).
- Collapsible "Budget" view: activities table, transport table, totals; totals recompute when I add activities with a cost.
- Collapsible "Book this" checklist and "Swaps if weather changes" list.

**Editing**

- Add activity: name, day, time, address or "pick on map", type, cost, why/note. New items get a different marker style so I can tell mine from the plan.
- Edit, delete, and drag to reorder stops within a day (the route line follows the new order).
- A note field on every stop, original or mine.
- Tick checklist items and mark a stop "done".
- Export and import everything as one JSON file; a "reset to original plan" button with confirmation.

**Done means**

- [ ] Every stop in the seed data appears on the right day, in order, at a sensible location.
- [ ] Notes, added activities, reorders and ticks survive a reload.
- [ ] Export, then clear storage, then import restores everything.
- [ ] Usable one-handed on a phone-width screen (\~390 px).
- [ ] Works offline once loaded, except the map tiles.

## Tech approach

Keep it small: one static page, no backend, no build step required, so it can live on GitHub Pages (or as a claude.ai artifact) and open instantly on a phone.

| Decision | Choice | Why |
| --- | --- | --- |
| Structure | `index.html` + `app.js` + `styles.css` + `data/itinerary.json`, or one self-contained HTML file | Nothing to install or run; trivially hostable. |
| Map | [Leaflet](https://leafletjs.com/) from a CDN | Free, no API key, mature, good on mobile. Google Maps JS needs a billed key. |
| Tiles | CARTO Positron or OpenStreetMap standard tiles, with attribution | Free for personal, low-traffic use; Positron is light and lets markers stand out. |
| Persistence | `localStorage` under one key, wrapped in try/catch, plus JSON export/import | No account or server; export/import covers cleared storage or switching phone and laptop. |
| User data | Stored as a separate layer over the seed: added stops, edits, order per day, notes, ticks | "Reset to original plan" stays easy, and updating the seed doesn't wipe my notes. |
| Geocoding | One-off Node or Python script against Nominatim, 1 req/s, with a User-Agent; results cached into `itinerary.json` | Coordinates are fetched once at build time, never at runtime; no key needed. |
| Fonts and style | Clean, readable, one accent color per day; no emoji | Used outdoors on a phone, so contrast and tap targets (44 px) matter. |

**Constraints**

- No API keys, no paid services, no analytics.
- Every address in the data must resolve; if Nominatim fails or lands far away (more than \~1.5 km from the neighborhood), mark `geocodeStatus: "check"` and list it in the console and in the README.
- Times are local Boston time. Daylight saving ends Sun Nov 1, 2026; show clock times as written, don't convert.
- Keep the "Open route in Google Maps" links exactly as given in the data.

## Data model

Two layers: the seed file (read-only plan) and the user layer (my changes, in localStorage and in exports). The app merges them at render time.

```json
{
  "trip": { "name": "Boston & Cambridge", "start": "2026-10-30", "end": "2026-11-05", "timezone": "America/New_York" },
  "lodging": [ { "id": "airbnb", "name": "...", "address": "...", "nights": ["2026-10-30", "2026-10-31"], "checkIn": "16:00", "checkOut": "11:00", "lat": null, "lng": null } ],
  "days": [
    {
      "date": "2026-10-30",
      "title": "Fri Oct 30: land, Harvard Square bookshops at dusk",
      "summary": "one or two sentences",
      "spend": "text, e.g. ~$15 to $25 plus the airport leg",
      "routeUrl": "Google Maps multi-stop link",
      "stops": [
        {
          "id": "fri-harvard-book-store",
          "time": "17:45",
          "name": "Harvard Book Store",
          "type": "bookstore | cafe | food | museum | walk | event | market | transit | lodging | cinema",
          "address": "1256 Massachusetts Ave, Cambridge, MA",
          "alternatives": [ { "name": "...", "address": "...", "why": "..." } ],
          "why": "why it was chosen",
          "cost": { "label": "Free to browse", "amountUsd": 0, "payAhead": false },
          "legToNext": { "mode": "walk | subway | bus | ride", "minutes": 3, "costUsd": 0, "text": "3 min walk" },
          "optional": false,
          "lat": null, "lng": null, "geocodeStatus": "ok | check"
        }
      ]
    }
  ],
  "budget": { "activities": [ ... ], "transport": [ ... ] },
  "bookings": [ { "id": "gardner", "text": "Gardner timed ticket, Wed Nov 4, 11:00 ($15)" } ],
  "swaps": [ "..." ]
}
```

User layer, stored under one localStorage key such as `bostonTrip.v1`:

```json
{
  "version": 1,
  "addedStops": [ { "id": "user-...", "date": "2026-11-01", "time": "19:30", "name": "...", "type": "food", "address": "...", "lat": 42.36, "lng": -71.06, "cost": { "amountUsd": 20 }, "note": "..." } ],
  "editedStops": { "fri-harvard-book-store": { "time": "18:00" } },
  "deletedStops": [ "sun-bobby-from-boston" ],
  "order": { "2026-11-01": [ "stop ids in my order" ] },
  "stopNotes": { "stop-id": "text" },
  "dayNotes": { "2026-11-01": "text" },
  "done": { "stop-id": true },
  "bookingsChecked": { "gardner": true }
}
```

A stop with no time (like the "→" travel rows in the itinerary doc) is not a stop: fold it into the previous stop's `legToNext`.

## Itinerary data

The full plan from the [itinerary doc](https://claude.ai/artifact/DR1ba72MYMvgUrznnBuHrc), as the seed file `data/itinerary.json`. Coordinates are left out on purpose: the geocoding script fills `lat`, `lng` and `geocodeStatus`. The happy hour location is unknown, so it has no address and no marker until I add one.

```json
{
  "trip": { "name": "Boston & Cambridge", "start": "2026-10-30", "end": "2026-11-05", "timezone": "America/New_York" },
  "lodging": [
    { "id": "airbnb", "name": "Airbnb", "address": "15 Holmes St, Cambridge, MA 02138", "nights": ["2026-10-30", "2026-10-31"], "checkIn": "16:00", "checkOut": "11:00" },
    { "id": "sonesta", "name": "Royal Sonesta Boston", "address": "40 Edwin Land Blvd, Cambridge, MA 02142", "nights": ["2026-11-01", "2026-11-02"], "checkIn": "16:00", "checkOut": "11:00" },
    { "id": "ginkgo", "name": "Ginkgo House on Harvard", "address": "288 Harvard St, Cambridge, MA 02139", "nights": ["2026-11-03", "2026-11-04"], "checkIn": "16:00", "checkOut": "05:00 departure" }
  ],
  "days": [
    {
      "date": "2026-10-30",
      "title": "Fri Oct 30: land, Harvard Square bookshops at dusk",
      "summary": "Short and close to the Airbnb: two bookstores, the Yard at golden hour, cheap dinner, early night.",
      "spend": "~$15 to $25 plus the airport leg",
      "routeUrl": "https://www.google.com/maps/dir/15+Holmes+St,+Cambridge,+MA+02138/Harvard+Yard,+Cambridge,+MA/Harvard+Book+Store,+1256+Massachusetts+Ave,+Cambridge,+MA/Grolier+Poetry+Book+Shop,+6+Plympton+St,+Cambridge,+MA/Clover+Food+Lab+Harvard+Square,+Cambridge,+MA",
      "stops": [
        { "id": "fri-logan", "time": "14:40", "name": "Land at Logan Airport", "type": "transit", "address": "Boston Logan International Airport, Boston, MA", "why": "If this is the international arrival, expect to be out around 15:45 to 16:15.", "cost": { "label": "", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "subway", "minutes": 70, "costUsd": 2.4, "text": "Free Silver Line SL1 to South Station, Red Line to Harvard, walk (~70 min, $2.40); or Uber 35 to 50 min (~$40 to $60)" } },
        { "id": "fri-airbnb", "time": "16:30", "name": "Check in at the Airbnb", "type": "lodging", "address": "15 Holmes St, Cambridge, MA 02138", "why": "Check-in opens 16:00.", "cost": { "label": "", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 20, "costUsd": 0, "text": "Walk to Harvard Square, ~15 to 25 min" } },
        { "id": "fri-harvard-yard", "time": "17:15", "name": "Harvard Yard", "type": "walk", "address": "Harvard Yard, Cambridge, MA", "why": "Sunset ~17:40: the one evening you get the Yard in golden light before the clock change. Widener Library, Memorial Church, John Harvard statue.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 3, "costUsd": 0, "text": "3 min walk" } },
        { "id": "fri-harvard-book-store", "time": "17:45", "name": "Harvard Book Store", "type": "bookstore", "address": "1256 Massachusetts Ave, Cambridge, MA", "why": "Independent since the 1930s, open late, with a used and remainder basement where books are cheap.", "cost": { "label": "Free to browse", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 3, "costUsd": 0, "text": "3 min walk" } },
        { "id": "fri-grolier", "time": "18:45", "name": "Grolier Poetry Book Shop", "type": "bookstore", "address": "6 Plympton St, Cambridge, MA", "why": "One of the oldest poetry-only bookstores in the US, one tiny room, on the way. May close around 19:00.", "optional": true, "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 4, "costUsd": 0, "text": "4 min walk" } },
        { "id": "fri-dinner", "time": "19:00", "name": "Dinner: Clover Food Lab", "type": "food", "address": "Clover Food Lab, Harvard Square, Cambridge, MA", "alternatives": [ { "name": "Mr. Bartley's Burger Cottage", "address": "1246 Massachusetts Ave, Cambridge, MA", "why": "Harvard Square institution since 1960, ~$20 to $25." } ], "why": "Local vegetarian chain, fast, ~$12 to $15, good after a flight.", "cost": { "label": "~$13 to $25", "amountUsd": 15, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 20, "costUsd": 0, "text": "Walk back to the Airbnb" } }
      ]
    },
    {
      "date": "2026-10-31",
      "title": "Sat Oct 31: Mount Auburn, Harvard, Athenaeum, Halloween on Beacon Hill",
      "summary": "Cambridge in the morning, Beacon Hill from early afternoon through Halloween night. The Athenaeum closes 17:00 Saturdays and is closed Sundays.",
      "spend": "~$12 (or $40) plus food and ~$5 in T fares",
      "routeUrl": "https://www.google.com/maps/dir/Simon%27s+Coffee+Shop,+1736+Massachusetts+Ave,+Cambridge,+MA/Mount+Auburn+Cemetery,+580+Mount+Auburn+St,+Cambridge,+MA/Harvard+Art+Museums,+32+Quincy+St,+Cambridge,+MA/Pinocchio%27s+Pizza,+74+Winthrop+St,+Cambridge,+MA/Boston+Athenaeum,+10+1%2F2+Beacon+St,+Boston,+MA/Panificio,+144+Charles+St,+Boston,+MA/Acorn+St,+Boston,+MA/Boston+Public+Garden,+Boston,+MA/Louisburg+Square,+Boston,+MA/Charles%2FMGH+Station,+Boston,+MA",
      "stops": [
        { "id": "sat-coffee", "time": "08:30", "name": "Coffee: Simon's Coffee Shop", "type": "cafe", "address": "1736 Massachusetts Ave, Cambridge, MA", "alternatives": [ { "name": "Tatte, Harvard Square", "address": "Tatte Bakery, Harvard Square, Cambridge, MA", "why": "Sit-down breakfast with pastries; pricier and busy." } ], "why": "Tiny, local, cheap, a Harvard-student favorite.", "cost": { "label": "~$5 to $15", "amountUsd": 7, "payAhead": false }, "legToNext": { "mode": "bus", "minutes": 10, "costUsd": 1.7, "text": "Bus 71 or 73 from Harvard, ~10 min, or a 25 min walk down Brattle St" } },
        { "id": "sat-mount-auburn", "time": "09:15", "name": "Mount Auburn Cemetery", "type": "walk", "address": "580 Mount Auburn St, Cambridge, MA", "why": "America's first garden cemetery (1831), a 175-acre arboretum at peak fall color. Climb Washington Tower for the skyline. Gardens, walks and architecture in one free stop. 1.5 h.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "bus", "minutes": 10, "costUsd": 1.7, "text": "Bus 71/73 back to Harvard, ~10 min" } },
        { "id": "sat-harvard-art-museums", "time": "11:00", "name": "Harvard Art Museums", "type": "museum", "address": "32 Quincy St, Cambridge, MA", "why": "Free, world-class collection, Renzo Piano's glass-roofed courtyard. The best free museum on the trip. 1.5 h.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 5, "costUsd": 0, "text": "5 min walk" } },
        { "id": "sat-lunch", "time": "12:30", "name": "Lunch: Pinocchio's Pizza", "type": "food", "address": "74 Winthrop St, Cambridge, MA", "why": "Cheap Sicilian slices, a Harvard Square institution; fast.", "cost": { "label": "~$8 to $12", "amountUsd": 10, "payAhead": false }, "legToNext": { "mode": "subway", "minutes": 15, "costUsd": 2.4, "text": "Red Line Harvard to Park Street, ~12 min + 3 min walk" } },
        { "id": "sat-athenaeum", "time": "14:00", "name": "Boston Athenaeum", "type": "museum", "address": "10 1/2 Beacon St, Boston, MA", "why": "Founded 1807. The ~$12 tour covers the building's story; the 5th-floor reading room is guaranteed only with the $40 day pass. Granary Burying Ground next door.", "cost": { "label": "~$12 tour or $40 day pass", "amountUsd": 12, "payAhead": true }, "legToNext": { "mode": "walk", "minutes": 10, "costUsd": 0, "text": "Walk past the State House up to Charles St, ~10 min" } },
        { "id": "sat-coffee-break", "time": "15:30", "name": "Coffee: Panificio", "type": "cafe", "address": "144 Charles St, Boston, MA", "alternatives": [ { "name": "Tatte, Charles St", "address": "Tatte Bakery, Charles Street, Boston, MA", "why": "If you liked it in the morning." }, { "name": "Beacon Hill Books & Cafe (browse)", "address": "71 Charles St, Boston, MA", "why": "Five-story townhouse bookstore; browsing is free." } ], "why": "Long-running neighborhood bakery-cafe, cheaper and more local.", "cost": { "label": "~$5 to $10", "amountUsd": 7, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 5, "costUsd": 0, "text": "5 min walk" } },
        { "id": "sat-acorn", "time": "16:15", "name": "Acorn St", "type": "walk", "address": "Acorn St, Boston, MA", "why": "Boston's most photographed cobblestone lane; go while there is light and before the crowd.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 8, "costUsd": 0, "text": "8 min walk" } },
        { "id": "sat-public-garden", "time": "16:45", "name": "Public Garden", "type": "walk", "address": "Boston Public Garden, Boston, MA", "why": "Lagoon, willows, Make Way for Ducklings statues, at dusk.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 5, "costUsd": 0, "text": "5 min walk" } },
        { "id": "sat-dinner", "time": "17:15", "name": "Dinner: The Paramount", "type": "food", "address": "44 Charles St, Boston, MA", "why": "Order-at-the-counter diner; the cheapest sit-down meal on Charles St, no reservation fight on Halloween.", "cost": { "label": "~$18 to $25", "amountUsd": 22, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 8, "costUsd": 0, "text": "8 min walk" } },
        { "id": "sat-halloween", "time": "18:15", "name": "Halloween on Beacon Hill (Louisburg Square, Pinckney, Mount Vernon, West Cedar)", "type": "event", "address": "Louisburg Square, Boston, MA", "why": "Mount Vernon and Pinckney close to cars ~16:00 to 20:00; residents compete on decorations. One night a year.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "subway", "minutes": 15, "costUsd": 2.4, "text": "Red Line Charles/MGH to Harvard, ~15 min, then walk" } }
      ]
    },
    {
      "date": "2026-11-01",
      "title": "Sun Nov 1: move hotels, South End, happy hour",
      "summary": "SoWa runs only on Sundays, so midday goes to the South End: market, Parkside and decorated brownstones within a 10-minute walk. Clocks fell back overnight.",
      "spend": "Free activities; $35 to $40 in rides or ~$5 by T",
      "routeUrl": "https://www.google.com/maps/dir/Porter+Square+Books,+25+White+St,+Cambridge,+MA/Royal+Sonesta+Boston,+40+Edwin+Land+Blvd,+Cambridge,+MA/SoWa+Vintage+Market,+450+Harrison+Ave,+Boston,+MA/Bobby+From+Boston,+19+Thayer+St,+Boston,+MA/South+End+Buttery,+314+Shawmut+Ave,+Boston,+MA/Union+Park,+Boston,+MA/Rutland+Square,+Boston,+MA/Parkside+Bookshop,+260+Shawmut+Ave,+Boston,+MA/Royal+Sonesta+Boston,+40+Edwin+Land+Blvd,+Cambridge,+MA",
      "stops": [
        { "id": "sun-breakfast", "time": "08:30", "name": "Breakfast: Page & Leaf at Porter Square Books", "type": "cafe", "address": "25 White St, Cambridge, MA", "alternatives": [ { "name": "Phinista", "address": "Phinista, Porter Square, Cambridge, MA", "why": "Vietnamese coffee shop, stronger drinks." } ], "why": "Coffee inside one of Cambridge's best indie bookstores.", "cost": { "label": "~$6 to $12", "amountUsd": 9, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 15, "costUsd": 0, "text": "Back to pack; check out by 11:00" } },
        { "id": "sun-checkout", "time": "10:15", "name": "Check out, ride to Royal Sonesta, drop bags", "type": "lodging", "address": "40 Edwin Land Blvd, Cambridge, MA 02142", "why": "With luggage the T means two lines and stairs; worth the ride.", "cost": { "label": "~$15 to $20 ride", "amountUsd": 18, "payAhead": false }, "legToNext": { "mode": "ride", "minutes": 15, "costUsd": 18, "text": "Uber to SoWa ~15 min (~$15 to $20), or Green Line + 15 min walk, 35 min ($2.40)" } },
        { "id": "sun-sowa", "time": "11:00", "name": "SoWa Vintage Market", "type": "market", "address": "450 Harrison Ave, Boston, MA", "why": "Weekly antiques and vintage market, Sundays 11:00 to 16:00 only, free entry, dozens of dealers.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 2, "costUsd": 0, "text": "2 min walk" } },
        { "id": "sun-bobby", "time": "12:00", "name": "Bobby from Boston", "type": "market", "address": "19 Thayer St, Boston, MA", "optional": true, "why": "Famous but mostly menswear; two minutes away, so a 15-minute look. Confirm Sunday hours.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 8, "costUsd": 0, "text": "8 min walk" } },
        { "id": "sun-brunch", "time": "12:30", "name": "Brunch: South End Buttery", "type": "food", "address": "314 Shawmut Ave, Boston, MA", "alternatives": [ { "name": "Flour Bakery", "address": "1595 Washington St, Boston, MA", "why": "Joanne Chang's bakery, cheaper (sticky bun + coffee ~$10), faster." } ], "why": "Neighborhood cafe-bakery on the same block as Parkside, real brunch plates.", "cost": { "label": "~$10 to $25", "amountUsd": 18, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 5, "costUsd": 0, "text": "5 min walk" } },
        { "id": "sun-decor", "time": "13:45", "name": "Halloween-decor stroll: Union Park, Rutland Square, Waltham St, Pembroke St", "type": "walk", "address": "Union Park, Boston, MA", "why": "Victorian bowfront rowhouses around oval gardens, still decorated. Best daylight for content. ~45 min.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 5, "costUsd": 0, "text": "5 min walk" } },
        { "id": "sun-parkside", "time": "14:45", "name": "Parkside Bookshop", "type": "bookstore", "address": "260 Shawmut Ave, Boston, MA", "why": "Opened 2024 in an 1800s building with tin ceilings and a working fireplace; a Boston Globe best bookstore of 2026.", "cost": { "label": "Free to browse", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "ride", "minutes": 15, "costUsd": 18, "text": "Uber back to the Sonesta ~15 min (~$15 to $20), or Orange + Green Line, 35 min ($2.40)" } },
        { "id": "sun-sonesta", "time": "16:00", "name": "Check in at Royal Sonesta, rest", "type": "lodging", "address": "40 Edwin Land Blvd, Cambridge, MA 02142", "why": "Sunset is now ~16:35.", "cost": { "label": "", "amountUsd": 0, "payAhead": false }, "legToNext": null },
        { "id": "sun-happy-hour", "time": "18:00", "name": "Creator happy hour (18:00 to 21:00)", "type": "event", "address": "", "why": "Location not set yet.", "cost": { "label": "", "amountUsd": 0, "payAhead": false }, "legToNext": null }
      ]
    },
    {
      "date": "2026-11-02",
      "title": "Mon Nov 2: summit day",
      "summary": "Sci comm summit, 8:30 to 21:00. Nothing else scheduled. Leave the Sonesta at 8:10.",
      "spend": "$0",
      "routeUrl": "https://www.google.com/maps/dir/Royal+Sonesta+Boston,+40+Edwin+Land+Blvd,+Cambridge,+MA/Museum+of+Science,+Boston,+MA/data=!4m2!4m1!3e2",
      "stops": [
        { "id": "mon-summit", "time": "08:30", "name": "Sci comm summit, Museum of Science", "type": "event", "address": "1 Museum of Science Driveway, Boston, MA", "why": "The reason for the trip. ~10 min walk from the Sonesta across the Charles River Dam.", "cost": { "label": "$0", "amountUsd": 0, "payAhead": false }, "legToNext": null }
      ]
    },
    {
      "date": "2026-11-03",
      "title": "Tue Nov 3: MIT, Brattle, North End, then the film",
      "summary": "MIT in the morning, downtown and the North End in the afternoon, You Can See Everything at night, 15 minutes' walk from Ginkgo House.",
      "spend": "About $25 in activities, $10 ride, $7 in T fares",
      "routeUrl": "https://www.google.com/maps/dir/Royal+Sonesta+Boston,+40+Edwin+Land+Blvd,+Cambridge,+MA/288+Harvard+St,+Cambridge,+MA+02139/MIT+Museum,+314+Main+St,+Cambridge,+MA/Ray+and+Maria+Stata+Center,+32+Vassar+St,+Cambridge,+MA/Killian+Court,+Cambridge,+MA/Kresge+Auditorium,+48+Massachusetts+Ave,+Cambridge,+MA/Flour+Bakery,+190+Massachusetts+Ave,+Cambridge,+MA/Brattle+Book+Shop,+9+West+St,+Boston,+MA/Boston+Public+Market,+100+Hanover+St,+Boston,+MA/Old+North+Church,+193+Salem+St,+Boston,+MA/Landmark+Kendall+Square+Cinema,+355+Binney+St,+Cambridge,+MA/288+Harvard+St,+Cambridge,+MA+02139",
      "stops": [
        { "id": "tue-breakfast", "time": "08:45", "name": "Breakfast: Shy Bird Kendall", "type": "cafe", "address": "390 Third St, Cambridge, MA", "alternatives": [ { "name": "Tatte, Kendall Square", "address": "Tatte Bakery, Kendall Square, Cambridge, MA", "why": "Quicker pastry and coffee." } ], "why": "~10 min walk from the Sonesta; proper cooked breakfast after the summit.", "cost": { "label": "~$10 to $18", "amountUsd": 14, "payAhead": false }, "legToNext": { "mode": "ride", "minutes": 10, "costUsd": 10, "text": "Check out 09:30; Uber with bags to Ginkgo House, ~10 min (~$10)" } },
        { "id": "tue-ginkgo-bags", "time": "09:45", "name": "Drop bags at Ginkgo House", "type": "lodging", "address": "288 Harvard St, Cambridge, MA 02139", "why": "Check-in is 16:00; dropping bags first avoids crossing back for them.", "cost": { "label": "", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 20, "costUsd": 0, "text": "Walk to MIT, ~20 min" } },
        { "id": "tue-mit-museum", "time": "10:15", "name": "MIT Museum", "type": "museum", "address": "314 Main St, Cambridge, MA", "why": "AI and robotics galleries, holography, MIT hacks; directly useful for content. Daily 10 to 17. 1.5 h.", "cost": { "label": "~$18 (ask about student rate)", "amountUsd": 18, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 8, "costUsd": 0, "text": "8 min walk" } },
        { "id": "tue-mit-walk", "time": "11:45", "name": "MIT architecture walk: Stata Center, Killian Court, Kresge and MIT Chapel", "type": "walk", "address": "32 Vassar St, Cambridge, MA", "why": "Gehry's Stata, the Great Dome, Saarinen's two 1955 buildings in one 45-minute free loop.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 5, "costUsd": 0, "text": "5 min walk up Mass Ave" } },
        { "id": "tue-lunch", "time": "12:45", "name": "Lunch: Flour Bakery Central", "type": "food", "address": "190 Massachusetts Ave, Cambridge, MA", "why": "On the way, fast, cheap sandwiches.", "cost": { "label": "~$12 to $15", "amountUsd": 13, "payAhead": false }, "legToNext": { "mode": "subway", "minutes": 12, "costUsd": 2.4, "text": "Red Line Central to Downtown Crossing, ~12 min" } },
        { "id": "tue-brattle", "time": "14:00", "name": "Brattle Book Shop", "type": "bookstore", "address": "9 West St, Boston, MA", "why": "Founded 1825; outdoor lot of $1 to $5 books, rare books on the third floor. Best bookstore for the budget. Mon to Sat until 17:30.", "cost": { "label": "$1 to $5 per book", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 15, "costUsd": 0, "text": "Walk past the Old State House and Faneuil Hall, ~15 min" } },
        { "id": "tue-coffee", "time": "15:15", "name": "Coffee: George Howell, Boston Public Market", "type": "cafe", "address": "100 Hanover St, Boston, MA", "why": "One of Boston's most respected roasters (Globe best coffee 2026), inside a free-to-browse food market.", "cost": { "label": "~$5", "amountUsd": 5, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 10, "costUsd": 0, "text": "10 min walk" } },
        { "id": "tue-north-end", "time": "15:45", "name": "North End: Hanover St, Old North Church, Copp's Hill at sunset", "type": "walk", "address": "193 Salem St, Boston, MA", "alternatives": [ { "name": "Caffè Vittoria (cannoli)", "address": "290 Hanover St, Boston, MA", "why": "Old-school pick over the tourist lines." } ], "why": "Boston's oldest neighborhood; viewing outside is free. Sunset ~16:30.", "cost": { "label": "Free (~$5 cannoli)", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "subway", "minutes": 20, "costUsd": 2.4, "text": "Green Line Haymarket to Park St, Red Line to Kendall/MIT, ~20 min" } },
        { "id": "tue-dinner", "time": "17:45", "name": "Dinner: The Friendly Toast or Flat Top Johnny's", "type": "food", "address": "One Kendall Square, Cambridge, MA", "why": "Same courtyard as the cinema entrance, zero transit before the film.", "cost": { "label": "~$18 to $25", "amountUsd": 22, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 2, "costUsd": 0, "text": "2 min walk" } },
        { "id": "tue-film", "time": "19:00", "name": "You Can See Everything (Landmark Kendall Square Cinema)", "type": "cinema", "address": "355 Binney St, Cambridge, MA", "why": "15 min walk from Ginkgo, $7 Tuesdays with free loyalty signup (usual $16.50 to $18), and the only free evening without a 05:00 alarm. 2 h 54 min. Nov 3 times not posted yet.", "cost": { "label": "$7 Tue (loyalty)", "amountUsd": 7, "payAhead": true }, "legToNext": { "mode": "walk", "minutes": 15, "costUsd": 0, "text": "Walk home to Ginkgo House, ~15 min" } }
      ]
    },
    {
      "date": "2026-11-04",
      "title": "Wed Nov 4: Michette, Gardner, BPL, Back Bay",
      "summary": "The Gardner is closed Tuesdays, so it lands today, with the free BPL and a Back Bay walk. Dinner doubles as the last bookstore.",
      "spend": "$15 in activities, ~$7 in T fares",
      "routeUrl": "https://www.google.com/maps/dir/288+Harvard+St,+Cambridge,+MA+02139/Michette+Bakery,+Inman+Square,+Cambridge,+MA/Fenway+Victory+Gardens,+Boston,+MA/Isabella+Stewart+Gardner+Museum,+25+Evans+Way,+Boston,+MA/Boston+Public+Library,+700+Boylston+St,+Boston,+MA/Trinity+Church,+206+Clarendon+St,+Boston,+MA/Commonwealth+Avenue+Mall,+Boston,+MA/Trident+Booksellers+%26+Cafe,+338+Newbury+St,+Boston,+MA",
      "stops": [
        { "id": "wed-michette", "time": "08:00", "name": "Breakfast: Michette", "type": "cafe", "address": "Michette Bakery, Inman Square, Cambridge, MA", "alternatives": [ { "name": "Cicada Coffee Bar", "address": "106 Prospect St, Cambridge, MA", "why": "Vietnamese coffee, Best of Boston pick, next to Ginkgo." } ], "why": "Small artisanal French bakery ~10 min from Ginkgo. Temporary hours Tue to Sun 8 to 14; confirm.", "cost": { "label": "~$8 to $12", "amountUsd": 10, "payAhead": false }, "legToNext": { "mode": "subway", "minutes": 35, "costUsd": 2.4, "text": "Red Line Central to Park St, Green Line E to Museum of Fine Arts, about 35 min; or Uber, 20 min (~$15)" } },
        { "id": "wed-fens", "time": "09:45", "name": "Fenway Victory Gardens and the Back Bay Fens", "type": "walk", "address": "Fenway Victory Gardens, Boston, MA", "why": "WWII community gardens inside Olmsted's Emerald Necklace; fills the time before the Gardner opens.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 8, "costUsd": 0, "text": "8 min walk" } },
        { "id": "wed-gardner", "time": "11:00", "name": "Isabella Stewart Gardner Museum", "type": "museum", "address": "25 Evans Way, Boston, MA", "why": "Venetian palazzo around a flowering courtyard, rooms as Isabella left them, the empty frames from the 1990 heist. The one paid museum worth it if you only do one. 2 h.", "cost": { "label": "$15 student", "amountUsd": 15, "payAhead": true }, "legToNext": { "mode": "subway", "minutes": 10, "costUsd": 2.4, "text": "Green Line E, Museum of Fine Arts to Copley, ~10 min" } },
        { "id": "wed-lunch", "time": "13:15", "name": "Quick lunch near Copley", "type": "food", "address": "Copley Square, Boston, MA", "why": "Keep it cheap; grab-and-go.", "cost": { "label": "~$12", "amountUsd": 12, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 3, "costUsd": 0, "text": "3 min walk" } },
        { "id": "wed-bpl", "time": "13:45", "name": "Boston Public Library, McKim Building", "type": "museum", "address": "700 Boylston St, Boston, MA", "why": "Free. Bates Hall, the Sargent murals, the Italianate courtyard: the public version of the Athenaeum. 1 h.", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 2, "costUsd": 0, "text": "2 min walk across Copley Square" } },
        { "id": "wed-trinity", "time": "15:00", "name": "Trinity Church", "type": "walk", "address": "206 Clarendon St, Boston, MA", "why": "H. H. Richardson's 1877 masterpiece. Exterior free; interior has a fee, skip on budget.", "cost": { "label": "Free outside", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 5, "costUsd": 0, "text": "5 min walk" } },
        { "id": "wed-comm-ave", "time": "15:30", "name": "Commonwealth Avenue Mall and Newbury St", "type": "walk", "address": "Commonwealth Avenue Mall, Boston, MA", "why": "Tree-lined boulevard of brownstones at dusk (sunset ~16:30).", "cost": { "label": "Free", "amountUsd": 0, "payAhead": false }, "legToNext": { "mode": "walk", "minutes": 15, "costUsd": 0, "text": "Walk up Newbury St" } },
        { "id": "wed-trident", "time": "17:00", "name": "Dinner and last bookstore: Trident Booksellers & Cafe", "type": "bookstore", "address": "338 Newbury St, Boston, MA", "why": "40-year-old bookstore with a full cafe serving dinner; last meal and last browse in one stop.", "cost": { "label": "~$18 to $25", "amountUsd": 22, "payAhead": false }, "legToNext": { "mode": "subway", "minutes": 30, "costUsd": 2.4, "text": "Green Line Hynes to Park St, Red Line to Central, walk 10 min (about 30 min total)" } }
      ]
    },
    {
      "date": "2026-11-05",
      "title": "Thu Nov 5: departure",
      "summary": "Leave Ginkgo House at 05:00 for the 08:00 flight; ride ~20 min ($35 to $50). Book it the night before.",
      "spend": "$35 to $50 ride",
      "routeUrl": "https://www.google.com/maps/dir/288+Harvard+St,+Cambridge,+MA+02139/Boston+Logan+International+Airport",
      "stops": [
        { "id": "thu-depart", "time": "05:00", "name": "Leave for Logan", "type": "transit", "address": "Boston Logan International Airport, Boston, MA", "why": "Arrive ~05:20 for an 08:00 international departure.", "cost": { "label": "$35 to $50 ride", "amountUsd": 42, "payAhead": false }, "legToNext": null }
      ]
    }
  ],
  "budget": {
    "activities": [
      { "item": "You Can See Everything, Landmark Kendall (Tue, loyalty)", "amountUsd": 7 },
      { "item": "Boston Athenaeum tour (or $40 day pass)", "amountUsd": 12 },
      { "item": "Gardner Museum, student", "amountUsd": 15 },
      { "item": "MIT Museum", "amountUsd": 18 }
    ],
    "transport": [
      { "item": "Logan to Airbnb (T / ride)", "lowUsd": 2.4, "highUsd": 60 },
      { "item": "Airbnb to Sonesta with bags (ride)", "lowUsd": 15, "highUsd": 20 },
      { "item": "Sonesta to SoWa and back", "lowUsd": 4.8, "highUsd": 40 },
      { "item": "Sonesta to Ginkgo with bags (ride)", "lowUsd": 0, "highUsd": 10 },
      { "item": "Ginkgo to Logan 05:00 (ride)", "lowUsd": 35, "highUsd": 50 },
      { "item": "Other subway rides (~10)", "lowUsd": 24, "highUsd": 24 }
    ],
    "notes": "Activities ~$52 per person (~$80 with the Athenaeum day pass). Transport ~$110 to $150 budget-leaning. Food not included."
  },
  "bookings": [
    { "id": "gardner", "text": "Gardner timed ticket, Wed Nov 4, 11:00 ($15)" },
    { "id": "athenaeum", "text": "Athenaeum tour, Sat Oct 31, ~14:00 (~$12), or decide on the $40 day pass" },
    { "id": "landmark", "text": "Landmark free loyalty signup; buy the film ticket when Tuesday's times appear" },
    { "id": "airport-ride", "text": "Ride to Logan, Thu Nov 5, 05:00, booked the night before" }
  ],
  "swaps": [
    "Rain on Saturday morning: Harvard Museum of Natural History (26 Oxford St, Cambridge) and its Glass Flowers instead of Mount Auburn (paid).",
    "Tired on Tuesday: skip the North End, go from Brattle straight to dinner in Kendall; the film stays.",
    "Film times don't fit Tuesday: Sunday ~21:30 after the happy hour at Landmark Kendall, full price.",
    "One more free museum: MIT List Visual Arts Center (20 Ames St, Cambridge), opens 12:00 Tue."
  ]
}
```

## Build steps and test checklist

Ask Claude Code to work in this order and show you the result after steps 2 and 4, so you can redirect early.

1. Save the JSON above as `data/itinerary.json` and validate it parses.
2. Write and run the geocoding script; print a table of every stop with its coordinates and status, and list the `check` ones. Fix those by hand (a more specific address or manual coordinates) before moving on.
3. Build the map and day switcher from the seed data only: markers, numbered route line, lodging icons, popups.
4. Build the side panel: day header, timeline, legs, Google Maps links, budget, bookings, swaps.
5. Add the user layer: notes, add/edit/delete, drag to reorder, done and checklist ticks, localStorage, export/import, reset.
6. Phone layout pass at \~390 px wide, then deploy (GitHub Pages or a claude.ai artifact).

**Test before the trip**

- [ ] Each day's markers match the order in the itinerary doc; nothing lands outside Boston/Cambridge.
- [ ] Add a stop on Sunday by clicking the map, give it a cost; it appears in the timeline and the budget total changes.
- [ ] Reorder two Tuesday stops; reload; the order and route line persist.
- [ ] Write a stop note and a day note; reload; both persist.
- [ ] Export, clear site data, import; everything comes back.
- [ ] Open on your phone over mobile data; the panel scrolls, buttons are easy to tap, and the route links open the Google Maps app.

**When the happy hour location arrives:** add it as a user stop on Sunday, or update its `address` in the seed and rerun the geocoding script.
