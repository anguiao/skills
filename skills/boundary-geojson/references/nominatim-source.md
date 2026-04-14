# Current Source: Nominatim

## Endpoints

- Search: `https://nominatim.openstreetmap.org/search`
- Lookup: `https://nominatim.openstreetmap.org/lookup`

Use `search` for free-form place names and `lookup` when you already have OSM ids like `R913067`.

## Recommended Parameters

For boundary fetches, prefer:

- `format=jsonv2`
- `polygon_geojson=1`
- `addressdetails=1`
- `extratags=1`
- `namedetails=1`

Useful narrowing parameters:

- `featureType=country|state|city|settlement`
- `countrycodes=cn,us,...`
- `accept-language=zh-CN,en`
- `polygon_threshold=<float>`

Useful identification parameters:

- `email=<address>` for larger request volumes
- `osm_ids=R913067,W123456`

## Response Notes

- `search` and `lookup` both support `jsonv2`, `geojson`, and `geocodejson`.
- `jsonv2` is convenient when you want the raw Nominatim metadata and polygon geometry together.
- `boundingbox` in Nominatim responses is ordered as `[south, north, west, east]`.
- GeoJSON `bbox` must be ordered as `[west, south, east, north]`.
- `geocodejson` has more stable address classification, but `jsonv2` is usually easier when you need the original Nominatim metadata fields in the output.

## Public Usage Constraints

The public OSM Foundation service is limited. At the time of writing:

- Stay at or below 1 request per second.
- Send a valid custom `User-Agent` or `Referer`.
- Cache repeated queries on your side.
- Do not implement autocomplete against the public endpoint.
- Do not use the public endpoint for systematic bulk crawling.

If the task needs exhaustive lists of features in an area, use Overpass or an OSM extract instead of Nominatim search.

## Source Links

- Search API: <https://nominatim.org/release-docs/latest/api/Search/>
- Lookup API: <https://nominatim.org/release-docs/latest/api/Lookup/>
- Usage policy: <https://operations.osmfoundation.org/policies/nominatim/>
