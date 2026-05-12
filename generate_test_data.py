import numpy as np
import pandas as pd

# ===============================
# GENERATE SYNTHETIC ROCKET DATA
# ===============================

# Time array (0 to 2 seconds)
time_s = np.linspace(0, 2, 400)

# Simulated thrust curve
thrust = []

for t in time_s:

    # Before ignition
    if t < 0.2:
        f = 0

    # Ramp up
    elif t < 0.4:
        f = (t - 0.2) * 200

    # Peak and decay
    elif t < 1.2:
        f = 40 * np.exp(-(t - 0.4) * 2)

    # Burnout
    else:
        f = 0

    thrust.append(f)

# Add sensor noise
noise = np.random.normal(0, 0.5, len(thrust))
thrust = np.array(thrust) + noise

# Convert time to milliseconds
time_ms = (time_s * 1000).astype(int)

# Fake raw column
raw = np.zeros(len(time_ms))

# Create dataframe
df = pd.DataFrame({
    "time_ms": time_ms,
    "raw": raw,
    "thrust_lbf": thrust
})

# Save CSV
output_path = "./rocket_data/test1.csv"

df.to_csv(output_path, index=False)

print(f"Test data saved to: {output_path}")
