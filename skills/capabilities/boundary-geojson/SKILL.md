---
name: boundary-geojson
description: Fetch administrative or regional boundaries and save normalized GeoJSON. Use when Codex needs a country, province, state, city, county, district, municipality, or other area boundary for maps, GIS, spatial analysis, or downstream APIs, including lookup by place name or canonical OSM id.
---

# Boundary GeoJSON

Fetch polygon boundaries from Nominatim and return a GeoJSON `FeatureCollection`.

## Run

Use Node.js 20 or newer. Pass a quoted place name or an OSM id as the only positional argument, and always provide an output file:

```bash
node scripts/fetch-boundary.mjs "Shanghai, China" --type state --out shanghai.geojson
node scripts/fetch-boundary.mjs R913067 --out shanghai.geojson
```

Add `--country cn` to exclude candidates outside China when a place name exists in multiple countries. It does not resolve duplicate names within the same country. If multiple polygons still match, inspect the candidates printed to stderr and rerun with `--pick <n>`. Use `--all` only when every matching polygon is wanted.

Run `node scripts/fetch-boundary.mjs --help` for the complete CLI.

## Validate

Before handing off the file, confirm:

- `features[0].properties.display_name` names the intended place.
- `features[0].id` is the expected OSM object when a canonical id is known.
- The top-level `bbox` is plausible and ordered `[west, south, east, north]`.
- Every geometry is a `Polygon` or `MultiPolygon`.

## Source constraints

The public Nominatim service requires a recognizable user agent and no more than one request per second. Set `NOMINATIM_USER_AGENT` for the calling project and `NOMINATIM_EMAIL` for repeated use. Cache repeated queries. Do not use this workflow for autocomplete, bulk crawling, POI enumeration, or all features inside an area; use Overpass or an OSM extract for those tasks.

Read [references/nominatim-source.md](references/nominatim-source.md) only when source parameters or policy details matter.
