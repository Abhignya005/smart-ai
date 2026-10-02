import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate 24 hours of data at 1-minute intervals
start_time = datetime(2026, 9, 27, 0, 0, 0)
timestamps = [start_time + timedelta(minutes=i) for i in range(1440)]

# Base power follows a daily curve (low at night, high in evening)
time_hours = np.array([t.hour + t.minute/60 for t in timestamps])
base_power = 1.0 + 2.0 * np.sin(np.pi * (time_hours - 6) / 12)
base_power = np.clip(base_power, 0.5, 5.0)

# Add some noise
power = base_power + np.random.normal(0, 0.2, 1440)

# Add an artificial anomaly spike at 14:00 (row 840)
power[840:855] = 8.5 

# Sub-meterings (Kitchen, Laundry, AC)
sub1 = np.where((time_hours > 7) & (time_hours < 8), 10, 0) + np.where((time_hours > 18) & (time_hours < 19), 15, 0) # Kitchen usage
sub2 = np.where((time_hours > 10) & (time_hours < 11), 20, 0) # Laundry
sub3 = np.where(power > 2.0, power * 5, 0) # AC correlates with higher load

df = pd.DataFrame({
    'Date': [t.strftime('%d/%m/%Y') for t in timestamps],
    'Time': [t.strftime('%H:%M:%S') for t in timestamps],
    'Global_active_power': np.round(power, 3),
    'Global_reactive_power': np.round(np.random.uniform(0, 0.5, 1440), 3),
    'Voltage': np.round(np.random.normal(240, 2, 1440), 2),
    'Global_intensity': np.round(power * 4.2, 2), # Approx I = P/V
    'Sub_metering_1': np.round(sub1),
    'Sub_metering_2': np.round(sub2),
    'Sub_metering_3': np.round(sub3)
})

df.to_csv('dummy_electricity_data.csv', sep=';', index=False)
print("Created dummy_electricity_data.csv successfully!")

