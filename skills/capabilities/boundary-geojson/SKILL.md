---
name: boundary-geojson
description: Fetch or derive administrative or regional boundaries and normalize them into GeoJSON. Use when Codex needs to look up a country, province, state, city, county, district, municipality, or other area boundary; disambiguate place candidates from a geocoder; fetch a boundary by canonical area identifier; or save the result as GeoJSON for mapping, GIS, spatial analysis, or downstream APIs.
---

# Boundary GeoJSON

## Goal

Fetch a polygon boundary from the current configured source and return a normalized GeoJSON `FeatureCollection`.

Use this skill for "find the boundary for this region" tasks. The current bundled script uses OpenStreetMap Nominatim as the default source, but the skill name stays source-agnostic so the implementation can change later without renaming the skill. If the user wants exhaustive POIs, bulk geocoding, or all OSM features inside an area, switch to Overpass or another extract source instead of stretching a geocoder search endpoint beyond its intended use.

## Quick Start

1. Prefer `python scripts/fetch_boundary.py --query "<place>" --feature-type <type>` for country, province, state, or city requests.
2. Prefer `python scripts/fetch_boundary.py --osm-id R<id>` when the user already has an OSM object id.
3. Save the result with `--out <path>` and inspect the chosen feature before handing it off.

Examples:

```bash
python scripts/fetch_boundary.py \
  --query "Shanghai, China" \
  --feature-type state \
  --out shanghai.geojson
```

```bash
python scripts/fetch_boundary.py \
  --query "Sichuan, China" \
  --feature-type state \
  --countrycodes cn \
  --polygon-threshold 0.001 \
  --out sichuan.geojson
```

```bash
python scripts/fetch_boundary.py \
  --osm-id R913067 \
  --out shanghai.geojson
```

## Workflow

### 1. Choose the request mode

- Use `--query` for free-form place names or addresses.
- Use `--osm-id` for direct lookups like `R913067`, `W123456`, or `N987654`.
- Add `--feature-type country|state|city|settlement` whenever the target is a standard administrative level and the query is ambiguous.
- Add `--countrycodes <iso2[,iso2...]>` when the place name exists in multiple countries.

### 2. Keep the result boundary-shaped

- The script requests `polygon_geojson=1` and keeps only `Polygon` or `MultiPolygon` results.
- Use `--polygon-threshold` to simplify very large geometries before saving them.
- If the first result is ambiguous, rerun with `--pick <n>` after checking the warning output, or use `--all` to export all polygon candidates as one collection.

### 3. Validate the selected feature

- Check `features[0].properties.display_name`, `osm_type`, `osm_id`, `addresstype`, and `place_rank`.
- Confirm the output `bbox` matches the expected region.
- If the user needs a stable OSM reference, use the feature `id` such as `R913067`.

### 4. Respect the public service limits

- Use a real `User-Agent`. The script already sends one by default; override it with `--user-agent` if the calling project has its own identifier.
- Stay at or below one request per second against the public `nominatim.openstreetmap.org` service.
- Use `--email` for larger or repeated jobs on the public service.
- Cache repeated lookups in the calling workflow when possible.
- Do not build autocomplete or bulk crawling flows on top of the public endpoint.

## Output Shape

The script always writes a GeoJSON `FeatureCollection`.

- Top-level `bbox` follows GeoJSON order: `[west, south, east, north]`.
- Each feature has an `id` like `R913067`.
- Each feature `properties` block keeps the most useful Nominatim metadata: `display_name`, `name`, `osm_type`, `osm_id`, `category`, `type`, `addresstype`, `place_rank`, `importance`, `center`, `address`, `namedetails`, `extratags`, and `licence`.
- The top-level `nominatim` object records how the collection was generated.

## Resources

- Run `scripts/fetch_boundary.py` to fetch and normalize boundaries.
- Read `references/nominatim-source.md` when you need current-source parameter details, response-field notes, or the public usage constraints.

## Notes

- Keep the workflow deterministic: narrow the query first, then fetch, then validate the chosen feature.
- Prefer direct lookup by OSM id when the user already provides a canonical relation or way reference.
- If the user needs all features of a certain type inside an area, stop and switch tools instead of misusing Nominatim search.
