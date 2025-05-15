import pandas as pd
import numpy as np
from datetime import datetime
import os

# Define areas
areas = [
    "Wakad", "Aundh", "Baner", "Hinjewadi", "Kharadi", 
    "Viman Nagar", "Koregaon Park", "Magarpatta", "Hadapsar", 
    "Akurdi", "Pimpri", "Chinchwad", "Ambegaon Budruk"
]

# Generate data for years 2020 to 2023
years = list(range(2020, 2024))

# Create empty lists for data
data = []

# Generate random data with some trends
for area in areas:
    base_price = np.random.randint(5000, 10000)  # Base price per sqft in 2020
    base_demand = np.random.randint(70, 95)  # Base demand score in 2020
    
    for year in years:
        # Price increases each year (with some randomness)
        year_factor = (year - 2020) * 0.08  # 8% average yearly growth
        price_growth = base_price * (1 + year_factor + np.random.uniform(-0.02, 0.04))
        price_per_sqft = round(price_growth, 2)
        
        # Demand changes each year (with some randomness)
        if area in ["Wakad", "Baner", "Hinjewadi"]:  # High growth areas
            demand_growth = base_demand * (1 + 0.05 * (year - 2020) + np.random.uniform(-0.02, 0.04))
        elif area in ["Akurdi", "Ambegaon Budruk"]:  # Emerging areas with faster growth
            demand_growth = base_demand * (1 + 0.07 * (year - 2020) + np.random.uniform(-0.02, 0.04))
        else:  # Stable areas
            demand_growth = base_demand * (1 + 0.03 * (year - 2020) + np.random.uniform(-0.03, 0.03))
        
        demand_score = min(round(demand_growth), 100)  # Cap at 100
        
        # Average property size
        avg_size = round(np.random.uniform(800, 1500), 0)
        
        # Add to data
        data.append({
            'Year': year,
            'Area': area,
            'Price_Per_SqFt': price_per_sqft,
            'Demand_Score': demand_score,
            'Avg_Property_Size_SqFt': avg_size,
            'Units_Sold': round(demand_score * 10 * np.random.uniform(0.8, 1.2)),
            'New_Constructions': round(demand_score * 2 * np.random.uniform(0.7, 1.3))
        })

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
excel_path = 'real_estate_data.xlsx'
df.to_excel(excel_path, index=False)

print(f"Sample data saved to {excel_path}")
