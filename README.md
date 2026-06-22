# 🌊 AlexCoast-Watch Pro

> **Dynamic Coastal Flood Intelligence Platform for Alexandria, Egypt**  
> An advanced geospatial analytics and interactive web application designed to simulate, visualize, and assess coastal inundation risk along Alexandria's 32 km Mediterranean shoreline up to the year 2100.

---

## 📌 Project Overview

**AlexCoast-Watch Pro** is a professional-grade geospatial intelligence dashboard built with Python and Streamlit. The application integrates localized Sea Level Rise (SLR) projections—modeled after IPCC Representative Concentration Pathways (RCP 2.6, RCP 4.5, and RCP 8.5)—with extreme weather event simulations (such as the historic Mediterranean winter "Nawa" or 50-year return storms).

Unlike static historical mapping tools, `main.py` utilizes an **elevation-based contour flooding pipeline**. By combining dynamic hydrodynamic modeling with precise vertical topography, the platform evaluates risk at an individual asset level—checking structural terrain elevation (`elevation_m`) against calculated water levels to deliver immediate financial, demographic, and infrastructure hazard metrics.

---

## ✨ Key Features

- **🌊 Dynamic Hydrodynamic Simulation:** Accurately models inland flood propagation adjusted to Alexandria’s low-lying coastal gradient topology (~1:500 structural slope).
- **🗺️ Split-Screen Temporal Comparison:** Leverages Folium's side-by-side layer plugin, enabling users to visually swipe and compare the current scenario against the 2100 aggressive worst-case trajectory.
- **🏗️ Infrastructure Vulnerability Explorer:** Segregates real-time operational risk into actionable asset classes: *Critical Infrastructure (Hospitals, Ports, Utilities), Industrial Facilities, Commercial Zones, and Residential Units*.
- **📊 Parametric Financial & Demographic Risk Models:** Computes cumulative local exposure, estimating immediate structural replacement costs in Egyptian Pounds (EGP Billions) alongside impacted population counts.
- **🎨 Bespoke Dark Cyberpunk Interface:** Features custom inline styling (`DARK_CSS`), fully optimizing UI controls, Plotly animated telemetry gauges, responsive data grids, and multi-lingual tailored typography (`Cairo` & `JetBrains Mono`).

---

## 🛠️ Architecture & Tech Stack

- **Application Framework:** Streamlit (UI Engine & reactive state binding)
- **Geospatial Pipeline:** GeoPandas & Shapely (Spatial relationships, geometric intersections, and vector projections)
- **Interactive Geospatial Visualization:** Folium & Streamlit-Folium (Web-mapping engine utilizing CartoDB dark-matter canvas)
- **Analytical Telemetry:** Plotly Graph Objects (Interactive water gauges, donut distributions, and timeline trajectories)
- **Core Math & Pipelines:** NumPy & Pandas (Stochastic synthesis, linear interpolation, and tabular filtering)

---

## 📁 Repository Structure

```text
├── main.py                    # Core Application Source Code
├── shoreline_2026.geojson      # (Optional) Actual Mediterranean baseline shoreline vector data
├── alex_buildings.geojson     # (Optional) Structural asset inventory and elevation database
├── README.md                  # Project Documentation
└── requirements.txt           # Python Project Dependencies
