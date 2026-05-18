"""Build a standalone HTML visualization of the local music graph toplists."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from common import AUDIO_EXTS, DATA_ROOT, PROJECT_ROOT, ZENE
from build_toplists import (
    compute_adjusted_scores,
    compute_normalized_scores,
    compute_top_region,
    load_json,
    load_region_overrides,
)

OUT_PATH = PROJECT_ROOT / "index.html"


# === US Continental outline (from world.geo.json) ===
US_CONTINENTAL = [[-94.81758,49.38905],[-94.64,48.84],[-94.32914,48.67074],[-93.63087,48.60926],[-92.61,48.45],[-91.64,48.14],[-90.83,48.27],[-89.6,48.01],[-89.272917,48.019808],[-88.378114,48.302918],[-87.439793,47.94],[-86.461991,47.553338],[-85.652363,47.220219],[-84.87608,46.900083],[-84.779238,46.637102],[-84.543749,46.538684],[-84.6049,46.4396],[-84.3367,46.40877],[-84.14212,46.512226],[-84.091851,46.275419],[-83.890765,46.116927],[-83.616131,46.116927],[-83.469551,45.994686],[-83.592851,45.816894],[-82.550925,45.347517],[-82.337763,44.44],[-82.137642,43.571088],[-82.43,42.98],[-82.9,42.43],[-83.12,42.08],[-83.142,41.975681],[-83.02981,41.832796],[-82.690089,41.675105],[-82.439278,41.675105],[-81.277747,42.209026],[-80.247448,42.3662],[-78.939362,42.863611],[-78.92,42.965],[-79.01,43.27],[-79.171674,43.466339],[-78.72028,43.625089],[-77.737885,43.629056],[-76.820034,43.628784],[-76.5,44.018459],[-76.375,44.09631],[-75.31821,44.81645],[-74.867,45.00048],[-73.34783,45.00738],[-71.50506,45.0082],[-71.405,45.255],[-71.08482,45.30524],[-70.66,45.46],[-70.305,45.915],[-69.99997,46.69307],[-69.237216,47.447781],[-68.905,47.185],[-68.23444,47.35486],[-67.79046,47.06636],[-67.79134,45.70281],[-67.13741,45.13753],[-66.96466,44.8097],[-68.03252,44.3252],[-69.06,43.98],[-70.11617,43.68405],[-70.645476,43.090238],[-70.81489,42.8653],[-70.825,42.335],[-70.495,41.805],[-70.08,41.78],[-70.185,42.145],[-69.88497,41.92283],[-69.96503,41.63717],[-70.64,41.475],[-71.12039,41.49445],[-71.86,41.32],[-72.295,41.27],[-72.87643,41.22065],[-73.71,40.931102],[-72.24126,41.11948],[-71.945,40.93],[-73.345,40.63],[-73.982,40.628],[-73.952325,40.75075],[-74.25671,40.47351],[-73.96244,40.42763],[-74.17838,39.70926],[-74.90604,38.93954],[-74.98041,39.1964],[-75.20002,39.24845],[-75.52805,39.4985],[-75.32,38.96],[-75.071835,38.782032],[-75.05673,38.40412],[-75.37747,38.01551],[-75.94023,37.21689],[-76.03127,37.2566],[-75.72205,37.93705],[-76.23287,38.319215],[-76.35,39.15],[-76.542725,38.717615],[-76.32933,38.08326],[-76.989998,38.239992],[-76.30162,37.917945],[-76.25874,36.9664],[-75.9718,36.89726],[-75.86804,36.55125],[-75.72749,35.55074],[-76.36318,34.80854],[-77.397635,34.51201],[-78.05496,33.92547],[-78.55435,33.86133],[-79.06067,33.49395],[-79.20357,33.15839],[-80.301325,32.509355],[-80.86498,32.0333],[-81.33629,31.44049],[-81.49042,30.72999],[-81.31371,30.03552],[-80.98,29.18],[-80.535585,28.47213],[-80.53,28.04],[-80.056539,26.88],[-80.088015,26.205765],[-80.13156,25.816775],[-80.38103,25.20616],[-80.68,25.08],[-81.17213,25.20126],[-81.33,25.64],[-81.71,25.87],[-82.24,26.73],[-82.70515,27.49504],[-82.85526,27.88624],[-82.65,28.55],[-82.93,29.1],[-83.70959,29.93656],[-84.1,30.09],[-85.10882,29.63615],[-85.28784,29.68612],[-85.7731,30.15261],[-86.4,30.4],[-87.53036,30.27433],[-88.41782,30.3849],[-89.18049,30.31598],[-89.593831,30.159994],[-89.413735,29.89419],[-89.43,29.48864],[-89.21767,29.29108],[-89.40823,29.15961],[-89.77928,29.30714],[-90.15463,29.11743],[-90.880225,29.148535],[-91.626785,29.677],[-92.49906,29.5523],[-93.22637,29.78375],[-93.84842,29.71363],[-94.69,29.48],[-95.60026,28.73863],[-96.59404,28.30748],[-97.14,27.83],[-97.37,27.38],[-97.38,26.69],[-97.33,26.21],[-97.14,25.87],[-97.53,25.84],[-98.24,26.06],[-99.02,26.37],[-99.3,26.84],[-99.52,27.54],[-100.11,28.11],[-100.45584,28.69612],[-100.9576,29.38071],[-101.6624,29.7793],[-102.48,29.76],[-103.11,28.97],[-103.94,29.27],[-104.45697,29.57196],[-104.70575,30.12173],[-105.03737,30.64402],[-105.63159,31.08383],[-106.1429,31.39995],[-106.50759,31.75452],[-108.24,31.754854],[-108.24194,31.34222],[-109.035,31.34194],[-111.02361,31.33472],[-113.30498,32.03914],[-114.815,32.52528],[-114.72139,32.72083],[-115.99135,32.61239],[-117.12776,32.53534],[-117.295938,33.046225],[-117.944,33.621236],[-118.410602,33.740909],[-118.519895,34.027782],[-119.081,34.078],[-119.438841,34.348477],[-120.36778,34.44711],[-120.62286,34.60855],[-120.74433,35.15686],[-121.71457,36.16153],[-122.54747,37.55176],[-122.51201,37.78339],[-122.95319,38.11371],[-123.7272,38.95166],[-123.86517,39.76699],[-124.39807,40.3132],[-124.17886,41.14202],[-124.2137,41.99964],[-124.53284,42.76599],[-124.14214,43.70838],[-124.020535,44.615895],[-123.89893,45.52341],[-124.079635,46.86475],[-124.39567,47.72017],[-124.68721,48.184433],[-124.566101,48.379715],[-123.12,48.04],[-122.58736,47.096],[-122.34,47.36],[-122.5,48.18],[-122.84,49],[-120,49],[-117.03121,49],[-116.04818,49],[-113,49],[-110.05,49],[-107.05,49],[-104.04826,48.99986],[-100.65,49],[-97.22872,49.0007],[-95.15907,49],[-95.15609,49.38425],[-94.81758,49.38905]]

# === Hungary outline ===
HU_OUTLINE_COORDS = [[16.202298,46.852386],[16.534268,47.496171],[16.340584,47.712902],[16.903754,47.714866],[16.979667,48.123497],[17.488473,47.867466],[17.857133,47.758429],[18.696513,47.880954],[18.777025,48.081768],[19.174365,48.111379],[19.661364,48.266615],[19.769471,48.202691],[20.239054,48.327567],[20.473562,48.56285],[20.801294,48.623854],[21.872236,48.319971],[22.085608,48.422264],[22.64082,48.15024],[22.710531,47.882194],[22.099768,47.672439],[21.626515,46.994238],[21.021952,46.316088],[20.220192,46.127469],[19.596045,46.17173],[18.829838,45.908878],[18.456062,45.759481],[17.630066,45.951769],[16.882515,46.380632],[16.564808,46.503751],[16.370505,46.841327],[16.202298,46.852386]]

# US region geographic coordinates
US_REGION_GEO = {
    "New York":     (-74.0, 40.7),
    "Atlanta":      (-84.4, 33.8),
    "Chicago":      (-87.6, 41.9),
    "Louisiana":    (-91.2, 30.5),
    "Florida":      (-81.5, 27.5),
    "California":   (-119.4, 36.8),
    "Detroit":      (-83.0, 42.3),
    "Memphis":      (-90.0, 35.1),
    "Texas":        (-97.7, 31.0),
    "Philadelphia": (-75.2, 40.0),
    "Toronto":      (-79.4, 43.7),
    "DC":           (-77.0, 38.9),
    "USA":          (-98.0, 39.5),
    "USA Other":    (-105.0, 39.5),
}

# Hungarian city coordinates
HU_CITY_GEO = {
    "Budapest":     (19.04, 47.50),
    "Győr":         (17.63, 47.68),
    "Kapuvár":      (17.03, 47.60),
    "Kecskemét":    (19.69, 46.90),
    "Pápa":         (17.47, 47.33),
    "Tatabánya":    (18.39, 47.58),
    "Almásfüzitő":  (18.32, 47.72),
    "Gyöngyös":     (19.93, 47.78),
    "Eger":         (20.38, 47.90),
    "Surány":       (19.17, 48.09),
    "Ózd":          (20.29, 48.22),
    "Veszprém":     (17.91, 47.09),
    "Somogy":       (17.79, 46.35),
    "Pécs":         (18.23, 46.07),
    "Szeged":       (20.15, 46.25),
}


def project_coords(coords, viewbox, padding=30):
    W, H = viewbox
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    def proj(lon, lat):
        x = padding + (lon - min_lon) / (max_lon - min_lon) * (W - 2 * padding)
        y = padding + (max_lat - lat) / (max_lat - min_lat) * (H - 2 * padding)
        return round(x, 1), round(y, 1)

    return proj, (min_lon, max_lon, min_lat, max_lat)


def coords_to_svg_path(coords, proj_fn):
    parts = []
    for i, (lon, lat) in enumerate(coords):
        x, y = proj_fn(lon, lat)
        parts.append(f"{'M' if i == 0 else 'L'}{x},{y}")
    parts.append("Z")
    return " ".join(parts)


def project_points(points_dict, proj_fn):
    result = {}
    for name, (lon, lat) in points_dict.items():
        x, y = proj_fn(lon, lat)
        result[name] = {"x": x, "y": y}
    return result




def export_persons(area: str) -> list[dict]:
    base = DATA_ROOT / area / "normalized"
    persons = load_json(base / "persons.json")
    groups = load_json(base / "groups.json") if (base / "groups.json").exists() else {}
    songs = load_json(base / "songs.json")
    song_map = {s["song_id"]: s for s in songs}
    person_overrides, _ = load_region_overrides(area)

    norm = compute_normalized_scores(songs, groups)
    adj = compute_adjusted_scores(songs, groups)

    ranked = sorted(persons.items(), key=lambda x: -adj.get(x[0], 0))
    out = []
    for name, p in ranked:
        region = compute_top_region(
            name, p.get("song_ids", []), song_map, person_overrides
        )
        out.append(
            {
                "name": name,
                "songs": len(p.get("song_ids", [])),
                "norm": round(norm.get(name, 0), 1),
                "adj": round(adj.get(name, 0), 1),
                "primary": len(p.get("primary_song_ids", [])),
                "feature": len(p.get("feature_song_ids", [])),
                "via_group": len(p.get("via_group_song_ids", [])),
                "region": region,
                "labels": ", ".join(p.get("labels", [])),
                "groups": ", ".join(p.get("groups", [])),
            }
        )
    return out


def export_regions(area: str) -> dict:
    base = DATA_ROOT / area / "normalized"
    regions = load_json(base / "regions.json")
    if isinstance(regions, dict) and regions.get("status"):
        return {}
    if not regions or (isinstance(regions, dict) and not any(
        isinstance(v, dict) and "song_ids" in v for v in regions.values()
    )):
        return {}
    return {
        rname: {
            "songs": len(rdata.get("song_ids", [])),
            "persons": len(rdata.get("persons", [])),
        }
        for rname, rdata in regions.items()
        if isinstance(rdata, dict) and "song_ids" in rdata
    }


def build_hu_regions_from_overrides(area: str, persons_data: list[dict]) -> dict:
    """Build region stats from person region overrides for Hungarian data."""
    region_stats: dict[str, dict] = {}
    for p in persons_data:
        r = p.get("region")
        if not r:
            continue
        if r not in region_stats:
            region_stats[r] = {"songs": 0, "persons": 0}
        region_stats[r]["persons"] += 1
        region_stats[r]["songs"] += p["songs"]
    return region_stats


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Music Collection</title>
<style>
  :root {
    --bg: #fafafa; --card: #fff; --border: #e0e0e0; --text: #1a1a1a;
    --muted: #666; --accent: #2563eb; --accent-light: #dbeafe;
    --hover: #f5f5f5; --bar: #3b82f6; --bar-hu: #dc2626;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.5; padding: 20px; }
  h1 { font-size: 1.5rem; margin-bottom: 4px; }
  .subtitle { color: var(--muted); font-size: 0.85rem; margin-bottom: 20px; }

  .tabs { display: flex; gap: 2px; margin-bottom: 16px; }
  .tab { padding: 8px 20px; border: 1px solid var(--border); background: var(--card);
    cursor: pointer; font-size: 0.9rem; border-radius: 6px 6px 0 0; color: var(--muted); }
  .tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }

  .controls { display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; align-items: center; }
  .controls input[type=text] { padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px;
    font-size: 0.85rem; width: 220px; }
  .controls select { padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px;
    font-size: 0.85rem; background: var(--card); }
  .controls label { font-size: 0.8rem; color: var(--muted); }

  .stats { display: flex; gap: 24px; margin-bottom: 16px; flex-wrap: wrap; }
  .stat { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 16px; min-width: 100px; }
  .stat .val { font-size: 1.3rem; font-weight: 700; color: var(--accent); }
  .stat .lbl { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; }

  .table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 8px;
    background: var(--card); }
  table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  th { position: sticky; top: 0; background: #f8f9fa; border-bottom: 2px solid var(--border);
    padding: 8px 10px; text-align: left; cursor: pointer; user-select: none;
    white-space: nowrap; font-weight: 600; font-size: 0.78rem; text-transform: uppercase;
    color: var(--muted); }
  th:hover { color: var(--accent); }
  th .arrow { font-size: 0.7rem; margin-left: 3px; }
  td { padding: 6px 10px; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }
  tr:hover td { background: var(--hover); }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  td.rank { color: var(--muted); width: 40px; text-align: right; }
  .name-cell { font-weight: 500; max-width: 200px; overflow: hidden; text-overflow: ellipsis; }
  .tag { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 0.72rem;
    background: var(--accent-light); color: var(--accent); margin-right: 3px; }
  .bar-cell { width: 80px; }
  .bar { height: 14px; background: var(--bar); border-radius: 3px; opacity: 0.6; min-width: 1px; }

  .map-section { margin-top: 24px; }
  .map-container { position: relative; width: 100%; max-width: 900px; margin: 0 auto;
    background: var(--card); border: 1px solid var(--border); border-radius: 8px;
    padding: 20px; }
  .map-svg { width: 100%; height: auto; }
  .map-dot { cursor: pointer; transition: r 0.15s; }
  .map-dot:hover { opacity: 0.8; }
  .map-label { font-size: 10px; fill: var(--text); pointer-events: none; font-weight: 600; }
  .map-tooltip { position: absolute; background: var(--card); border: 1px solid var(--border);
    border-radius: 6px; padding: 8px 12px; font-size: 0.8rem; pointer-events: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: none; z-index: 10; max-width: 280px; }
  .map-tooltip .tt-region { font-weight: 700; margin-bottom: 4px; }
  .map-tooltip .tt-stat { color: var(--muted); }

  .section-title { font-size: 1.1rem; font-weight: 600; margin: 20px 0 10px; }
  .table-scroll { max-height: 70vh; overflow-y: auto; }
  .name-cell { cursor: pointer; }
  .name-cell:hover { color: var(--accent); text-decoration: underline; }

  /* folder modal */
  .fm-bg { display:none; position:fixed; inset:0; background:rgba(0,0,0,.45); z-index:100; justify-content:center; align-items:center; }
  .fm-bg.open { display:flex; }
  .fm { background:var(--card); border:1px solid var(--border); border-radius:12px; width:640px; max-width:92vw; max-height:80vh; display:flex; flex-direction:column; box-shadow:0 8px 32px rgba(0,0,0,.15); }
  .fm-head { display:flex; justify-content:space-between; align-items:center; padding:14px 18px; border-bottom:1px solid var(--border); }
  .fm-head h3 { font-size:1rem; }
  .fm-close { background:none; border:none; font-size:1.3rem; cursor:pointer; color:var(--muted); line-height:1; }
  .fm-close:hover { color:var(--text); }
  .fm-body { overflow-y:auto; padding:10px 18px 18px; font-size:.82rem; }
  .fm-tree { list-style:none; padding-left:0; }
  .fm-tree ul { list-style:none; padding-left:18px; }
  .fm-dir > span { cursor:pointer; font-weight:500; user-select:none; }
  .fm-dir > span::before { content:'▸ '; color:var(--muted); display:inline-block; width:14px; }
  .fm-dir.open > span::before { content:'▾ '; }
  .fm-dir > ul { display:none; }
  .fm-dir.open > ul { display:block; }
  .fm-file { color:var(--muted); padding:1px 0; }
  .fm-file::before { content:'♪ '; opacity:.5; }
  .fm-empty { color:var(--muted); font-style:italic; padding:1px 0 1px 14px; }
  .fm-stats { color:var(--muted); font-size:.75rem; margin-left:8px; }
</style>
</head>
<body>

<h1>My Music Collection</h1>
<p class="subtitle">Artist rankings across 15,000+ songs with normalized and adjusted credits</p>

<div class="tabs">
  <div class="tab active" data-tab="us">US Rap</div>
  <div class="tab" data-tab="hu">Hungarian Rap</div>
  <div class="tab" data-tab="rnb">R&amp;B</div>
  <div class="tab" data-tab="rock">Rock</div>
  <div class="tab" data-tab="magyar">Magyar</div>
  <div class="tab" data-tab="latino">Latin Music</div>
  <div class="tab" data-tab="pop">Pop</div>
  <div class="tab" data-tab="alternate">Alternative</div>
  <div class="tab" data-tab="elektro">Electronic</div>
  <div class="tab" data-tab="combined">R&B + Pop + Alt</div>
</div>

<div id="panel-us" class="panel">
  <div class="stats" id="stats-us"></div>
  <div class="controls">
    <input type="text" id="search-us" placeholder="Search artists...">
    <select id="region-us"><option value="">All Regions</option></select>
    <select id="label-us"><option value="">All Labels</option></select>
    <label><input type="checkbox" id="top100-us"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-us"></div></div>
  <div class="map-section">
    <div class="section-title">US Map</div>
    <div class="map-container" id="map-us-container">
      <div class="map-tooltip" id="map-us-tooltip"></div>
    </div>
  </div>
</div>

<div id="panel-hu" class="panel" style="display:none">
  <div class="stats" id="stats-hu"></div>
  <div class="controls">
    <input type="text" id="search-hu" placeholder="Search artists...">
    <select id="region-hu"><option value="">All Regions</option></select>
    <select id="label-hu"><option value="">All Labels</option></select>
    <label><input type="checkbox" id="top100-hu"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-hu"></div></div>
  <div class="map-section">
    <div class="section-title">Hungary Map</div>
    <div class="map-container" id="map-hu-container">
      <div class="map-tooltip" id="map-hu-tooltip"></div>
    </div>
  </div>
</div>

<div id="panel-rnb" class="panel" style="display:none">
  <div class="stats" id="stats-rnb"></div>
  <div class="controls">
    <input type="text" id="search-rnb" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-rnb"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-rnb"></div></div>
</div>

<div id="panel-rock" class="panel" style="display:none">
  <div class="stats" id="stats-rock"></div>
  <div class="controls">
    <input type="text" id="search-rock" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-rock"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-rock"></div></div>
</div>

<div id="panel-magyar" class="panel" style="display:none">
  <div class="stats" id="stats-magyar"></div>
  <div class="controls">
    <input type="text" id="search-magyar" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-magyar"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-magyar"></div></div>
</div>

<div id="panel-latino" class="panel" style="display:none">
  <div class="stats" id="stats-latino"></div>
  <div class="controls">
    <input type="text" id="search-latino" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-latino"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-latino"></div></div>
</div>

<div id="panel-elektro" class="panel" style="display:none">
  <div class="stats" id="stats-elektro"></div>
  <div class="controls">
    <input type="text" id="search-elektro" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-elektro"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-elektro"></div></div>
</div>

<div id="panel-combined" class="panel" style="display:none">
  <div class="stats" id="stats-combined"></div>
  <div class="controls">
    <input type="text" id="search-combined" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-combined"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-combined"></div></div>
</div>

<div id="panel-pop" class="panel" style="display:none">
  <div class="stats" id="stats-pop"></div>
  <div class="controls">
    <input type="text" id="search-pop" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-pop"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-pop"></div></div>
</div>

<div id="panel-alternate" class="panel" style="display:none">
  <div class="stats" id="stats-alternate"></div>
  <div class="controls">
    <input type="text" id="search-alternate" placeholder="Search artists...">
    <label><input type="checkbox" id="top100-alternate"> Top 100 only</label>
  </div>
  <div class="table-wrap"><div class="table-scroll" id="table-alternate"></div></div>
</div>

<div class="fm-bg" id="fmBg">
  <div class="fm">
    <div class="fm-head"><h3 id="fmTitle"></h3><button class="fm-close" id="fmClose">&times;</button></div>
    <div class="fm-body" id="fmBody"></div>
  </div>
</div>

<script>
const TREES = __FOLDER_TREES__;
const RNB_DATA = __RNB_DATA__;
const ROCK_DATA = __ROCK_DATA__;
const MAGYAR_DATA = __MAGYAR_DATA__;
const LATINO_DATA = __LATINO_DATA__;
const ELEKTRO_DATA = __ELEKTRO_DATA__;
const POP_DATA = __POP_DATA__;
const ALT_DATA = __ALT_DATA__;
const US_DATA = __US_DATA__;
const HU_DATA = __HU_DATA__;
const US_REGIONS = __US_REGIONS__;
const HU_REGIONS = __HU_REGIONS__;

// ─── Map coordinates (projected from GeoJSON) ───
const US_COORDS = __US_COORDS__;
const HU_COORDS = __HU_COORDS__;

// ─── TABS ───
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.querySelectorAll('.panel').forEach(p => p.style.display = 'none');
    document.getElementById('panel-' + t.dataset.tab).style.display = '';
  });
});

// ─── TABLE ENGINE ───
function buildTable(containerId, data, columns, sortCol, sortDir) {
  const el = document.getElementById(containerId);
  let html = '<table><thead><tr>';
  columns.forEach(c => {
    const arrow = c.key === sortCol ? (sortDir === 'asc' ? ' \u25B2' : ' \u25BC') : '';
    html += `<th data-key="${c.key}" data-type="${c.type || 'num'}">${c.label}<span class="arrow">${arrow}</span></th>`;
  });
  html += '</tr></thead><tbody>';
  const maxAdj = data.length ? Math.max(...data.map(d => d.adj || 0)) : 1;
  data.forEach((d, i) => {
    html += '<tr>';
    columns.forEach(c => {
      if (c.key === '_rank') {
        html += `<td class="rank">${i + 1}</td>`;
      } else if (c.key === 'name') {
        html += `<td class="name-cell" title="Click to browse folders" onclick="showFolders('${d.name.replace(/'/g, "\\'")}')">${d.name}</td>`;
      } else if (c.key === '_bar') {
        const w = Math.round(((d.adj || 0) / maxAdj) * 100);
        html += `<td class="bar-cell"><div class="bar" style="width:${w}%"></div></td>`;
      } else if (c.key === 'labels' || c.key === 'groups') {
        const val = d[c.key] || '';
        const tags = val ? val.split(', ').map(t => `<span class="tag">${t}</span>`).join('') : '-';
        html += `<td>${tags}</td>`;
      } else if (c.type === 'num') {
        html += `<td class="num">${d[c.key] ?? ''}</td>`;
      } else {
        html += `<td>${d[c.key] || '-'}</td>`;
      }
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  el.innerHTML = html;
}

function setupPanel(prefix, allData) {
  let sortCol = 'adj', sortDir = 'desc';
  const searchEl = document.getElementById('search-' + prefix);
  const top100El = document.getElementById('top100-' + prefix);
  const regionEl = document.getElementById('region-' + prefix);
  const labelEl = document.getElementById('label-' + prefix);

  if (regionEl) {
    const regions = [...new Set(allData.map(d => d.region).filter(Boolean))].sort();
    regions.forEach(r => { const o = document.createElement('option'); o.value = r; o.textContent = r; regionEl.appendChild(o); });
  }
  if (labelEl) {
    const labels = [...new Set(allData.flatMap(d => (d.labels || '').split(', ')).filter(Boolean))].sort();
    labels.forEach(l => { const o = document.createElement('option'); o.value = l; o.textContent = l; labelEl.appendChild(o); });
  }

  const columns = [
    { key: '_rank', label: '#', type: 'num' },
    { key: 'name', label: 'Artist', type: 'str' },
    { key: 'songs', label: 'Songs' },
    { key: 'norm', label: 'Norm' },
    { key: 'adj', label: 'Adj' },
    { key: '_bar', label: '', type: 'str' },
    { key: 'primary', label: 'Primary' },
    { key: 'feature', label: 'Feature' },
    { key: 'via_group', label: 'Via Grp' },
    { key: 'region', label: 'Region', type: 'str' },
    { key: 'labels', label: 'Labels', type: 'str' },
    { key: 'groups', label: 'Groups', type: 'str' },
  ];

  function getFiltered() {
    let d = [...allData];
    const q = (searchEl?.value || '').toLowerCase();
    if (q) d = d.filter(p => p.name.toLowerCase().includes(q));
    if (regionEl?.value) d = d.filter(p => p.region === regionEl.value);
    if (labelEl?.value) d = d.filter(p => (p.labels || '').includes(labelEl.value));
    if (top100El?.checked) d = d.slice(0, 100);
    return d;
  }

  function render() {
    let data = getFiltered();
    data.sort((a, b) => {
      const col = columns.find(c => c.key === sortCol);
      const type = col?.type || 'num';
      let va = a[sortCol] ?? '', vb = b[sortCol] ?? '';
      if (type === 'num') { va = +va || 0; vb = +vb || 0; }
      else { va = String(va).toLowerCase(); vb = String(vb).toLowerCase(); }
      if (va < vb) return sortDir === 'asc' ? -1 : 1;
      if (va > vb) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    buildTable('table-' + prefix, data, columns, sortCol, sortDir);
    updateStats(prefix, data, allData);
    document.querySelectorAll('#table-' + prefix + ' th').forEach(th => {
      th.addEventListener('click', () => {
        const key = th.dataset.key;
        if (key === '_rank' || key === '_bar') return;
        if (sortCol === key) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
        else { sortCol = key; sortDir = th.dataset.type === 'str' ? 'asc' : 'desc'; }
        render();
      });
    });
  }

  // expose render for map click filtering
  window['render_' + prefix] = render;

  searchEl?.addEventListener('input', render);
  regionEl?.addEventListener('change', render);
  labelEl?.addEventListener('change', render);
  top100El?.addEventListener('change', render);
  render();
}

function updateStats(prefix, filtered, all) {
  const el = document.getElementById('stats-' + prefix);
  const totalSongs = filtered.reduce((s, d) => s + d.songs, 0);
  const avgAdj = filtered.length ? (filtered.reduce((s, d) => s + d.adj, 0) / filtered.length).toFixed(1) : 0;
  el.innerHTML = `
    <div class="stat"><div class="val">${filtered.length}</div><div class="lbl">Artists shown</div></div>
    <div class="stat"><div class="val">${all.length}</div><div class="lbl">Total artists</div></div>
    <div class="stat"><div class="val">${totalSongs.toLocaleString()}</div><div class="lbl">Total song credits</div></div>
    <div class="stat"><div class="val">${avgAdj}</div><div class="lbl">Avg adjusted</div></div>
  `;
}

// ─── GENERIC MAP BUILDER ───
function buildMap(containerId, tooltipId, regionSelectId, data, regionStats, coords, outlinePath, viewBox, bubbleColor) {
  const container = document.getElementById(containerId);
  const tooltip = document.getElementById(tooltipId);
  const [W, H] = viewBox;

  // Top artists per region
  const regionTopArtists = {};
  data.forEach(p => {
    if (!p.region) return;
    if (!regionTopArtists[p.region]) regionTopArtists[p.region] = [];
    if (regionTopArtists[p.region].length < 5) regionTopArtists[p.region].push(p.name);
  });

  const maxPersons = Math.max(...Object.values(regionStats).map(r => r.persons), 1);

  let svg = `<svg class="map-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
  svg += `<rect width="${W}" height="${H}" fill="#f8fafc" rx="8"/>`;
  svg += outlinePath;

  Object.entries(coords).forEach(([name, pos]) => {
    const region = regionStats[name];
    if (!region) return;
    const r = Math.max(10, Math.min(40, Math.sqrt(region.persons / maxPersons) * 48));
    const opacity = 0.35 + (region.persons / maxPersons) * 0.5;

    svg += `<circle class="map-dot" cx="${pos.x}" cy="${pos.y}" r="${r}"
      fill="${bubbleColor}" opacity="${opacity.toFixed(2)}"
      data-region="${name}" data-songs="${region.songs}" data-persons="${region.persons}"/>`;
    svg += `<text class="map-label" x="${pos.x}" y="${pos.y + r + 13}" text-anchor="middle">${name}</text>`;
    svg += `<text x="${pos.x}" y="${pos.y + 4}" text-anchor="middle"
      font-size="11" font-weight="700" fill="#fff" pointer-events="none">${region.persons}</text>`;
  });

  svg += '</svg>';
  container.insertAdjacentHTML('afterbegin', svg);

  container.querySelectorAll('.map-dot').forEach(dot => {
    dot.addEventListener('mouseenter', e => {
      const name = dot.dataset.region;
      const top = regionTopArtists[name] || [];
      tooltip.innerHTML = `
        <div class="tt-region">${name}</div>
        <div class="tt-stat">${dot.dataset.persons} artists / ${dot.dataset.songs} songs</div>
        ${top.length ? '<div style="margin-top:4px;font-size:0.75rem;color:#666">Top: ' + top.join(', ') + '</div>' : ''}
      `;
      tooltip.style.display = 'block';
    });
    dot.addEventListener('mousemove', e => {
      const rect = container.getBoundingClientRect();
      tooltip.style.left = Math.min(e.clientX - rect.left + 12, rect.width - 200) + 'px';
      tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
    });
    dot.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
    dot.addEventListener('click', () => {
      const sel = document.getElementById(regionSelectId);
      if (sel) { sel.value = dot.dataset.region; sel.dispatchEvent(new Event('change')); }
    });
  });
}

// ─── Map outlines (from GeoJSON, projected) ───
const US_OUTLINE = `<path d="__US_PATH__" fill="#e8ecf0" stroke="#cbd5e1" stroke-width="1.5"/>`;
const HU_OUTLINE = `<path d="__HU_PATH__" fill="#e8ecf0" stroke="#cbd5e1" stroke-width="1.5"/>`;

// ─── FOLDER MODAL ───
function countFiles(node) {
  if (node.t === 'f') return 1;
  return (node.c || []).reduce((s, c) => s + countFiles(c), 0);
}
function countDirs(node) {
  if (node.t === 'f') return 0;
  return 1 + (node.c || []).reduce((s, c) => s + countDirs(c), 0);
}
function renderTree(nodes) {
  let html = '<ul class="fm-tree">';
  nodes.forEach(node => {
    if (node.t === 'f') {
      html += `<li class="fm-file">${esc(node.n)}</li>`;
    } else {
      const files = countFiles(node);
      const kids = node.c || [];
      const hasContent = kids.length > 0;
      html += `<li class="fm-dir open"><span onclick="this.parentElement.classList.toggle('open')">${esc(node.n)} <span class="fm-stats">(${files} files)</span></span>`;
      if (hasContent) {
        html += '<ul>';
        kids.forEach(c => {
          if (c.t === 'f') html += `<li class="fm-file">${esc(c.n)}</li>`;
          else {
            const cf = countFiles(c);
            const ck = c.c || [];
            html += `<li class="fm-dir"><span onclick="this.parentElement.classList.toggle('open')">${esc(c.n)} <span class="fm-stats">(${cf} files)</span></span>`;
            if (ck.length) html += renderSubTree(ck);
            else html += '<ul><li class="fm-empty">empty</li></ul>';
            html += '</li>';
          }
        });
        html += '</ul>';
      } else {
        html += '<ul><li class="fm-empty">empty folder</li></ul>';
      }
      html += '</li>';
    }
  });
  html += '</ul>';
  return html;
}
function renderSubTree(nodes) {
  let html = '<ul>';
  nodes.forEach(c => {
    if (c.t === 'f') html += `<li class="fm-file">${esc(c.n)}</li>`;
    else {
      const cf = countFiles(c);
      const ck = c.c || [];
      html += `<li class="fm-dir"><span onclick="this.parentElement.classList.toggle('open')">${esc(c.n)} <span class="fm-stats">(${cf})</span></span>`;
      if (ck.length) html += renderSubTree(ck);
      else html += '<ul><li class="fm-empty">empty</li></ul>';
      html += '</li>';
    }
  });
  html += '</ul>';
  return html;
}
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function showFolders(name) {
  const tree = TREES[name];
  if (!tree) { alert('No folder data for ' + name); return; }
  const totalFiles = tree.reduce((s, t) => s + countFiles(t), 0);
  const totalDirs = tree.reduce((s, t) => s + countDirs(t), 0);
  document.getElementById('fmTitle').textContent = name + ' — ' + totalFiles + ' files in ' + totalDirs + ' folders';
  document.getElementById('fmBody').innerHTML = renderTree(tree);
  document.getElementById('fmBg').classList.add('open');
}
document.getElementById('fmBg').addEventListener('click', function(e) { if (e.target === this) this.classList.remove('open'); });
document.getElementById('fmClose').addEventListener('click', function() { document.getElementById('fmBg').classList.remove('open'); });
document.addEventListener('keydown', function(e) { if (e.key === 'Escape') document.getElementById('fmBg').classList.remove('open'); });

// ─── INIT ───
setupPanel('us', US_DATA);
setupPanel('hu', HU_DATA);
setupPanel('rnb', RNB_DATA);
setupPanel('rock', ROCK_DATA);
setupPanel('magyar', MAGYAR_DATA);
setupPanel('latino', LATINO_DATA);
setupPanel('elektro', ELEKTRO_DATA);
setupPanel('pop', POP_DATA);
setupPanel('alternate', ALT_DATA);

// Build combined R&B + Pop + Alt
const COMBINED = (() => {
  const map = {};
  [RNB_DATA, POP_DATA, ALT_DATA].forEach(src => {
    src.forEach(p => {
      const e = map[p.name];
      if (!e) { map[p.name] = {...p}; }
      else {
        e.songs += p.songs; e.norm += p.norm; e.adj += p.adj;
        e.primary += p.primary; e.feature += p.feature; e.via_group += p.via_group;
        if (p.groups && !e.groups) e.groups = p.groups;
        if (p.labels && !e.labels) e.labels = p.labels;
      }
    });
  });
  return Object.values(map).sort((a,b) => b.adj - a.adj);
})();
setupPanel('combined', COMBINED);
buildMap('map-us-container', 'map-us-tooltip', 'region-us', US_DATA, US_REGIONS, US_COORDS, US_OUTLINE, [900, 560], '#3b82f6');
buildMap('map-hu-container', 'map-hu-tooltip', 'region-hu', HU_DATA, HU_REGIONS, HU_COORDS, HU_OUTLINE, [620, 260], '#dc2626');
</script>
</body>
</html>"""


