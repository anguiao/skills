#!/usr/bin/env python3
"""Fetch region boundaries from Nominatim and normalize them into GeoJSON."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_ENDPOINT = "https://nominatim.openstreetmap.org"
DEFAULT_USER_AGENT = "boundary-geojson/1.0 (+https://openstreetmap.org)"
POLYGON_GEOMETRY_TYPES = {"Polygon", "MultiPolygon"}
OSM_ID_PREFIXES = {"N", "W", "R"}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch an OpenStreetMap region boundary from Nominatim and write normalized GeoJSON."
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--query",
        help="Free-form search query, for example 'Shanghai, China'.",
    )
    source_group.add_argument(
        "--osm-id",
        dest="osm_ids",
        action="append",
        help="OSM object id with prefix, for example R913067. Repeat or pass comma-separated values.",
    )
    parser.add_argument(
        "--feature-type",
        choices=["country", "state", "city", "settlement"],
        help="Nominatim featureType filter for search mode.",
    )
    parser.add_argument(
        "--countrycodes",
        help="Comma-separated ISO 3166-1 alpha-2 country codes to hard-filter results.",
    )
    parser.add_argument(
        "--accept-language",
        help="Preferred result language, for example 'zh-CN,en'.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of search results to inspect before selection. Default: 5.",
    )
    parser.add_argument(
        "--pick",
        type=int,
        help="1-based index of the polygon candidate to export after filtering.",
    )
    parser.add_argument(
        "--all",
        dest="all_results",
        action="store_true",
        help="Export all polygon candidates instead of a single selected result.",
    )
    parser.add_argument(
        "--polygon-threshold",
        type=float,
        default=0.0,
        help="Geometry simplification tolerance in degrees passed to Nominatim. Default: 0.0.",
    )
    parser.add_argument(
        "--email",
        help="Contact email for larger or repeated jobs against the public service.",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"Base Nominatim endpoint. Default: {DEFAULT_ENDPOINT}",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"HTTP User-Agent to send. Default: {DEFAULT_USER_AGENT}",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds. Default: 30.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output file path. Defaults to stdout.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation for output. Default: 2.",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include the original Nominatim object under properties.nominatim_raw.",
    )
    args = parser.parse_args()

    if args.limit < 1 or args.limit > 40:
        fail("--limit must be between 1 and 40.")
    if args.pick is not None and args.pick < 1:
        fail("--pick must be a positive 1-based index.")
    if args.polygon_threshold < 0:
        fail("--polygon-threshold must be greater than or equal to 0.")

    return args


def fail(message: str, exit_code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(exit_code)


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def normalize_osm_ids(raw_values: list[str] | None) -> list[str]:
    normalized: list[str] = []
    for raw_value in raw_values or []:
        for item in raw_value.split(","):
            osm_id = item.strip().upper()
            if not osm_id:
                continue
            if len(osm_id) < 2 or osm_id[0] not in OSM_ID_PREFIXES or not osm_id[1:].isdigit():
                fail(f"Invalid --osm-id value: {item!r}. Use forms like R913067, W123456, or N987654.")
            normalized.append(osm_id)

    if len(normalized) > 50:
        fail("Nominatim lookup supports at most 50 OSM ids per request.")
    return normalized


def request_json(endpoint: str, path: str, params: dict[str, Any], user_agent: str, timeout: float) -> Any:
    url = f"{endpoint.rstrip('/')}{path}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": user_agent,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        fail(f"Nominatim returned HTTP {exc.code}: {body or exc.reason}", exit_code=1)
    except URLError as exc:
        fail(f"Unable to reach Nominatim: {exc.reason}", exit_code=1)


def build_search_params(args: argparse.Namespace) -> dict[str, Any]:
    params: dict[str, Any] = {
        "q": args.query,
        "format": "jsonv2",
        "polygon_geojson": 1,
        "addressdetails": 1,
        "extratags": 1,
        "namedetails": 1,
        "limit": args.limit,
        "dedupe": 1,
        "polygon_threshold": args.polygon_threshold,
    }
    if args.feature_type:
        params["featureType"] = args.feature_type
    if args.countrycodes:
        params["countrycodes"] = args.countrycodes
    if args.accept_language:
        params["accept-language"] = args.accept_language
    if args.email:
        params["email"] = args.email
    return params


def build_lookup_params(args: argparse.Namespace, osm_ids: list[str]) -> dict[str, Any]:
    params: dict[str, Any] = {
        "osm_ids": ",".join(osm_ids),
        "format": "jsonv2",
        "polygon_geojson": 1,
        "addressdetails": 1,
        "extratags": 1,
        "namedetails": 1,
        "polygon_threshold": args.polygon_threshold,
    }
    if args.accept_language:
        params["accept-language"] = args.accept_language
    if args.email:
        params["email"] = args.email
    return params


def is_polygon_candidate(item: dict[str, Any]) -> bool:
    geometry = item.get("geojson") or {}
    return geometry.get("type") in POLYGON_GEOMETRY_TYPES


def candidate_summary(index: int, item: dict[str, Any]) -> str:
    return (
        f"{index}. {to_osm_ref(item)} | "
        f"{item.get('display_name', '<unknown>')} | "
        f"type={item.get('type')} | "
        f"addresstype={item.get('addresstype')} | "
        f"place_rank={item.get('place_rank')} | "
        f"geometry={item.get('geojson', {}).get('type')}"
    )


def select_search_results(items: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    polygon_items = [item for item in items if is_polygon_candidate(item)]
    if not polygon_items:
        fail("The search returned no polygon boundary. Narrow the query or switch to --osm-id lookup.")

    if args.all_results:
        return polygon_items

    if args.pick is not None:
        if args.pick > len(polygon_items):
            lines = "\n".join(candidate_summary(idx, item) for idx, item in enumerate(polygon_items, start=1))
            fail(f"--pick {args.pick} is out of range.\nAvailable polygon candidates:\n{lines}")
        return [polygon_items[args.pick - 1]]

    if len(polygon_items) > 1:
        warn("Multiple polygon candidates matched the query; selecting the first result.")
        for idx, item in enumerate(polygon_items, start=1):
            warn(candidate_summary(idx, item))

    return [polygon_items[0]]


def select_lookup_results(
    items: list[dict[str, Any]],
    osm_ids: list[str],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    polygon_items = [item for item in items if is_polygon_candidate(item)]
    if not polygon_items:
        fail("The lookup returned no polygon geometry for the requested OSM ids.")

    if args.pick is not None:
        if args.pick > len(polygon_items):
            lines = "\n".join(candidate_summary(idx, item) for idx, item in enumerate(polygon_items, start=1))
            fail(f"--pick {args.pick} is out of range.\nAvailable polygon candidates:\n{lines}")
        return [polygon_items[args.pick - 1]]

    if args.all_results or len(osm_ids) > 1:
        return polygon_items

    return [polygon_items[0]]


def parse_bbox(raw_bbox: Any) -> list[float] | None:
    if not isinstance(raw_bbox, list) or len(raw_bbox) != 4:
        return None
    south, north, west, east = (float(value) for value in raw_bbox)
    return [west, south, east, north]


def union_bbox(features: list[dict[str, Any]]) -> list[float] | None:
    bboxes = [feature.get("bbox") for feature in features if feature.get("bbox")]
    if not bboxes:
        return None
    west = min(bbox[0] for bbox in bboxes)
    south = min(bbox[1] for bbox in bboxes)
    east = max(bbox[2] for bbox in bboxes)
    north = max(bbox[3] for bbox in bboxes)
    return [west, south, east, north]


def clean_mapping(values: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in values.items():
        if value in (None, "", [], {}):
            continue
        cleaned[key] = value
    return cleaned


def to_osm_ref(item: dict[str, Any]) -> str:
    osm_type = item.get("osm_type")
    prefix = {
        "node": "N",
        "way": "W",
        "relation": "R",
    }.get(osm_type)
    if not prefix:
        return str(item.get("osm_id", ""))
    return f"{prefix}{item.get('osm_id')}"


def normalize_feature(item: dict[str, Any], include_raw: bool) -> dict[str, Any]:
    bbox = parse_bbox(item.get("boundingbox"))
    properties = clean_mapping(
        {
            "display_name": item.get("display_name"),
            "name": item.get("name"),
            "osm_type": item.get("osm_type"),
            "osm_id": item.get("osm_id"),
            "category": item.get("category"),
            "type": item.get("type"),
            "addresstype": item.get("addresstype"),
            "place_rank": item.get("place_rank"),
            "importance": item.get("importance"),
            "center": [float(item["lon"]), float(item["lat"])] if item.get("lon") and item.get("lat") else None,
            "address": item.get("address"),
            "namedetails": item.get("namedetails"),
            "extratags": item.get("extratags"),
            "licence": item.get("licence"),
        }
    )
    if include_raw:
        properties["nominatim_raw"] = item

    feature = {
        "type": "Feature",
        "id": to_osm_ref(item),
        "properties": properties,
        "geometry": item.get("geojson"),
    }
    if bbox:
        feature["bbox"] = bbox
    return feature


def build_collection(
    features: list[dict[str, Any]],
    args: argparse.Namespace,
    mode: str,
    osm_ids: list[str],
) -> dict[str, Any]:
    collection = {
        "type": "FeatureCollection",
        "features": features,
        "nominatim": clean_mapping(
            {
                "endpoint": args.endpoint.rstrip("/"),
                "mode": mode,
                "query": args.query,
                "osm_ids": osm_ids if osm_ids else None,
                "feature_type": args.feature_type,
                "countrycodes": args.countrycodes,
                "accept_language": args.accept_language,
                "polygon_threshold": args.polygon_threshold,
                "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        ),
    }
    bbox = union_bbox(features)
    if bbox:
        collection["bbox"] = bbox
    if args.query:
        collection["name"] = args.query
    elif osm_ids:
        collection["name"] = ",".join(osm_ids)
    return collection


def write_output(payload: dict[str, Any], output_path: Path | None, indent: int) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=indent)
    if output_path is None:
        print(serialized)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{serialized}\n", encoding="utf-8")


def main() -> None:
    configure_stdio()
    args = parse_args()
    osm_ids = normalize_osm_ids(args.osm_ids)

    if args.query:
        items = request_json(
            endpoint=args.endpoint,
            path="/search",
            params=build_search_params(args),
            user_agent=args.user_agent,
            timeout=args.timeout,
        )
        selected_items = select_search_results(list(items), args)
        mode = "search"
    else:
        items = request_json(
            endpoint=args.endpoint,
            path="/lookup",
            params=build_lookup_params(args, osm_ids),
            user_agent=args.user_agent,
            timeout=args.timeout,
        )
        selected_items = select_lookup_results(list(items), osm_ids, args)
        mode = "lookup"

    features = [normalize_feature(item, include_raw=args.include_raw) for item in selected_items]
    payload = build_collection(features, args, mode=mode, osm_ids=osm_ids)
    write_output(payload, args.out, args.indent)


if __name__ == "__main__":
    main()
