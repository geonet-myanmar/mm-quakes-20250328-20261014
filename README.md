# Myanmar Seismic Activity (March 28, 2025 – Present) & GEM Active Faults Web Map

![USGS Catalog](https://img.shields.io/badge/Data-USGS_Earthquake_Catalog-blue)
![GEM Active Faults](https://img.shields.io/badge/Faults-GEM_GAF--DB-red)
![Leaflet.js](https://img.shields.io/badge/Map-Leaflet.js_1.9.4-green)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)

An end-to-end geospatial data pipeline and standalone interactive web map visualizing seismic events across **Myanmar** from **March 28, 2025** (the $M_w$ 7.7 Mandalay earthquake sequence) to the present, overlaid on tectonic fault traces from the **GEM Global Active Faults Database**.

---

## 📌 Project Overview

On **March 28, 2025**, a catastrophic **$M_w$ 7.7 strike-slip earthquake** (`us7000pn9s`) ruptured the **Sagaing Fault** near Mandalay and Sagaing in central Myanmar at a shallow depth of 10 km, followed minutes later by a **$M_w$ 6.7 aftershock** (`us7000pn9z`) and an extensive aftershock sequence along the fault zone. 

This repository provides:
1. **Automated Data Extraction (`fetch_data.py`):** A Python script that queries the USGS FDSN Event Web Service API and the GEM Global Active Faults GitHub repository, spatially clips both datasets to Myanmar's boundaries, and exports standards-compliant GeoJSON files.
2. **Pre-Exported GeoJSON Datasets:**
   - `myanmar_earthquakes.geojson`: Point features of earthquakes occurring within Myanmar from `2025-03-28T00:00:00` UTC to present.
   - `myanmar_active_faults.geojson`: LineString fault traces across Myanmar extracted from the GEM Global Active Faults Database (`HimaTibetMap` and `EOS_SE_Asia` catalogs).
3. **Zero-Config Interactive Web Map (`index.html`):** A single-file HTML/CSS/JavaScript application built with **Leaflet.js** and keyless **Esri ArcGIS Online** basemaps that works both via `file:///` (offline/local double-click) and on **GitHub Pages**.

---

## 📂 Repository Structure

```text
├── index.html                      # Standalone interactive Leaflet web map
├── fetch_data.py                   # Python script to fetch & clip USGS + GEM datasets
├── myanmar_earthquakes.geojson     # Exported USGS earthquake catalog for Myanmar
├── myanmar_active_faults.geojson   # Exported GEM active fault traces for Myanmar
└── README.md                       # Project documentation