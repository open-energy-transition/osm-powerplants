# Workshop: Data Quality Improvement

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/open-energy-transition/osm-powerplants/blob/main/notebooks/workshop_data_quality.ipynb)

This interactive workshop demonstrates the complete workflow for improving OpenStreetMap power plant data quality using the `osm-powerplants` package.

## What You'll Learn

1. **Extract** power plant data from OpenStreetMap
2. **Analyze** why certain plants fail validation (rejection tracking)
3. **Export** issues as GeoJSON for fixing in JOSM
4. **Visualize** data on interactive maps
5. **Verify** improvements after OSM edits

## Prerequisites

- Basic Python knowledge
- Google account (for Colab) or local Python environment
- Optional: [JOSM](https://josm.openstreetmap.de/) for editing OSM data

## Running the Workshop

### Option 1: Google Colab (Recommended)

Click the "Open in Colab" badge above to run the workshop in your browser. No installation required!

### Option 2: Local Environment

```bash
pip install osm-powerplants folium jupyter
jupyter notebook notebooks/workshop_data_quality.ipynb
```

## Workshop Sections

### 1. Setup
Install the package and import required modules.

### 2. Extract Power Plant Data
Fetch data for a small country (Malta) to demonstrate the extraction process.

### 3. Rejection Analysis
The key feature! Learn why OSM elements fail validation:

- Missing source type → Add `plant:source` tag
- Missing technology type → Add `plant:method` tag  
- Missing output tag → Add `plant:output:electricity` tag
- And more...

### 4. Export for JOSM
Generate GeoJSON files that can be loaded into JOSM as a hint layer for fixing issues.

### 5. Interactive Maps
Visualize both rejected elements and valid plants on interactive Folium maps.

### 6. Verification
Re-run the extraction after making OSM edits to measure improvements.

## The Feedback Loop

```
osm-powerplants → Identify Issues → Fix in JOSM → Upload to OSM → Verify Improvements
       ↑                                                                    │
       └────────────────────────────────────────────────────────────────────┘
```

This workflow enables continuous improvement of OSM power plant data, which ultimately improves energy system models built with [powerplantmatching](https://github.com/PyPSA/powerplantmatching) and [PyPSA-Eur](https://github.com/PyPSA/pypsa-eur).

## Related Resources

- [Quality Tracking Guide](quality-tracking.md) - Detailed documentation on rejection tracking
- [MapYourGrid](https://mapyourgrid.org/strategies/#improve-osm-tags-with-ppm) - Community mapping strategies
- [JOSM](https://josm.openstreetmap.de/) - OSM editor for fixing data issues
