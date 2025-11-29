# Extending OSM Power Plants

This guide shows how to extend and customize the package for specific needs.

## Custom Configuration

### Adding New Source Mappings

To recognize additional OSM source tags:

```yaml
# custom-config.yaml
source_mapping:
  Solar:
    - solar
    - photovoltaic
    - pv_system        # Custom addition
    - solar_thermal    # Custom addition

  # New fuel type
  Hydrogen:
    - hydrogen
    - h2
    - fuel_cell
```

### Adding New Technology Mappings

```yaml
technology_mapping:
  PV:
    - photovoltaic
    - solar_photovoltaic_panel
    - bifacial_pv      # Custom addition
    - floating_pv      # Custom addition
```

## Custom Parsers

### Extending the Base Parser

```python
from osm_powerplants.parsing.base import BaseParser
from osm_powerplants.models import Unit

class CustomPlantParser(BaseParser):
    """Parser with custom logic for specific regions."""

    def process_element(self, element, country, processed_ids):
        # Call parent implementation
        unit = super().process_element(element, country, processed_ids)

        if unit is None:
            return None

        # Add custom post-processing
        unit = self._apply_regional_corrections(unit, country)

        return unit

    def _apply_regional_corrections(self, unit, country):
        """Apply country-specific corrections."""
        if country == "Germany":
            # German-specific capacity corrections
            if unit.Fueltype == "Solar" and unit.Capacity:
                # Apply known systematic bias correction
                unit.Capacity *= 0.95

        return unit
```

### Custom Capacity Extraction

```python
from osm_powerplants.parsing.capacity import CapacityExtractor

class CustomCapacityExtractor(CapacityExtractor):
    """Extended capacity extraction with custom patterns."""

    def __init__(self, config):
        super().__init__(config)

        # Add custom regex patterns
        self.custom_patterns = [
            r"(\d+)\s*turbines?\s*@\s*(\d+(?:\.\d+)?)\s*MW",  # "10 turbines @ 3.5 MW"
            r"(\d+)x(\d+(?:\.\d+)?)\s*MW",  # "10x3.5 MW"
        ]

    def extract_capacity(self, tags, source_type=None):
        # Try parent extraction first
        success, capacity, source = super().extract_capacity(tags, source_type)

        if success:
            return success, capacity, source

        # Try custom patterns
        return self._try_custom_patterns(tags)

    def _try_custom_patterns(self, tags):
        import re

        for tag_key in ["plant:output:electricity", "description"]:
            if tag_key not in tags:
                continue

            value = tags[tag_key]

            # Pattern: "10 turbines @ 3.5 MW"
            match = re.match(r"(\d+)\s*turbines?\s*@\s*(\d+(?:\.\d+)?)\s*MW", value)
            if match:
                count = int(match.group(1))
                per_unit = float(match.group(2))
                return True, count * per_unit, "custom_turbine_pattern"

        return False, None, "no_match"
```

## Custom Enhancement Modules

### Custom Clustering Algorithm

```python
from osm_powerplants.enhancement.clustering import ClusteringManager
from osm_powerplants.models import Unit
import numpy as np

class CustomClusteringManager(ClusteringManager):
    """Clustering with custom algorithm for specific fuel types."""

    def cluster_generators(self, generators, source_type):
        if source_type == "Solar":
            # Use custom solar-specific clustering
            return self._cluster_solar_farms(generators)

        # Fall back to default
        return super().cluster_generators(generators, source_type)

    def _cluster_solar_farms(self, generators):
        """Custom clustering for solar farms based on naming patterns."""
        from collections import defaultdict

        # Group by name similarity
        name_groups = defaultdict(list)

        for gen in generators:
            if gen.Name:
                # Extract base name (remove numbers, suffixes)
                base_name = self._extract_base_name(gen.Name)
                name_groups[base_name].append(gen)
            else:
                name_groups["unnamed"].append(gen)

        # Convert to cluster format
        clusters = []
        for name, gens in name_groups.items():
            if len(gens) >= 2:
                clusters.append({
                    "generators": gens,
                    "centroid": self._calculate_centroid(gens),
                    "name": name
                })

        return True, clusters

    def _extract_base_name(self, name):
        import re
        # Remove trailing numbers and common suffixes
        return re.sub(r'\s*[IVX\d]+$', '', name).strip()

    def _calculate_centroid(self, generators):
        lats = [g.lat for g in generators if g.lat]
        lons = [g.lon for g in generators if g.lon]
        return (np.mean(lats), np.mean(lons)) if lats else (None, None)
```

### Custom Capacity Estimation

