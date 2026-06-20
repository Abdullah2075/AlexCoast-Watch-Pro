"""
AlexCoast-Watch Pro — Alexandria, Egypt Coastal Flood Intelligence Platform
Refactored: Dynamic Elevation-Based Water Level System + Extreme Climate/Weather Events
"""

import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import SideBySideLayers
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union
import warnings
import json

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AlexCoast-Watch Pro",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DARK_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    background-color: #0a0e1a !important;
    color: #e0e6f0 !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1220 0%, #0a0e1a 100%) !important;
    border-right: 1px solid #1e2a42 !important;
  }
  [data-testid="stSidebar"] * { color: #c8d4e8 !important; }

  /* Main area */
  .main .block-container {
    background-color: #0a0e1a !important;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
  }

  /* Header */
  .app-header {
    background: linear-gradient(135deg, #061428 0%, #0d2244 50%, #061428 100%);
    border: 1px solid #1a3660;
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .app-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0af, #0f6fff, #3af);
  }
  .app-header h1 {
    font-family: 'Cairo', sans-serif;
    font-weight: 900;
    font-size: 1.9rem;
    color: #5bc8ff !important;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .app-header p {
    color: #7da0cc !important;
    font-size: 0.88rem;
    margin: 0.3rem 0 0 0;
    font-family: 'JetBrains Mono', monospace;
  }

  /* Metric cards */
  .metric-card {
    background: linear-gradient(145deg, #0d1a2e, #111f38);
    border: 1px solid #1e3055;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    text-align: center;
    transition: border-color 0.25s;
  }
  .metric-card:hover { border-color: #2a5090; }
  .metric-card .mc-label {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    color: #6a8aaa;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 0.35rem;
  }
  .metric-card .mc-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #5bc8ff;
    line-height: 1.1;
  }
  .metric-card .mc-sub {
    font-size: 0.75rem;
    color: #4a6a8a;
    margin-top: 0.2rem;
  }

  /* Severity badge */
  .badge-safe    { color: #00e676; background: rgba(0,230,118,0.1); border: 1px solid #00e67640; }
  .badge-warning { color: #ffca28; background: rgba(255,202,40,0.1); border: 1px solid #ffca2840; }
  .badge-critical{ color: #ff5252; background: rgba(255,82,82,0.1);  border: 1px solid #ff525240; }
  .severity-badge {
    display: inline-block;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
  }

  /* Tabs */
  [data-testid="stTabs"] [role="tab"] {
    color: #6a8aaa !important;
    font-family: 'Cairo', sans-serif;
    font-weight: 600;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: #5bc8ff !important;
    border-bottom: 2px solid #5bc8ff !important;
  }

  /* Selectbox / slider labels */
  label { color: #8ab0cc !important; font-size: 0.85rem !important; }

  /* Slider */
  [data-testid="stSlider"] > div > div > div > div {
    background-color: #0af !important;
  }

  /* Table */
  .stDataFrame, .stTable { background-color: #0d1a2e !important; }

  /* Divider */
  hr { border-color: #1e2a42 !important; }

  /* Sidebar section headers */
  .sidebar-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #3a6090;
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 0.6rem 0 0.3rem 0;
    border-top: 1px solid #1a2840;
    margin-top: 0.5rem;
  }

  /* Info boxes */
  .info-box {
    background: #0d1f38;
    border-left: 3px solid #0af;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    font-size: 0.83rem;
    color: #90b8d8;
    margin: 0.5rem 0;
  }
  .warn-box {
    background: #1f1800;
    border-left: 3px solid #ffca28;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    font-size: 0.83rem;
    color: #c8a800;
    margin: 0.5rem 0;
  }
  .crit-box {
    background: #1f0808;
    border-left: 3px solid #ff5252;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    font-size: 0.83rem;
    color: #ff8080;
    margin: 0.5rem 0;
  }
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

ALEX_CENTER = [31.2001, 29.9187]

# Alexandria approximate coastal bounding coords (WGS84)
# Coastline runs roughly E–W; Mediterranean to the north
COAST_LAT = 31.215   # approximate shoreline latitude
CITY_LON_W = 29.85
CITY_LON_E = 30.10

# SLR scenarios (cm/year above 2026 baseline)
SLR_SCENARIOS = {
    "🟢 Conservative (RCP 2.6)": 3.2,
    "🟡 Moderate (RCP 4.5)": 5.8,
    "🔴 Aggressive (RCP 8.5)": 9.4,
}

# Weather / storm surge options
WEATHER_EVENTS = {
    "⚓ Normal Tide (Stable Weather)": {
        "surge_m": 0.0,
        "wave_energy": "Low",
        "severity": "safe",
        "label": "SAFE",
        "color": "#00e676",
    },
    "🌧️ Moderate Storm Surge (Winter Nawa)": {
        "surge_m": 0.50,
        "wave_energy": "Moderate",
        "severity": "warning",
        "label": "WARNING",
        "color": "#ffca28",
    },
    "🌀 Extreme Event (50-Year Return Storm)": {
        "surge_m": 1.35,
        "wave_energy": "Extreme Wave Propagation",
        "severity": "critical",
        "label": "CRITICAL",
        "color": "#ff5252",
    },
}

# Propagation scale: metres of inland advance per metre of total flood level
# Based on Alexandria's low-lying coastal gradient (~1:500 slope)
M_PER_FLOOD_LEVEL = 0.0018  # in degrees lat (~200 m per 1 m flood level)

# Economic value per building (EGP millions)
ECON_VALUE_PER_BLDG = 4.5

# ─────────────────────────────────────────────────────────────────────────────
# GEOSPATIAL DATA PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_geodata():
    """
    Try to load real GeoJSON files; fall back to high-fidelity simulated geometry
    representing Alexandria's Mediterranean coastal zone.
    """
    shoreline_gdf = None
    buildings_gdf = None

    # ── Try real files ──────────────────────────────────────────────────────
    try:
        shoreline_gdf = gpd.read_file("shoreline_2026.geojson")
    except Exception:
        pass

    try:
        buildings_gdf = gpd.read_file("alex_buildings.geojson")
    except Exception:
        pass

    # ── Simulated shoreline ─────────────────────────────────────────────────
    if shoreline_gdf is None:
        # Realistic jagged Mediterranean coastline segment
        lons = np.linspace(CITY_LON_W, CITY_LON_E, 120)
        noise = np.random.RandomState(42).normal(0, 0.0008, 120).cumsum() * 0.3
        lats = COAST_LAT + noise
        lats = np.clip(lats, COAST_LAT - 0.008, COAST_LAT + 0.004)
        coords = list(zip(lons, lats))
        shoreline_gdf = gpd.GeoDataFrame(
            {"id": [1], "type": ["Mediterranean Shoreline 2026"]},
            geometry=[LineString(coords)],
            crs="EPSG:4326",
        )

    # ── Simulated buildings ─────────────────────────────────────────────────
    if buildings_gdf is None:
        rng = np.random.RandomState(7)
        records = []
        # Coastal zone: dense low-rise
        for i in range(280):
            lon = rng.uniform(CITY_LON_W + 0.01, CITY_LON_E - 0.01)
            lat = rng.uniform(COAST_LAT - 0.025, COAST_LAT - 0.002)
            size = rng.uniform(0.0003, 0.0008)
            btype = rng.choice(["Residential", "Commercial", "Industrial", "Critical Infrastructure"])
            floors = rng.randint(1, 6)
            elev = rng.uniform(0.2, 3.5)   # elevation above MSL (metres)
            records.append({
                "geometry": Polygon([
                    (lon, lat), (lon + size, lat),
                    (lon + size, lat + size * 0.7),
                    (lon, lat + size * 0.7),
                ]),
                "building_id": f"ALX-{i+1000:04d}",
                "type": btype,
                "floors": floors,
                "elevation_m": round(elev, 2),
                "area_m2": round(size * 111320 * size * 111320 * 0.7, 0),
            })
        buildings_gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")

    return shoreline_gdf, buildings_gdf


@st.cache_data(show_spinner=False)
def _build_baseline_shoreline_polygon():
    """Fixed baseline polygon (2026 shoreline strip) for comparison tab."""
    lons = np.linspace(CITY_LON_W, CITY_LON_E, 120)
    rng = np.random.RandomState(42)
    noise = rng.normal(0, 0.0008, 120).cumsum() * 0.3
    base_lat = COAST_LAT + noise
    base_lat = np.clip(base_lat, COAST_LAT - 0.008, COAST_LAT + 0.004)

    upper = list(zip(lons, base_lat))
    lower = list(zip(reversed(lons), [lat - 0.003 for lat in reversed(base_lat)]))
    poly = Polygon(upper + lower)
    return poly


def build_flood_polygon(total_flood_level_m: float) -> Polygon:
    """
    Compute dynamic flood polygon purely from total_flood_level_m.
    Inland propagation offset (degrees lat) scales with flood level,
    simulating contour-based inundation on Alexandria's low coastal gradient.
    """
    lons = np.linspace(CITY_LON_W, CITY_LON_E, 120)
    rng = np.random.RandomState(42)
    noise = rng.normal(0, 0.0008, 120).cumsum() * 0.3
    base_lat = COAST_LAT + noise
    base_lat = np.clip(base_lat, COAST_LAT - 0.008, COAST_LAT + 0.004)

    # Dynamic inland advance (degrees latitude) proportional to flood level
    offset = M_PER_FLOOD_LEVEL * total_flood_level_m
    # Also add slight wave irregularity proportional to surge energy
    wave_noise = rng.normal(0, 0.0001 * (total_flood_level_m + 0.1), 120)
    flood_inner_lat = base_lat - offset + wave_noise

    # Sea-side boundary is always north of shoreline
    sea_lat = base_lat + 0.006

    upper = list(zip(lons, sea_lat))
    lower = list(zip(reversed(lons), reversed(flood_inner_lat)))
    try:
        poly = Polygon(upper + lower)
        if not poly.is_valid:
            poly = poly.buffer(0)
    except Exception:
        poly = Polygon()
    return poly


def intersect_buildings(flood_poly: Polygon, buildings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return buildings whose geometry intersects the flood polygon."""
    if flood_poly.is_empty:
        return buildings_gdf.iloc[0:0]
    try:
        flood_gs = gpd.GeoSeries([flood_poly], crs="EPSG:4326")
        mask = buildings_gdf.intersects(flood_gs.iloc[0])
        return buildings_gdf[mask].copy()
    except Exception:
        return buildings_gdf.iloc[0:0]


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY WATER GAUGE
# ─────────────────────────────────────────────────────────────────────────────

def make_water_gauge(total_flood_m: float, surge_m: float, slr_m: float, severity: str, color: str):
    """
    Vertical animated bar chart acting as a water-level gauge (0–2.5 m).
    """
    max_level = 2.5

    # Colour gradient stops
    color_map = {"safe": "#00e676", "warning": "#ffca28", "critical": "#ff5252"}
    bar_color = color_map.get(severity, "#5bc8ff")

    # Background reference bands
    shapes = [
        dict(type="rect", x0=0, x1=1, y0=0,    y1=0.5,  fillcolor="rgba(0,230,118,0.06)", line_width=0),
        dict(type="rect", x0=0, x1=1, y0=0.5,  y1=1.2,  fillcolor="rgba(255,202,40,0.06)", line_width=0),
        dict(type="rect", x0=0, x1=1, y0=1.2,  y1=2.5,  fillcolor="rgba(255,82,82,0.06)", line_width=0),
    ]

    fig = go.Figure()

    # SLR component
    fig.add_trace(go.Bar(
        x=[1], y=[slr_m],
        marker_color="#2060c0",
        name="Sea Level Rise",
        width=0.55,
        base=0,
    ))

    # Storm surge component stacked
    fig.add_trace(go.Bar(
        x=[1], y=[surge_m],
        marker_color=bar_color,
        name="Storm Surge",
        width=0.55,
        base=slr_m,
    ))

    # Danger line at 1.2 m
    fig.add_hline(y=1.2, line_dash="dash", line_color="#ff5252", line_width=1.2,
                  annotation_text="Critical", annotation_font_color="#ff5252",
                  annotation_font_size=9)
    fig.add_hline(y=0.5, line_dash="dot", line_color="#ffca28", line_width=1,
                  annotation_text="Warning", annotation_font_color="#ffca28",
                  annotation_font_size=9)

    fig.update_layout(
        barmode="stack",
        height=360,
        margin=dict(l=4, r=4, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,26,46,0.9)",
        title=dict(
            text=f"<b>Water Level</b><br><span style='font-size:22px;color:{bar_color}'>{total_flood_m:.2f} m</span>",
            font=dict(color="#c8d4e8", size=11, family="Cairo"),
            x=0.5,
        ),
        yaxis=dict(
            range=[0, max_level],
            tickfont=dict(color="#5a7a9a", size=9, family="JetBrains Mono"),
            gridcolor="#1a2840",
            title=dict(text="metres above MSL", font=dict(color="#3a5a7a", size=8)),
            zeroline=False,
        ),
        xaxis=dict(showticklabels=False, showgrid=False),
        legend=dict(
            orientation="h",
            x=0.5, xanchor="center",
            y=-0.06,
            font=dict(color="#6a8aaa", size=8, family="Cairo"),
            bgcolor="rgba(0,0,0,0)",
        ),
        shapes=shapes,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FOLIUM MAP BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def _severity_style(severity: str):
    """Return (fill_color, fill_opacity, line_color) based on severity."""
    if severity == "critical":
        return "#ff2200", 0.38, "#ff5500"
    elif severity == "warning":
        return "#ff9900", 0.30, "#ffbb00"
    else:
        return "#0099ff", 0.22, "#00ccff"


def build_temporal_map(
    flood_poly: Polygon,
    buildings_gdf: gpd.GeoDataFrame,
    hit_buildings: gpd.GeoDataFrame,
    total_flood_m: float,
    severity: str,
    year: int,
    slr_scenario: str,
    weather_label: str,
):
    m = folium.Map(
        location=ALEX_CENTER,
        zoom_start=13,
        tiles="CartoDB.DarkMatter",
        control_scale=True,
    )

    fill_color, fill_opacity, line_color = _severity_style(severity)

    # Flood polygon
    if not flood_poly.is_empty:
        folium.GeoJson(
            flood_poly.__geo_interface__,
            style_function=lambda _: {
                "fillColor": fill_color,
                "color": line_color,
                "weight": 1.8,
                "fillOpacity": fill_opacity,
            },
            tooltip=folium.Tooltip(
                f"<b>Inundation Zone</b><br>"
                f"Total Water Level: {total_flood_m:.2f} m<br>"
                f"Scenario: {weather_label}<br>"
                f"Year: {year}",
                style="background:#0d1a2e;color:#c8d4e8;border:1px solid #1e3055;font-family:Cairo,sans-serif;",
            ),
            name="Flood Zone",
        ).add_to(m)

    # All buildings (dim)
    if not buildings_gdf.empty:
        folium.GeoJson(
            buildings_gdf.__geo_interface__,
            style_function=lambda _: {
                "fillColor": "#1a3050",
                "color": "#223355",
                "weight": 0.5,
                "fillOpacity": 0.6,
            },
            name="All Buildings",
        ).add_to(m)

    # Vulnerable buildings (highlighted)
    if not hit_buildings.empty:
        def hit_style(feat):
            btype = feat["properties"].get("type", "")
            if "Critical" in btype:
                return {"fillColor": "#ff0055", "color": "#ff3388", "weight": 1.5, "fillOpacity": 0.9}
            elif "Industrial" in btype:
                return {"fillColor": "#ff8800", "color": "#ffaa00", "weight": 1.2, "fillOpacity": 0.85}
            elif "Commercial" in btype:
                return {"fillColor": "#ffdd00", "color": "#ffee55", "weight": 1.2, "fillOpacity": 0.8}
            else:
                return {"fillColor": "#ff5500", "color": "#ff7722", "weight": 1, "fillOpacity": 0.75}

        folium.GeoJson(
            hit_buildings.__geo_interface__,
            style_function=hit_style,
            tooltip=folium.GeoJsonTooltip(
                fields=["building_id", "type", "floors", "elevation_m"],
                aliases=["ID", "Type", "Floors", "Elevation (m)"],
                style="background:#0d1a2e;color:#c8d4e8;border:1px solid #ff3300;font-family:Cairo,sans-serif;font-size:12px;",
            ),
            name="Vulnerable Structures",
        ).add_to(m)

    # Legend
    legend_html = f"""
    <div style="
        position:fixed;bottom:20px;right:10px;z-index:9999;
        background:rgba(10,14,26,0.92);border:1px solid #1e3055;
        border-radius:8px;padding:12px 16px;color:#c8d4e8;
        font-family:'Cairo',sans-serif;font-size:12px;min-width:200px;">
      <b style='color:#5bc8ff;font-size:13px;'>🌊 AlexCoast-Watch Pro</b><br>
      <hr style='border-color:#1e3055;margin:6px 0'>
      <span style='color:#6a8aaa;font-size:10px;font-family:JetBrains Mono,monospace;'>YEAR</span>
      <span style='float:right;color:#fff;font-weight:700;'>{year}</span><br>
      <span style='color:#6a8aaa;font-size:10px;font-family:JetBrains Mono,monospace;'>WATER LEVEL</span>
      <span style='float:right;color:#5bc8ff;font-weight:700;'>{total_flood_m:.2f} m</span><br>
      <span style='color:#6a8aaa;font-size:10px;font-family:JetBrains Mono,monospace;'>SLR SCENARIO</span>
      <span style='float:right;color:#a8c8e8;font-size:10px;'>{slr_scenario.split("(")[1].replace(")","") if "(" in slr_scenario else ""}</span><br>
      <span style='color:#6a8aaa;font-size:10px;font-family:JetBrains Mono,monospace;'>WEATHER</span>
      <span style='float:right;color:#ffc;font-size:10px;'>{weather_label}</span><br>
      <hr style='border-color:#1e3055;margin:6px 0'>
      <div style='display:flex;gap:6px;flex-wrap:wrap;font-size:10px;'>
        <span style='color:#0af'>■</span> Sea Rise &nbsp;
        <span style='color:{line_color}'>■</span> Surge Flood<br>
        <span style='color:#ff0055'>■</span> Critical Infra &nbsp;
        <span style='color:#ff8800'>■</span> Industrial<br>
        <span style='color:#ffdd00'>■</span> Commercial &nbsp;
        <span style='color:#ff5500'>■</span> Residential
      </div>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl(collapsed=True).add_to(m)
    return m


def build_comparison_map(
    flood_poly_current: Polygon,
    flood_poly_2050: Polygon,
    buildings_gdf: gpd.GeoDataFrame,
):
    """Side-by-side comparison: current scenario vs. 2050 worst-case."""
    m = folium.Map(location=ALEX_CENTER, zoom_start=13, tiles=None)

    # Left: Current scenario
    left = folium.TileLayer("CartoDB.DarkMatter", name="Current Scenario")
    left.add_to(m)
    if not flood_poly_current.is_empty:
        folium.GeoJson(
            flood_poly_current.__geo_interface__,
            style_function=lambda _: {"fillColor": "#0088ff", "color": "#00aaff", "weight": 1.5, "fillOpacity": 0.3},
        ).add_to(left)

    # Right: 2050 aggressive
    right = folium.TileLayer("CartoDB.DarkMatterNoLabels", name="2050 Projection")
    right.add_to(m)
    if not flood_poly_2050.is_empty:
        folium.GeoJson(
            flood_poly_2050.__geo_interface__,
            style_function=lambda _: {"fillColor": "#ff2200", "color": "#ff4400", "weight": 1.5, "fillOpacity": 0.35},
        ).add_to(right)

    SideBySideLayers(layer_left=left, layer_right=right).add_to(m)
    return m


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0 0.5rem 0;'>
          <span style='font-size:2.2rem;'>🌊</span><br>
          <span style='font-family:Cairo,sans-serif;font-weight:900;font-size:1.1rem;color:#5bc8ff;'>AlexCoast-Watch</span><br>
          <span style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#3a6090;'>PRO · ALEXANDRIA, EGYPT</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='sidebar-section'>📡 TEMPORAL RANGE</div>", unsafe_allow_html=True)
        year = st.slider("Projection Year", min_value=2026, max_value=2100, value=2040, step=1)

        st.markdown("<div class='sidebar-section'>🌡️ CLIMATE SCENARIOS</div>", unsafe_allow_html=True)
        slr_scenario = st.selectbox(
            "Sea Level Rise Pathway",
            list(SLR_SCENARIOS.keys()),
            index=1,
        )

        st.markdown("<div class='sidebar-section'>🌦️ WEATHER & WAVE DYNAMICS</div>", unsafe_allow_html=True)
        weather_event = st.selectbox(
            "Storm / Weather Event",
            list(WEATHER_EVENTS.keys()),
            index=0,
        )

        st.markdown("<div class='sidebar-section'>ℹ️ ABOUT</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:0.75rem;color:#4a6a8a;line-height:1.55;padding:0.3rem 0;'>
        AlexCoast-Watch Pro integrates dynamic sea-level rise projections with real-time storm surge modelling
        for Alexandria's 32 km Mediterranean coastline.<br><br>
        Elevation-based contour flooding replaces static year offsets for physical accuracy.
        </div>
        """, unsafe_allow_html=True)

    return year, slr_scenario, weather_event


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='app-header'>
      <h1>🌊 AlexCoast-Watch Pro</h1>
      <p>Dynamic Coastal Flood Intelligence · Alexandria, Egypt · Mediterranean Basin</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar controls ─────────────────────────────────────────────────────
    year, slr_scenario, weather_event = render_sidebar()

    # ── Derived physics ──────────────────────────────────────────────────────
    slr_rate_cm_yr = SLR_SCENARIOS[slr_scenario]
    years_elapsed = max(0, year - 2026)
    base_slr_m = (slr_rate_cm_yr * years_elapsed) / 100.0

    wx = WEATHER_EVENTS[weather_event]
    surge_m = wx["surge_m"]
    wave_energy = wx["wave_energy"]
    severity = wx["severity"]
    severity_label = wx["label"]
    severity_color = wx["color"]
    weather_short = weather_event.split("(")[-1].replace(")", "") if "(" in weather_event else weather_event.split(" ", 1)[-1]

    total_flood_m = base_slr_m + surge_m

    # ── Load geo data ────────────────────────────────────────────────────────
    with st.spinner("Loading geospatial data…"):
        shoreline_gdf, buildings_gdf = load_geodata()

    # ── Build flood polygon (dynamic, elevation-based) ────────────────────────
    flood_poly = build_flood_polygon(total_flood_m)

    # ── Intersect buildings ──────────────────────────────────────────────────
    hit_buildings = intersect_buildings(flood_poly, buildings_gdf)

    n_hit = len(hit_buildings)
    n_total = len(buildings_gdf)
    pct_hit = (n_hit / n_total * 100) if n_total > 0 else 0
    econ_risk_bn = (n_hit * ECON_VALUE_PER_BLDG) / 1000  # EGP billions
    pop_at_risk = n_hit * 28  # rough occupancy factor

    # ── Severity info box ────────────────────────────────────────────────────
    box_class = {"safe": "info-box", "warning": "warn-box", "critical": "crit-box"}.get(severity, "info-box")
    icon = {"safe": "🟢", "warning": "🟡", "critical": "🔴"}.get(severity, "🔵")
    st.markdown(
        f"<div class='{box_class}'>"
        f"{icon} <b>{severity_label}</b> — {weather_event.split(' ', 1)[-1]} &nbsp;|&nbsp; "
        f"Storm Surge: <b>{surge_m:.2f} m</b> &nbsp;|&nbsp; "
        f"Wave Energy: <b>{wave_energy}</b> &nbsp;|&nbsp; "
        f"Total Flood Level: <b>{total_flood_m:.3f} m</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── TABS ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🌊 Temporal Simulation",
        "📊 Comparison Matrix",
        "🏗️ Infrastructure Risk Explorer",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — Temporal Simulation
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        col_map, col_gauge = st.columns([3, 1])

        with col_map:
            folium_map = build_temporal_map(
                flood_poly=flood_poly,
                buildings_gdf=buildings_gdf,
                hit_buildings=hit_buildings,
                total_flood_m=total_flood_m,
                severity=severity,
                year=year,
                slr_scenario=slr_scenario,
                weather_label=weather_short,
            )
            st_folium(
                folium_map,
                width="100%",
                height=520,
                returned_objects=[],   # prevents rerender loops
            )

        with col_gauge:
            st.markdown(
                f"<div style='text-align:center;padding:0.5rem 0 0 0;'>"
                f"<span class='severity-badge badge-{severity}'>{severity_label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            gauge = make_water_gauge(total_flood_m, surge_m, base_slr_m, severity, severity_color)
            st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

            # Mini stat cards in gauge column
            for label, value, sub in [
                ("SEA LEVEL RISE", f"{base_slr_m*100:.1f} cm", f"Since 2026 · {slr_scenario.split('(')[1].rstrip(')') if '(' in slr_scenario else ''}"),
                ("STORM SURGE", f"{surge_m:.2f} m", wave_energy),
                ("TOTAL WATER", f"{total_flood_m:.3f} m", "Above MSL"),
            ]:
                st.markdown(
                    f"<div class='metric-card' style='margin-bottom:0.5rem;'>"
                    f"<div class='mc-label'>{label}</div>"
                    f"<div class='mc-value' style='font-size:1.3rem;'>{value}</div>"
                    f"<div class='mc-sub'>{sub}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Quick stats row below map
        st.markdown("<hr>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            ("YEAR", str(year), "Projection horizon"),
            ("STRUCTURES AT RISK", f"{n_hit:,}", f"{pct_hit:.1f}% of inventory"),
            ("POPULATION EXPOSED", f"{pop_at_risk:,}", "Estimated occupants"),
            ("ECONOMIC EXPOSURE", f"EGP {econ_risk_bn:.2f}B", "Replacement value"),
        ]
        for col, (label, value, sub) in zip([c1, c2, c3, c4], cards):
            col.markdown(
                f"<div class='metric-card'>"
                f"<div class='mc-label'>{label}</div>"
                f"<div class='mc-value'>{value}</div>"
                f"<div class='mc-sub'>{sub}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — Comparison Matrix
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("""
        <div style='font-size:0.85rem;color:#7a9ab8;margin-bottom:1rem;font-family:Cairo,sans-serif;'>
        <b style='color:#5bc8ff;'>Side-by-side comparison:</b>
        Current selected scenario (left) vs. 2100 Aggressive RCP 8.5 worst-case extreme storm (right).
        Drag the central divider to compare inundation extents.
        </div>
        """, unsafe_allow_html=True)

        # 2050 worst-case: aggressive SLR × 74 years + 50-year storm surge
        worst_slr_m = (9.4 * 74) / 100.0
        worst_flood_m = worst_slr_m + 1.35
        flood_poly_2100_worst = build_flood_polygon(worst_flood_m)

        comp_map = build_comparison_map(flood_poly, flood_poly_2100_worst, buildings_gdf)
        st_folium(
            comp_map,
            width="100%",
            height=540,
            returned_objects=[],
        )

        # Comparison table
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**Scenario Comparison Table**", unsafe_allow_html=False)

        hit_2100 = intersect_buildings(flood_poly_2100_worst, buildings_gdf)
        n_2100 = len(hit_2100)

        comp_df = pd.DataFrame({
            "Metric": [
                "Total Water Level (m)",
                "Sea Level Rise (m)",
                "Storm Surge (m)",
                "Structures at Risk",
                "Population Exposed",
                "Economic Exposure (EGP B)",
            ],
            "Current Scenario": [
                f"{total_flood_m:.3f}",
                f"{base_slr_m:.3f}",
                f"{surge_m:.2f}",
                f"{n_hit:,}",
                f"{n_hit * 28:,}",
                f"{(n_hit * ECON_VALUE_PER_BLDG)/1000:.2f}",
            ],
            "2100 Worst-Case": [
                f"{worst_flood_m:.3f}",
                f"{worst_slr_m:.3f}",
                "1.35",
                f"{n_2100:,}",
                f"{n_2100 * 28:,}",
                f"{(n_2100 * ECON_VALUE_PER_BLDG)/1000:.2f}",
            ],
        })
        st.dataframe(
            comp_df,
            use_container_width=True,
            hide_index=True,
        )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — Infrastructure Risk Explorer
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown(f"""
        <div style='font-size:0.85rem;color:#7a9ab8;margin-bottom:1rem;font-family:Cairo,sans-serif;'>
        Infrastructure vulnerability assessment for <b style='color:#5bc8ff;'>Year {year}</b> &nbsp;·&nbsp;
        Water level <b style='color:#5bc8ff;'>{total_flood_m:.3f} m</b> &nbsp;·&nbsp;
        <span class='severity-badge badge-{severity}'>{severity_label}</span>
        </div>
        """, unsafe_allow_html=True)

        # Metric cards row
        mc1, mc2, mc3, mc4 = st.columns(4)
        type_counts = hit_buildings["type"].value_counts() if not hit_buildings.empty else pd.Series(dtype=int)

        crit_count = type_counts.get("Critical Infrastructure", 0)
        indus_count = type_counts.get("Industrial", 0)
        comm_count = type_counts.get("Commercial", 0)
        resid_count = type_counts.get("Residential", 0)

        for col, (label, value, sub, color) in zip([mc1, mc2, mc3, mc4], [
            ("CRITICAL INFRASTRUCTURE", str(crit_count), "Hospitals, utilities, ports", "#ff0055"),
            ("INDUSTRIAL FACILITIES", str(indus_count), "Factories & warehouses", "#ff8800"),
            ("COMMERCIAL ZONES", str(comm_count), "Retail & office buildings", "#ffdd00"),
            ("RESIDENTIAL UNITS", str(resid_count), "Homes & apartments", "#ff5500"),
        ]):
            col.markdown(
                f"<div class='metric-card'>"
                f"<div class='mc-label'>{label}</div>"
                f"<div class='mc-value' style='color:{color};font-size:2rem;'>{value}</div>"
                f"<div class='mc-sub'>{sub}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)
        col_chart, col_table = st.columns([1, 2])

        with col_chart:
            # Building type distribution donut
            if not hit_buildings.empty:
                tc = hit_buildings["type"].value_counts()
                donut_colors = ["#ff0055", "#ff8800", "#ffdd00", "#ff5500", "#5bc8ff"]
                fig_donut = go.Figure(go.Pie(
                    labels=tc.index.tolist(),
                    values=tc.values.tolist(),
                    hole=0.58,
                    marker=dict(colors=donut_colors[:len(tc)], line=dict(color="#0a0e1a", width=2)),
                    textfont=dict(color="#c8d4e8", family="Cairo", size=10),
                ))
                fig_donut.update_layout(
                    title=dict(text="At-Risk Building Types", font=dict(color="#c8d4e8", size=12, family="Cairo"), x=0.5),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(font=dict(color="#6a8aaa", size=9, family="Cairo"), bgcolor="rgba(0,0,0,0)"),
                    height=280,
                    margin=dict(l=10, r=10, t=40, b=10),
                )
                st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No buildings at risk under current water level.")

            # SLR over time for current scenario
            yrs = np.arange(2026, 2101)
            slr_curve = [(slr_rate_cm_yr * (y - 2026)) / 100 for y in yrs]
            fig_slr = go.Figure()
            fig_slr.add_trace(go.Scatter(
                x=yrs, y=slr_curve,
                mode="lines",
                line=dict(color="#0af", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,170,255,0.1)",
                name="SLR (m)",
            ))
            fig_slr.add_vline(x=year, line_dash="dash", line_color="#ffca28", line_width=1.2)
            fig_slr.update_layout(
                title=dict(text="Sea Level Rise Trajectory", font=dict(color="#c8d4e8", size=11, family="Cairo"), x=0.5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,26,46,0.9)",
                xaxis=dict(gridcolor="#1a2840", tickfont=dict(color="#5a7a9a", size=9, family="JetBrains Mono")),
                yaxis=dict(gridcolor="#1a2840", tickfont=dict(color="#5a7a9a", size=9, family="JetBrains Mono"),
                           title=dict(text="m above 2026", font=dict(color="#3a5a7a", size=8))),
                legend=dict(font=dict(color="#6a8aaa", size=9), bgcolor="rgba(0,0,0,0)"),
                height=220,
                margin=dict(l=10, r=10, t=35, b=10),
            )
            st.plotly_chart(fig_slr, use_container_width=True, config={"displayModeBar": False})

        with col_table:
            if not hit_buildings.empty:
                display_df = hit_buildings[[
                    "building_id", "type", "floors", "elevation_m", "area_m2"
                ]].copy()
                display_df["econ_value_egp_m"] = ECON_VALUE_PER_BLDG
                display_df["flood_depth_est_m"] = (total_flood_m - display_df["elevation_m"]).clip(lower=0).round(3)
                display_df.columns = [
                    "Building ID", "Type", "Floors", "Elevation (m)", "Area (m²)",
                    "Value (EGP M)", "Est. Flood Depth (m)"
                ]
                display_df = display_df.sort_values("Est. Flood Depth (m)", ascending=False)

                st.markdown(
                    f"<div class='mc-label' style='margin-bottom:0.5rem;'>VULNERABLE STRUCTURES — {n_hit} RECORDS</div>",
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=460,
                )
            else:
                st.markdown(
                    "<div class='info-box'>✅ No structures are projected to be inundated at the current water level configuration. "
                    "Adjust the storm surge or sea level rise pathway to model higher-risk scenarios.</div>",
                    unsafe_allow_html=True,
                )

        # Storm surge scenario comparison bar chart
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**Storm Surge Sensitivity Analysis**", unsafe_allow_html=False)

        surge_values = [0.0, 0.50, 1.35]
        surge_labels = ["Normal Tide", "Winter Nawa", "50-Year Storm"]
        hit_counts = []
        for sv in surge_values:
            fp = build_flood_polygon(base_slr_m + sv)
            hb = intersect_buildings(fp, buildings_gdf)
            hit_counts.append(len(hb))

        fig_bar = go.Figure(go.Bar(
            x=surge_labels,
            y=hit_counts,
            marker_color=["#00e676", "#ffca28", "#ff5252"],
            text=hit_counts,
            textposition="outside",
            textfont=dict(color="#c8d4e8", size=11, family="Cairo"),
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,26,46,0.9)",
            xaxis=dict(gridcolor="#1a2840", tickfont=dict(color="#c8d4e8", size=11, family="Cairo")),
            yaxis=dict(gridcolor="#1a2840", tickfont=dict(color="#5a7a9a", size=9, family="JetBrains Mono"),
                       title=dict(text="Structures at Risk", font=dict(color="#3a5a7a", size=9))),
            height=260,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


if __name__ == "__main__":
    main()