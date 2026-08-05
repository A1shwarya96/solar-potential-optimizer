# Solar Potential Optimizer for Innsbruck

> Spatial optimization model identifying optimal rooftops for solar PV installation in Innsbruck, Austria.

## Overview

This project implements a **Mixed-Integer Linear Programming (MILP)** model to solve the rooftop solar siting problem: *given a target energy demand, which rooftops should be equipped with solar panels to minimize total installation cost?*

The model evaluates 19,377 building footprints across Innsbruck, calculates solar energy potential using real irradiance data, and selects the most cost-effective subset to meet a defined energy target.

## Methodology

### Data Sources
- **Building footprints**: OpenStreetMap via `osmnx`
- **Solar irradiance**: PVGIS API (European Commission Joint Research Centre)
- **Target region**: Innsbruck, Austria (47.2692°N, 11.4041°E)

### Optimization Formulation

**Decision variables**: Binary selection of rooftop candidates (x_i in {0,1})

**Objective**: Minimize total installation cost
min sum(FixedCost + VariableCost * Area_i) * x_i

**Constraint**: Total energy generation must meet target demand
sum(Potential_i * x_i) >= TargetDemand

### Key Parameters
| Parameter | Value |
|-----------|-------|
| Panel efficiency | 20% |
| Performance ratio (system losses) | 80% |
| Fixed cost per project | €50,000 |
| Variable cost per m² | €150 |
| Target demand | 197 GWh/yr (10% of total potential) |

## Results

| Metric | Value |
|--------|-------|
| Total buildings evaluated | 19,377 |
| Buildings selected | 79 |
| Total rooftop area used | 1,119,318 m² |
| Total energy generated | 197.0 GWh/yr |
| Total installation cost | €171.8M |
| Cost per kWh installed | €0.87 |

### Top 5 Buildings by Energy Potential
1. DEZ (Einkaufszentrum) — 9.67 GWh/yr
2. Tivoli Stadion Tirol — 6.06 GWh/yr
3. Sillpark Shopping Center — 5.42 GWh/yr
4. IKEA — 5.29 GWh/yr

## Key Outputs
- `output/innsbruck_solar_map.html` — Interactive map showing selected (purple) vs. non-selected (gray) rooftops
- `output/top_buildings_chart.png` — Bar chart of top 10 buildings by energy potential
- `data/processed/buildings_with_solar.csv` — Full dataset with energy calculations
- `data/processed/selected_buildings.csv` — Optimized subset of selected buildings

## Installation