```python
from osm_powerplants.enhancement.estimation import CapacityEstimator

class RegionalCapacityEstimator(CapacityEstimator):
    """Capacity estimation with regional efficiency factors."""

    # Regional solar irradiance factors (relative to reference)
    REGIONAL_FACTORS = {
        "ES": 1.15,  # Spain - high irradiance
        "DE": 0.90,  # Germany - moderate irradiance
        "NO": 0.75,  # Norway - low irradiance
    }

    def estimate_solar_capacity(self, unit, geometry_area_m2):
        # Base estimation
        base_efficiency = 150  # W/m²

        # Apply regional factor
        country_code = self._get_country_code(unit.Country)
        factor = self.REGIONAL_FACTORS.get(country_code, 1.0)

        adjusted_efficiency = base_efficiency * factor
        capacity_mw = geometry_area_m2 * adjusted_efficiency / 1_000_000

        return capacity_mw
```

## Custom Data Sources

### Adding Alternative API Endpoints

```python
from osm_powerplants.retrieval.client import OverpassAPIClient

class MultiEndpointClient(OverpassAPIClient):
    """Client with fallback to alternative Overpass endpoints."""

    ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]

    def query_overpass(self, query):
        last_error = None

        for endpoint in self.ENDPOINTS:
            try:
                self.api_url = endpoint
                return super().query_overpass(query)
            except Exception as e:
                last_error = e
                continue

        raise last_error
```

## Custom Output Formats

### GeoPackage Export

```python
from osm_powerplants import Units
import geopandas as gpd

def export_to_geopackage(units: Units, filepath: str):
    """Export units to GeoPackage format."""
    df = units.to_dataframe()

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.lon, df.lat),
        crs="EPSG:4326"
    )

    # Add additional metadata
    gdf["source"] = "OpenStreetMap"
    gdf["extraction_date"] = pd.Timestamp.now().isoformat()

    # Export
    gdf.to_file(filepath, driver="GPKG")
```

### PowerWorld Export

```python
def export_to_powerworld(units: Units, filepath: str):
    """Export to PowerWorld auxiliary format."""
    df = units.to_dataframe()

    # Map to PowerWorld fields
    pw_df = pd.DataFrame({
        "BusNum": range(1, len(df) + 1),
        "BusName": df["Name"].fillna("Unknown"),
        "GenID": df["projectID"],
        "GenMW": df["Capacity"],
        "Latitude": df["lat"],
        "Longitude": df["lon"],
        "FuelType": df["Fueltype"].map(FUELTYPE_MAPPING),
    })

    # Write auxiliary file
    with open(filepath, "w") as f:
        f.write("DATA (GEN, [BusNum, BusName, GenID, GenMW, Latitude, Longitude, FuelType])\n")
        for _, row in pw_df.iterrows():
            f.write(f"{row['BusNum']} \"{row['BusName']}\" \"{row['GenID']}\" ")
            f.write(f"{row['GenMW']:.2f} {row['Latitude']:.6f} {row['Longitude']:.6f} ")
            f.write(f"\"{row['FuelType']}\"\n")
```

## Integrating with Workflows

### Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def process_osm_data(**context):
    from osm_powerplants import process_countries_simple, get_config, get_cache_dir

    config = get_config()
    config["force_refresh"] = True  # Always fresh data

    countries = context["params"]["countries"]
    output_path = context["params"]["output_path"]

    df = process_countries_simple(
        countries=countries,
        config=config,
        cache_dir=str(get_cache_dir(config)),
        output_path=output_path,
    )

    return {"count": len(df), "total_capacity": df["Capacity"].sum()}

with DAG(
    "osm_powerplants",
    default_args={"retries": 3, "retry_delay": timedelta(minutes=5)},
    schedule_interval="@weekly",
    start_date=datetime(2024, 1, 1),
) as dag:

    process_europe = PythonOperator(
        task_id="process_europe",
        python_callable=process_osm_data,
        params={
            "countries": ["Germany", "France", "Spain", "Italy"],
            "output_path": "/data/osm_europe.csv"
        }
    )
```

### Prefect Flow

```python
from prefect import flow, task

@task
def fetch_osm_data(countries: list[str]) -> pd.DataFrame:
    from osm_powerplants import process_countries_simple, get_config, get_cache_dir

    config = get_config()
    return process_countries_simple(
        countries=countries,
        config=config,
        cache_dir=str(get_cache_dir(config)),
    )

@task
def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    # Custom validation
    assert len(df) > 0, "No data extracted"
    assert df["Capacity"].sum() > 0, "No capacity data"
    return df

@flow
def osm_extraction_flow(countries: list[str], output_path: str):
    df = fetch_osm_data(countries)
    df = validate_data(df)
    df.to_csv(output_path, index=False)
    return len(df)
```
