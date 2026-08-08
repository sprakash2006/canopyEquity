"""Generate a SHAREABLE interactive HTML map of the master ward table.

Builds a self-contained folder (outputs/mcd_ward_explorer_share/) with the map,
local Leaflet dependencies, and a README, so it can be zipped and sent to anyone.

Features:
  - default "Overall - regions" view: each assembly constituency a distinct
    colour (a reference map, not a heatmap)
  - dropdown to recolour by any metric (heatmaps)
  - hover a ward -> info panel with all its data
  - CLICK a ward -> zoom to it
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "processed" / "mcd_wards_master.geojson"
SHARE = ROOT / "outputs" / "mcd_ward_explorer_share"
OUT = SHARE / "index.html"

METRICS = [
    ("__region__", "Overall - regions (distinct)", "", "cat"),
    ("mean_ndvi", "Greenery (NDVI)", "", "greens"),
    ("mean_lst_c", "Surface temp", " C", "reds"),
    ("wc_canopy_frac", "Canopy cover", "%", "greens"),
    ("wc_built_frac", "Built-up", "%", "greys"),
    ("cropland_frac", "Cropland", "%", "ylorbr"),
    ("jj_area_frac", "Slum (JJ) area", "%", "purples"),
    ("jj_households", "JJ households", "", "purples"),
    ("sc_population", "SC population", "", "purples"),
    ("total_population", "Population", "", "viridis"),
    ("mean_annual_rainfall_mm", "Rainfall", " mm", "blues"),
    ("mean_gw_depth_m", "Groundwater depth", " m", "reds"),
    ("ridge_frac", "Ridge/forest", "%", "greens"),
]

PALETTES = {
    "greens": ["#f7fcf5", "#c7e9c0", "#74c476", "#238b45", "#00441b"],
    "reds": ["#fff5eb", "#fdd0a2", "#fd8d3c", "#e6550d", "#a63603"],
    "blues": ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
    "purples": ["#fcfbfd", "#dadaeb", "#9e9ac8", "#6a51a3", "#3f007d"],
    "greys": ["#ffffff", "#d9d9d9", "#969696", "#636363", "#252525"],
    "ylorbr": ["#ffffe5", "#fee391", "#fe9929", "#cc4c02", "#662506"],
    "viridis": ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"],
}
CAT_PALETTE = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc948",
               "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac", "#86bcb6", "#d37295",
               "#fabfd2", "#b6992d", "#8cd17d", "#499894", "#f1ce63", "#a0cbe8"]

PANEL = [
    ("ac_name", "Assembly const.", "", "str"),
    ("area_ha", "Area", " ha", "num0"),
    ("total_population", "Population 2011", "", "int"),
    ("sc_population", "SC population", "", "int"),
    ("mean_ndvi", "NDVI (greenery)", "", "num2"),
    ("mean_lst_c", "Surface temp", " C", "num1"),
    ("wc_canopy_frac", "Canopy cover", "%", "pct"),
    ("wc_built_frac", "Built-up", "%", "pct"),
    ("cropland_frac", "Cropland", "%", "pct"),
    ("jj_households", "JJ households", "", "int"),
    ("jj_area_frac", "JJ area share", "%", "pct"),
    ("mean_annual_rainfall_mm", "Rainfall", " mm", "num0"),
    ("mean_gw_depth_m", "Groundwater depth", " m", "num1"),
    ("ridge_frac", "Ridge/forest", "%", "pct"),
    ("water_tier", "Water tier", "", "str"),
]

README = """MCD Ward Data Explorer
======================

HOW TO OPEN
  Double-click  index.html  -> it opens in your web browser.
  (Keep all files in this folder together.)

USE
  - Hover a ward  -> see all its data in the right-hand panel.
  - Click a ward  -> zoom to it.
  - Top-left dropdown -> recolour the map (regions, greenery, heat,
    canopy, slum area, groundwater, rainfall, ...).

NOTES
  - Ward shapes + data are built into index.html - no internet needed for those.
  - The grey street background loads from the internet; without a connection
    you still get coloured wards + all hover data, just no basemap.

