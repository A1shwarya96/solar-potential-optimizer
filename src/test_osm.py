import osmnx as ox
import geopandas as gpd
import pandas as pd
import requests
import json
import os

ox.settings.use_cache = True
ox.settings.log_console = False

print("=" * 50)
print("DAY 2: Adding Solar Irradiance & Energy Potential")
print("=" * 50)

print("\n[Step 1/4] Downloading buildings from OpenStreetMap...")
place_name = "Innsbruck, Austria"
buildings = ox.features_from_place(place_name, tags={"building": True})

print("\n[Step 2/4] Filtering polygons and calculating roof area...")
polygons = buildings[buildings['geometry'].apply(lambda g: g.geom_type == 'Polygon')].copy()
polygons = polygons.to_crs(epsg=3857) # Metric for area
polygons['roof_area_m2'] = polygons.geometry.area

# Keep only useful columns + geometry
cols_to_keep = ['name', 'roof_area_m2', 'geometry']
polygons = polygons[[c for c in cols_to_keep if c in polygons.columns]].copy()

print("\n[Step 3/4] Fetching solar irradiance from PVGIS API...")
pvgis_url = "https://re.jrc.ec.europa.eu/api/TMY?lat=47.2692&lon=11.4041&outputformat=json"

try:
    response = requests.get(pvgis_url, timeout=30)
    response.raise_for_status()
    pvgis_data = response.json()
    
    hourly_data = pvgis_data['outputs']['tmy_hourly']
    df_irradiance = pd.DataFrame(hourly_data)
    
    # G(h) is Global Horizontal Irradiance in Wh/m²
    total_irradiance_kwh_m2_yr = df_irradiance['G(h)'].sum() / 1000
    print(f"✅ Fetched! Annual solar irradiance: {total_irradiance_kwh_m2_yr:.2f} kWh/m²/yr")

except Exception as e:
    print(f"⚠️ Could not fetch PVGIS data ({e}). Using fallback (1100 kWh/m²/yr).")
    total_irradiance_kwh_m2_yr = 1100.0

print("\n[Step 4/4] Calculating energy potential per building...")
# Area × Irradiance × Efficiency(0.20) × System Losses(0.80)
panel_efficiency = 0.20
performance_ratio = 0.80

polygons['potential_kwh_yr'] = (
    polygons['roof_area_m2'] * 
    total_irradiance_kwh_m2_yr * 
    panel_efficiency * 
    performance_ratio
)

# Prepare for CSV: Convert back to GPS coordinates and save geometry as text
polygons = polygons.to_crs(epsg=4326)
polygons['geometry_wkt'] = polygons['geometry'].to_wkt()

os.makedirs('data/processed', exist_ok=True)
csv_path = 'data/processed/buildings_with_solar.csv'

# Save without the geopandas geometry column, but with our text version
polygons.drop(columns=['geometry']).to_csv(csv_path, index=False)

print(f"\n✅ Saved enriched data to {csv_path}")
print("\n" + "=" * 50)
print("DAY 2 SUMMARY")
print("=" * 50)
print(f"Total buildings: {len(polygons)}")
print(f"Total potential energy: {polygons['potential_kwh_yr'].sum() / 1e6:.2f} GWh/yr")
print("\nTop 5 buildings by energy potential:")
print(polygons.nlargest(5, 'potential_kwh_yr')[['name', 'roof_area_m2', 'potential_kwh_yr']])
