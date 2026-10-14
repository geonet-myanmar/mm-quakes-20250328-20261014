import json
from datetime import datetime, timezone
import requests

# Optional spatial clipping using GeoPandas; falls back to pure-Python bounding box if unavailable
try:
    import geopandas as gpd
    from shapely.geometry import shape
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

# Myanmar Bounding Box
MIN_LAT, MAX_LAT = 9.5, 28.6
MIN_LON, MAX_LON = 92.1, 101.2
START_DATE = "2025-03-28T00:00:00"
END_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

USGS_URL = (
    f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
    f"format=geojson&starttime={START_DATE}&endtime={END_DATE}"
    f"&minlatitude={MIN_LAT}&maxlatitude={MAX_LAT}"
    f"&minlongitude={MIN_LON}&maxlongitude={MAX_LON}"
    f"&limit=20000&orderby=time-asc"
)

GEM_URL = "https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/geojson/gem_active_faults.geojson"
ADMIN_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"


def get_myanmar_polygon():
    """Fetches Myanmar's exact country polygon for accurate spatial filtering."""
    if not HAS_GEOPANDAS:
        return None
    try:
        resp = requests.get(ADMIN_URL, timeout=30)
        resp.raise_for_status()
        countries = gpd.GeoDataFrame.from_features(resp.json()["features"], crs="EPSG:4326")
        mmr = countries[countries["ADM0_A3"] == "MMR"]
        if not mmr.empty:
            return mmr.geometry.iloc[0]
    except Exception as e:
        print(f"Warning: Could not fetch exact polygon ({e}). Using bounding box filter.")
    return None


def coord_in_bbox(coords, geom_type):
    """Pure-Python recursive coordinate check against Myanmar's bounding box."""
    if geom_type == "Point":
        lon, lat = coords[0], coords[1]
        return MIN_LON <= lon <= MAX_LON and MIN_LAT <= lat <= MAX_LAT
    elif geom_type in ("LineString", "MultiPoint"):
        return any(MIN_LON <= c[0] <= MAX_LON and MIN_LAT <= c[1] <= MAX_LAT for c in coords)
    elif geom_type in ("MultiLineString", "Polygon"):
        return any(
            any(MIN_LON <= c[0] <= MAX_LON and MIN_LAT <= c[1] <= MAX_LAT for c in part)
            for part in coords
        )
    return False


def download_and_export_earthquakes(mmr_poly=None):
    print(f"1. Querying USGS Catalog ({START_DATE} to {END_DATE})...")
    resp = requests.get(USGS_URL, timeout=60)
    resp.raise_for_status()
    eq_data = resp.json()

    features = eq_data.get("features", [])
    if mmr_poly is not None:
        filtered = []
        for f in features:
            pt = shape(f["geometry"])
            # Include events inside Myanmar polygon or explicitly tagged in Myanmar/Burma
            place = (f.get("properties", {}).get("place") or "").lower()
            if mmr_poly.contains(pt) or "myanmar" in place or "burma" in place:
                filtered.append(f)
        eq_data["features"] = filtered

    out_file = "myanmar_earthquakes.geojson"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(eq_data, f, ensure_ascii=False, indent=2)
    print(f"   -> Saved {len(eq_data['features'])} earthquake events to '{out_file}'.")


def download_and_export_faults(mmr_poly=None):
    print("2. Downloading GEM Global Active Faults Database from GitHub...")
    resp = requests.get(GEM_URL, timeout=120)
    resp.raise_for_status()
    gem_data = resp.json()

    features = gem_data.get("features", [])
    filtered_faults = []

    for f in features:
        geom = f.get("geometry")
        if not geom or not geom.get("coordinates"):
            continue
        if coord_in_bbox(geom["coordinates"], geom["type"]):
            if mmr_poly is not None:
                if shape(geom).intersects(mmr_poly):
                    filtered_faults.append(f)
            else:
                filtered_faults.append(f)

    out_geojson = {
        "type": "FeatureCollection",
        "name": "Myanmar_GEM_Active_Faults",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": filtered_faults,
    }

    out_file = "myanmar_active_faults.geojson"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_geojson, f, ensure_ascii=False, indent=2)
    print(f"   -> Saved {len(filtered_faults)} active fault traces to '{out_file}'.")


if __name__ == "__main__":
    polygon = get_myanmar_polygon()
    download_and_export_earthquakes(polygon)
    download_and_export_faults(polygon)
    print("Done! Open index.html to view the interactive map.")