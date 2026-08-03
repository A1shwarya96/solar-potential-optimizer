import pandas as pd
import pulp

print("=" * 50)
print("OPTIMIZATION MODEL: Rooftop Selection")
print("=" * 50)

# 1. Load the data
df = pd.read_csv('data/processed/buildings_with_solar.csv')

# Drop buildings with missing potential or area
df = df.dropna(subset=['potential_kwh_yr', 'roof_area_m2'])
df = df[df['potential_kwh_yr'] > 0]
# Keep only the top 5000 buildings to make the solver faster
df = df.sort_values('potential_kwh_yr', ascending=False).head(5000).reset_index(drop=True)
print(f"Loaded {len(df)} buildings for optimization.")

# 2. Define Parameters
# Target: Meet 10% of Innsbruck's total theoretical potential (~197 GWh)
TARGET_DEMAND_KWH = 197_000_000  

# Cost model: Fixed cost per project (€50,000) + Variable cost per m² (€150)
FIXED_COST = 50000
VARIABLE_COST_PER_M2 = 150

# Calculate cost and potential for each building
df['installation_cost_eur'] = FIXED_COST + (VARIABLE_COST_PER_M2 * df['roof_area_m2'])

print(f"Target Demand: {TARGET_DEMAND_KWH / 1e6:.1f} GWh/yr")
print("Setting up Linear Integer Program...")

# 3. Formulate the Optimization Problem
prob = pulp.LpProblem("Solar_Rooftop_Optimization", pulp.LpMinimize)

# Decision Variables: x_i = 1 if building i is selected, 0 otherwise
# We use binary variables. 'cat' stands for category.
x = {i: pulp.LpVariable(f"x_{i}", cat='Binary') for i in df.index}

# Objective Function: Minimize Total Cost
prob += pulp.lpSum([df.loc[i, 'installation_cost_eur'] * x[i] for i in df.index]), "Total_Installation_Cost"

# Constraint: Total energy generated must meet or exceed target demand
prob += pulp.lpSum([df.loc[i, 'potential_kwh_yr'] * x[i] for i in df.index]) >= TARGET_DEMAND_KWH, "Meet_Energy_Demand"

# 4. Solve the Problem
print("Solving... (this may take a few seconds)")
prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))

# 5. Output Results
print("\n" + "=" * 50)
print("OPTIMIZATION RESULTS")
print("=" * 50)
print(f"Status: {pulp.LpStatus[prob.status]}")

selected_buildings = [i for i in df.index if x[i].varValue == 1.0]
total_cost = pulp.value(prob.objective)
total_energy = df.loc[selected_buildings, 'potential_kwh_yr'].sum()
total_area = df.loc[selected_buildings, 'roof_area_m2'].sum()

print(f"Buildings Selected: {len(selected_buildings)} out of {len(df)}")
print(f"Total Rooftop Area Used: {total_area:,.2f} m²")
print(f"Total Energy Generated: {total_energy / 1e6:,.2f} GWh/yr")
print(f"Total Installation Cost: €{total_cost:,.2f}")
print(f"Cost per kWh installed: €{(total_cost / total_energy):.4f}")

# Save the selected buildings for the map
selected_df = df.loc[selected_buildings].copy()
selected_df['selected'] = 1
selected_df.to_csv('data/processed/selected_buildings.csv', index=False)
print("\n✅ Saved selected buildings to data/processed/selected_buildings.csv")