# Folder roots to scan per area
AREA_SCAN_ROOTS = {
    "us": [ZENE / "_rap", ZENE / "_trap"],
    "hungarian": [ZENE / "_magyar rap", ZENE / "_magyar trap"],
}


def _normalize_folder_name(name: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]", "", name.lower())


def build_folder_trees(area: str, persons_data: list[dict]) -> dict[str, list]:
    """Scan disk for each artist's OWN folders (name-matched), including empty dirs."""
    base = DATA_ROOT / area / "normalized"
    songs = load_json(base / "songs.json")

    # Find artist-level folder roots where ANY folder in the path matches the artist
    artist_roots: dict[str, set[str]] = {}
    for s in songs:
        for credit in s.get("credits", []):
            if credit["entity_type"] != "person" or credit["role"] != "primary":
                continue
            name = credit["entity"]
            parts = Path(s["file"]).parts
            norm_name = _normalize_folder_name(name)
            # Check each directory level (skip filename at the end)
            for i in range(1, len(parts) - 1):
                if _normalize_folder_name(parts[i]) == norm_name:
                    artist_roots.setdefault(name, set()).add(str(Path(*parts[:i+1])))
                    break

    trees: dict[str, list] = {}
    for p in persons_data:
        name = p["name"]
        roots = artist_roots.get(name, set())
        if not roots:
            continue
        artist_tree = []
        for rel_root in sorted(roots):
            abs_root = ZENE / rel_root
            if not abs_root.is_dir():
                continue
            tree = _scan_dir(abs_root, rel_root)
            if tree:
                artist_tree.append(tree)
        if artist_tree:
            trees[name] = artist_tree
    return trees


