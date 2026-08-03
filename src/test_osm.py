import osmnx as ox

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.log_console = False

print("Downloading building data for Innsbruck from OpenStreetMap...")

# Download buildings
place_name = "Innsbruck, Austria"
buildings = ox.features_from_place(place_name, tags={"building": True})

print(f"✅ Success! Downloaded {len(buildings)} buildings")
print("\nFirst few rows:")
print(buildings.head())
print("\nColumns:", list(buildings.columns))