Data: Municipal Corporation of Delhi, 250 wards (2022). Sources: Sentinel-2,
Landsat, ESA WorldCover, Census 2011, DUSIB, CGWB, CHIRPS, OSM.
"""


def _round(x, nd=5):
    if isinstance(x, (int, float)):
        return round(x, nd)
    return [_round(v, nd) for v in x]


def main() -> int:
    gdf = gpd.read_file(MASTER)
    gdf["geometry"] = gdf.to_crs("EPSG:32643").geometry.simplify(30).to_crs("EPSG:4326")
    gj = json.loads(gdf.to_json())
    for f in gj["features"]:
        geom = f.get("geometry") or {}
        if "coordinates" in geom:
            geom["coordinates"] = _round(geom["coordinates"])

    html = (TEMPLATE
            .replace("__DATA__", json.dumps(gj, separators=(",", ":")))
            .replace("__METRICS__", json.dumps([{"k": k, "label": l, "unit": u, "pal": p}
                                                for k, l, u, p in METRICS]))
            .replace("__PANEL__", json.dumps([{"k": k, "label": l, "unit": u, "kind": kd}
                                              for k, l, u, kd in PANEL]))
            .replace("__PALETTES__", json.dumps(PALETTES))
            .replace("__CATPAL__", json.dumps(CAT_PALETTE)))
    SHARE.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    (SHARE / "README.txt").write_text(README, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1024:.0f} KB)")
    print(f"wrote {(SHARE/'README.txt').relative_to(ROOT)}")
    return 0


TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCD Ward Data Explorer</title>
<link rel="stylesheet" href="leaflet.css"/>
<style>
  html,body{margin:0;height:100%;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
  #map{position:absolute;inset:0}
  .card{position:absolute;z-index:1000;background:#fff;border:1px solid #ddd;
        border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.15);padding:12px 14px}
  #controls{top:12px;left:12px}
  #controls h1{margin:0 0 8px;font-size:15px}
  #controls select{font-size:13px;padding:5px 8px;border-radius:6px;border:1px solid #ccc;width:230px}
  #controls .sub{font-size:11px;color:#777;margin-top:6px}
  #controls button{margin-top:8px;font-size:12px;padding:4px 10px;border:1px solid #ccc;
        border-radius:6px;background:#f7f7f7;cursor:pointer}
  #info{top:12px;right:12px;width:250px;max-height:88vh;overflow:auto;display:none}
  #info h2{margin:0;font-size:16px;color:#1a6b2f}
  #info .wn{font-size:11px;color:#888;margin:2px 0 10px}
  #info table{width:100%;border-collapse:collapse;font-size:12px}
  #info td{padding:3px 0;border-bottom:1px solid #f0f0f0}
  #info td.k{color:#666}#info td.v{text-align:right;font-weight:600}
  #legend{bottom:16px;right:12px;font-size:12px}
  #legend .bar{height:12px;width:180px;border-radius:3px;margin:6px 0}
  #legend .ends{display:flex;justify-content:space-between;color:#555}
  .hint{position:absolute;bottom:16px;left:12px;z-index:1000;font-size:11px;color:#888;
        background:rgba(255,255,255,.85);padding:4px 8px;border-radius:6px}
</style></head><body>
<div id="map"></div>
<div id="controls" class="card">
  <h1>MCD Ward Data Explorer</h1>
  <label>Colour wards by:</label><br>
  <select id="metric"></select>
  <div class="sub">250 wards &middot; click a ward to pin its data</div>
  <button id="reset">Reset view</button>
</div>
<div id="info" class="card"></div>
<div id="legend" class="card"><b id="legTitle"></b><div class="bar" id="legBar"></div>
  <div class="ends"><span id="legLo"></span><span id="legHi"></span></div></div>
<div class="hint">Hover to preview &middot; click a ward to pin it (black outline) &middot; click again to release</div>
<script src="leaflet.js"></script>
<script>
const DATA=__DATA__, METRICS=__METRICS__, PANEL=__PANEL__, PALETTES=__PALETTES__, CATPAL=__CATPAL__;
const map=L.map('map').setView([28.62,77.10],10);
const HOME=[[28.40,76.83],[28.89,77.35]];
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
 {attribution:'&copy; OSM &copy; CARTO',subdomains:'abcd',maxZoom:19}).addTo(map);

function lerp(a,b,t){return a+(b-a)*t}
function hex2rgb(h){return [parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)]}
function ramp(pal,t){t=Math.max(0,Math.min(1,t));const n=pal.length-1;const i=Math.min(Math.floor(t*n),n-1);
  const f=t*n-i;const a=hex2rgb(pal[i]),b=hex2rgb(pal[i+1]);
  return `rgb(${Math.round(lerp(a[0],b[0],f))},${Math.round(lerp(a[1],b[1],f))},${Math.round(lerp(a[2],b[2],f))})`}

// categorical colours by assembly constituency
const acList=[...new Set(DATA.features.map(f=>f.properties.ac_name))].sort();
const acColor={}; acList.forEach((a,i)=>acColor[a]=CATPAL[i%CATPAL.length]);

let curMetric=METRICS[0], mn=0, mx=1, layer=null, selLayer=null, selWard=null;
const SEL_STYLE={color:'#000',weight:3};
function computeRange(k){let lo=Infinity,hi=-Infinity;
  DATA.features.forEach(f=>{const v=f.properties[k];if(v!=null&&!isNaN(v)){lo=Math.min(lo,v);hi=Math.max(hi,v)}});
  return [lo,hi]}

function fillFor(p){
  if(curMetric.pal==='cat')return acColor[p.ac_name]||'#ccc';
  const v=p[curMetric.k];
  return (v==null||isNaN(v))?'#eee':ramp(PALETTES[curMetric.pal],(v-mn)/((mx-mn)||1))}
function style(f){return {fillColor:fillFor(f.properties),fillOpacity:.82,color:'#fff',weight:.6}}

function fmt(v,kind){if(v==null||v==='')return '&mdash;';
  if(kind==='pct')return (v*100).toFixed(1)+'%';
  if(kind==='int'||kind==='num0')return Math.round(v).toLocaleString();
  if(kind==='num1')return (+v).toFixed(1);
  if(kind==='num2')return (+v).toFixed(2);
  return v}
function showInfo(p){let rows='';PANEL.forEach(f=>{let v=p[f.k];
  rows+=`<tr><td class="k">${f.label}</td><td class="v">${fmt(v,f.kind)}${(v!=null&&v!==''&&f.unit&&f.kind!=='pct')?f.unit:''}</td></tr>`});
  const el=document.getElementById('info');
  el.innerHTML=`<h2>${p.ward_name}</h2><div class="wn">Ward ${p.ward_no}</div><table>${rows}</table>`;
  el.style.display='block'}
function showPlaceholder(){const el=document.getElementById('info');
  el.innerHTML='<h2>Ward details</h2><div class="wn">Hover a ward to preview &middot; click to pin</div>';
  el.style.display='block'}

function selectLayer(lyr){
  if(selLayer&&selLayer!==lyr)layer.resetStyle(selLayer);
  selLayer=lyr; selWard=lyr.feature.properties.ward_no;
  lyr.setStyle(SEL_STYLE); lyr.bringToFront(); showInfo(lyr.feature.properties);
}
function deselect(){if(selLayer)layer.resetStyle(selLayer);selLayer=null;selWard=null;}
function onEach(f,lyr){lyr.on({
  mouseover:e=>{if(e.target!==selLayer)e.target.setStyle({weight:1.6,color:'#555'});
    if(!selLayer)showInfo(f.properties)},
  mouseout:e=>{if(e.target!==selLayer)layer.resetStyle(e.target)},
  click:e=>{if(e.target===selLayer){deselect();}
    else{selectLayer(e.target);map.fitBounds(e.target.getBounds(),{padding:[40,40],maxZoom:14});}}})}

function draw(){if(layer)layer.remove();
  if(curMetric.pal!=='cat')[mn,mx]=computeRange(curMetric.k);
  layer=L.geoJSON(DATA,{style:style,onEachFeature:onEach}).addTo(map);
  if(selWard!=null){selLayer=null;layer.eachLayer(l=>{
    if(l.feature.properties.ward_no===selWard){selLayer=l;l.setStyle(SEL_STYLE);l.bringToFront();}});}
  const leg=document.getElementById('legend');
  document.getElementById('legTitle').textContent=curMetric.label;
  if(curMetric.pal==='cat'){
    document.getElementById('legBar').style.background=`linear-gradient(90deg,${CATPAL.join(',')})`;
    document.getElementById('legLo').textContent='distinct colour per';
    document.getElementById('legHi').textContent='assembly constituency';
  }else{
    const pal=PALETTES[curMetric.pal];
    document.getElementById('legBar').style.background=`linear-gradient(90deg,${pal.join(',')})`;
    const u=curMetric.unit||'',pct=curMetric.unit==='%';
    document.getElementById('legLo').textContent=pct?(mn*100).toFixed(0)+'%':(mn.toFixed(mn<10?2:0)+u);
    document.getElementById('legHi').textContent=pct?(mx*100).toFixed(0)+'%':(mx.toFixed(mx<10?2:0)+u);
  }}

const sel=document.getElementById('metric');
METRICS.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=m.label;sel.appendChild(o)});
sel.onchange=()=>{curMetric=METRICS[+sel.value];draw()};
document.getElementById('reset').onclick=()=>{map.fitBounds(HOME);deselect();showPlaceholder()};
draw(); showPlaceholder();
</script></body></html>"""


if __name__ == "__main__":
    raise SystemExit(main())