def _scan_dir(abs_path: Path, rel_path: str) -> dict | None:
    """Recursively scan a directory, returning a tree node with children."""
    children = []
    try:
        entries = sorted(abs_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return None
    for entry in entries:
        if entry.name.startswith(".") or entry.name == "__pycache__":
            continue
        if entry.is_dir():
            child = _scan_dir(entry, rel_path + "/" + entry.name)
            if child:
                children.append(child)
        elif entry.suffix.lower() in AUDIO_EXTS:
            children.append({"n": entry.name, "t": "f"})
    # Include empty dirs too
    return {"n": Path(rel_path).name, "t": "d", "c": children}


def main() -> int:
    us_data = export_persons("us")
    hu_data = export_persons("hungarian")
    rnb_data = export_persons("rnb")
    rock_data = export_persons("rock")
    magyar_data = export_persons("magyar")
    latino_data = export_persons("latino")
    elektro_data = export_persons("elektro")
    pop_data = export_persons("pop")
    alt_data = export_persons("alternate")
    us_regions = export_regions("us")
    hu_regions = build_hu_regions_from_overrides("hungarian", hu_data)

    # Generate map paths and coordinates
    us_proj, _ = project_coords(US_CONTINENTAL, (900, 500))
    us_path = coords_to_svg_path(US_CONTINENTAL, us_proj)
    us_coords = project_points(US_REGION_GEO, us_proj)

    hu_proj, _ = project_coords(HU_OUTLINE_COORDS, (700, 320))
    hu_path = coords_to_svg_path(HU_OUTLINE_COORDS, hu_proj)
    hu_coords = project_points(HU_CITY_GEO, hu_proj)

    # Build folder trees
    us_trees = build_folder_trees("us", us_data)
    hu_trees = build_folder_trees("hungarian", hu_data)
    rnb_trees = build_folder_trees("rnb", rnb_data)
    rock_trees = build_folder_trees("rock", rock_data)
    magyar_trees = build_folder_trees("magyar", magyar_data)
    latino_trees = build_folder_trees("latino", latino_data)
    elektro_trees = build_folder_trees("elektro", elektro_data)
    pop_trees = build_folder_trees("pop", pop_data)
    alt_trees = build_folder_trees("alternate", alt_data)
    all_trees = {**us_trees, **hu_trees, **rnb_trees, **rock_trees, **magyar_trees, **latino_trees, **elektro_trees, **pop_trees, **alt_trees}

    html = HTML_TEMPLATE
    html = html.replace("__FOLDER_TREES__", json.dumps(all_trees, ensure_ascii=False, separators=(',', ':')))
    html = html.replace("__RNB_DATA__", json.dumps(rnb_data, ensure_ascii=False))
    html = html.replace("__ROCK_DATA__", json.dumps(rock_data, ensure_ascii=False))
    html = html.replace("__MAGYAR_DATA__", json.dumps(magyar_data, ensure_ascii=False))
    html = html.replace("__LATINO_DATA__", json.dumps(latino_data, ensure_ascii=False))
    html = html.replace("__ELEKTRO_DATA__", json.dumps(elektro_data, ensure_ascii=False))
    html = html.replace("__POP_DATA__", json.dumps(pop_data, ensure_ascii=False))
    html = html.replace("__ALT_DATA__", json.dumps(alt_data, ensure_ascii=False))
    html = html.replace("__US_DATA__", json.dumps(us_data, ensure_ascii=False))
    html = html.replace("__HU_DATA__", json.dumps(hu_data, ensure_ascii=False))
    html = html.replace("__US_REGIONS__", json.dumps(us_regions, ensure_ascii=False))
    html = html.replace("__HU_REGIONS__", json.dumps(hu_regions, ensure_ascii=False))
    html = html.replace("__US_COORDS__", json.dumps(us_coords, ensure_ascii=False))
    html = html.replace("__HU_COORDS__", json.dumps(hu_coords, ensure_ascii=False))
    html = html.replace("__US_PATH__", us_path)
    html = html.replace("__HU_PATH__", hu_path)

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
