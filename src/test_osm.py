import osmnx as ox
import geopandas as gpd
import pandas as pd
import os

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.log_console = False

print("=" * 50)
print("DAY 1: Solar Potential Data Pipeline")
print("=" * 50)

print("\n[Step 1/4] Downloading buildings from OpenStreetMap...")
place_name = "Innsbruck, Austria"
buildings = ox.features_from_place(place_name, tags={"building": True})
print(f"Downloaded {len(buildings)} total buildings")

print("\n[Step 2/4] Filtering for building polygons (footprints)...")
polygons_only = buildings[buildings['geometry'].apply(lambda geom: geom.geom_type == 'Polygon')]
print(f"Found {len(polygons_only)} buildings with actual footprints ({len(polygons_only)/len(buildings)*100:.1f}%)")

print("\n[Step 3/4] Calculating rooftop area...")
polygons_only = polygons_only.to_crs(epsg=3857)  # Convert to metric CRS
polygons_only['roof_area_m2'] = polygons_only.geometry.area
print(f"Average roof area: {polygons_only['roof_area_m2'].mean():.2f} m²")
print(f"Max roof area: {polygons_only['roof_area_m2'].max():.2f} m²")
print(f"Min roof area: {polygons_only['roof_area_m2'].min():.2f} m²")

print("\n[Step 4/4] Saving to CSV...")
os.makedirs('data/processed', exist_ok=True)
csv_path = 'data/processed/buildings_clean.csv'
polygons_only.drop(columns=['geometry'], inplace=True)
polygons_only.to_csv(csv_path, index=False)
print(f"Saved to {csv_path}")

print("\n✅ Day 1 Task Complete!")
print(f"\nSummary:")
print(f"- Total buildings downloaded: {len(buildings)}")
print(f"- Buildings with footprints: {len(polygons_only)}")
print(f"- Mean rooftop area: {polygons_only['roof_area_m2'].mean():.1f} m²")
print(f"- Total potential rooftop area: {polygons_only['roof_area_m2'].sum()/1e6:.2f} km²")
