import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
import matplotlib.pyplot as plt

print("=" * 50)
print("VISUALIZATION: Generating Maps and Charts")
print("=" * 50)

# 1. Load Data
print("Loading data...")
df_selected = pd.read_csv('data/processed/selected_buildings.csv')
df_all = pd.read_csv('data/processed/buildings_with_solar.csv')

# Convert WKT strings back to geometric polygons
df_selected['geometry'] = df_selected['geometry_wkt'].apply(wkt.loads)
df_all['geometry'] = df_all['geometry_wkt'].apply(wkt.loads)

# Create GeoDataFrames
gdf_selected = gpd.GeoDataFrame(df_selected, geometry='geometry', crs="EPSG:4326")
gdf_all = gpd.GeoDataFrame(df_all, geometry='geometry', crs="EPSG:4326")

# 2. Create Interactive Folium Map
print("Creating interactive map...")
# Center map on Innsbruck
m = folium.Map(location=[47.2692, 11.4041], zoom_start=13, tiles='CartoDB positron')

# Add non-selected buildings in gray
for _, row in gdf_all.iterrows():
    if row['potential_kwh_yr'] > 0:
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x: {'fillColor': '#cccccc', 'color': '#999999', 'weight': 0.5, 'fillOpacity': 0.3}
        ).add_to(m)

# Add selected buildings in green
for _, row in gdf_selected.iterrows():
    popup_text = f"""
    <b>Energy:</b> {row['potential_kwh_yr']/1e6:.2f} GWh/yr<br>
    <b>Area:</b> {row['roof_area_m2']:,.0f} m²<br>
    <b>Cost:</b> €{row['installation_cost_eur']:,.0f}
    """
    folium.GeoJson(
        row['geometry'],
        style_function=lambda x: {'fillColor': '#6d4aff', 'color': '#6d4aff', 'weight': 1, 'fillOpacity': 0.7},
        tooltip=popup_text
    ).add_to(m)

# Save map
m.save('output/innsbruck_solar_map.html')
print("✅ Interactive map saved to output/innsbruck_solar_map.html")

# 3. Create Chart: Top 10 Buildings by Potential
print("Creating chart...")
top_10 = gdf_selected.nlargest(10, 'potential_kwh_yr').sort_values('potential_kwh_yr')

plt.figure(figsize=(10, 6))
plt.barh(range(len(top_10)), top_10['potential_kwh_yr'] / 1e6, color='#6d4aff')
plt.yticks(range(len(top_10)), top_10['name'].fillna('Unknown Building'))
plt.xlabel('Annual Energy Potential (GWh/yr)')
plt.title('Top 10 Buildings Selected for Solar Installation')
plt.tight_layout()
plt.savefig('output/top_buildings_chart.png', dpi=150)
print("✅ Chart saved to output/top_buildings_chart.png")

print("\n" + "=" * 50)
print("VISUALIZATION COMPLETE!")
print("=" * 50)
print("\n📂 Open these files in your browser or image viewer:")
print("   - output/innsbruck_solar_map.html (open in Firefox/Chrome)")
print("   - output/top_buildings_chart.png")
