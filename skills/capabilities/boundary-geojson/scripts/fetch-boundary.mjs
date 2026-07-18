#!/usr/bin/env node

import { mkdir, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { parseArgs } from 'node:util'

const DEFAULT_URL = 'https://nominatim.openstreetmap.org'
const POLYGONS = new Set(['Polygon', 'MultiPolygon'])
const FEATURE_TYPES = new Set(['country', 'state', 'city', 'settlement'])

const { positionals, values } = parseArgs({
  allowPositionals: true,
  options: {
    all: { type: 'boolean', short: 'a' },
    country: { type: 'string', short: 'c' },
    help: { type: 'boolean', short: 'h' },
    language: { type: 'string', short: 'l' },
    out: { type: 'string', short: 'o' },
    pick: { type: 'string', short: 'p' },
    raw: { type: 'boolean' },
    simplify: { type: 'string', short: 's' },
    type: { type: 'string', short: 't' },
  },
  strict: true,
})

if (values.help) {
  console.log(`Usage:
  fetch-boundary.mjs <place|OSM-id[,OSM-id...]> [options]

Examples:
  fetch-boundary.mjs "Shanghai, China" --type state -o shanghai.geojson
  fetch-boundary.mjs R913067 -o shanghai.geojson

Options:
  -t, --type <type>       country, state, city, or settlement
  -c, --country <codes>   ISO 3166-1 alpha-2 codes, comma-separated
  -l, --language <value>  Preferred response language
  -p, --pick <number>     Select a polygon candidate (1-based)
  -a, --all               Export every polygon candidate
  -s, --simplify <value>  Nominatim polygon simplification tolerance
  -o, --out <path>        Output file path (required)
      --raw               Keep the complete Nominatim response per feature
  -h, --help              Show this help`)
  process.exit(0)
}

function fail(message) {
  throw new Error(message)
}

function osmRef(item) {
  const prefix = { node: 'N', relation: 'R', way: 'W' }[item.osm_type] ?? ''
  return `${prefix}${item.osm_id}`
}

function compact(object) {
  return Object.fromEntries(
    Object.entries(object).filter(([, value]) => value != null && value !== ''),
  )
}

function bbox(item) {
  if (!Array.isArray(item.boundingbox) || item.boundingbox.length !== 4)
    return undefined

  const [south, north, west, east] = item.boundingbox.map(Number)
  return [west, south, east, north]
}

function normalize(item) {
  return compact({
    type: 'Feature',
    id: osmRef(item),
    bbox: bbox(item),
    properties: compact({
      name: item.name,
      display_name: item.display_name,
      osm_type: item.osm_type,
      osm_id: item.osm_id,
      category: item.category,
      type: item.type,
      addresstype: item.addresstype,
      place_rank: item.place_rank,
      importance: item.importance,
      center: item.lon && item.lat ? [Number(item.lon), Number(item.lat)] : undefined,
      address: item.address,
      namedetails: item.namedetails,
      extratags: item.extratags,
      licence: item.licence,
      nominatim_raw: values.raw ? item : undefined,
    }),
    geometry: item.geojson,
  })
}

function collectionBbox(features) {
  const boxes = features.flatMap(feature => feature.bbox ? [feature.bbox] : [])
  if (!boxes.length)
    return undefined

  return [
    Math.min(...boxes.map(box => box[0])),
    Math.min(...boxes.map(box => box[1])),
    Math.max(...boxes.map(box => box[2])),
    Math.max(...boxes.map(box => box[3])),
  ]
}

function select(items) {
  const polygons = items.filter(item => POLYGONS.has(item.geojson?.type))
  if (!polygons.length)
    fail('No polygon boundary found. Narrow the place name or use a canonical OSM id.')

  if (values.all)
    return polygons

  const pick = values.pick == null ? 1 : Number(values.pick)
  if (!Number.isInteger(pick) || pick < 1 || pick > polygons.length)
    fail(`--pick must be between 1 and ${polygons.length}.`)

  if (values.pick == null && polygons.length > 1) {
    console.error('Multiple polygon candidates found; using the first:')
    polygons.forEach((item, index) => {
      console.error(`${index + 1}. ${osmRef(item)} | ${item.display_name}`)
    })
  }

  return [polygons[pick - 1]]
}

async function main() {
  if (positionals.length !== 1)
    fail('Pass exactly one quoted place name or comma-separated OSM id list. Use --help for examples.')
  if (!values.out)
    fail('--out is required.')

  const input = positionals[0]
  const osmIds = input.toUpperCase().split(',').map(id => id.trim())
  const lookup = osmIds.every(id => /^[NWR]\d+$/.test(id))
  const simplify = values.simplify ?? '0'
  if (values.type && !FEATURE_TYPES.has(values.type))
    fail('--type must be country, state, city, or settlement.')
  if (!Number.isFinite(Number(simplify)) || Number(simplify) < 0)
    fail('--simplify must be a non-negative number.')

  const params = new URLSearchParams({
    addressdetails: '1',
    extratags: '1',
    format: 'jsonv2',
    namedetails: '1',
    polygon_geojson: '1',
    polygon_threshold: simplify,
  })

  if (lookup) {
    if (osmIds.length > 50)
      fail('Nominatim accepts at most 50 OSM ids per lookup.')
    params.set('osm_ids', osmIds.join(','))
  }
  else {
    params.set('q', input)
    params.set('limit', '5')
    if (values.type)
      params.set('featureType', values.type)
    if (values.country)
      params.set('countrycodes', values.country)
  }

  if (values.language)
    params.set('accept-language', values.language)
  if (process.env.NOMINATIM_EMAIL)
    params.set('email', process.env.NOMINATIM_EMAIL)

  const endpoint = process.env.NOMINATIM_URL ?? DEFAULT_URL
  const url = `${endpoint.replace(/\/$/, '')}/${lookup ? 'lookup' : 'search'}?${params}`
  const response = await fetch(url, {
    headers: {
      accept: 'application/json',
      'user-agent': process.env.NOMINATIM_USER_AGENT ?? 'boundary-geojson/2.0',
    },
    signal: AbortSignal.timeout(30_000),
  })

  if (!response.ok)
    fail(`Nominatim returned HTTP ${response.status}: ${await response.text()}`)

  const features = select(await response.json()).map(normalize)
  const output = compact({
    type: 'FeatureCollection',
    name: input,
    bbox: collectionBbox(features),
    features,
  })
  const json = `${JSON.stringify(output, null, 2)}\n`

  await mkdir(dirname(values.out), { recursive: true })
  await writeFile(values.out, json)
}

main().catch((error) => {
  console.error(`error: ${error.message}`)
  process.exitCode = 1
})
