import numpy as np
import pandas as pd
import os

def generate_fake_test(filename, peak=10, burn_time=1.5, noise_level=0.2):

    # Create time array (milliseconds)
    t = np.linspace(0, 3, 600)  # 3 seconds, 600 samples
    t_ms = t * 1000

    # Gaussian thrust curve (realistic shape)
    thrust = peak * np.exp(-((t - burn_time/2)/(burn_time/5))**2)

    # Add noise
    noise = np.random.normal(0, noise_level, len(t))
    thrust_noisy = thrust + noise

    # Add baseline offset (simulates sensor bias)
    baseline = 0.5
    thrust_noisy += baseline

    # Fake "raw" signal (just scaled version)
    raw = thrust_noisy * 1000

    df = pd.DataFrame({
        "time_ms": t_ms,
        "raw": raw,
        "thrust_lbf": thrust_noisy
    })

    df.to_csv(filename, index=False)
    print(f"Saved: {filename}")


# ===============================
# GENERATE MULTIPLE TESTS
# ===============================
if __name__ == "__main__":

    os.makedirs("rocket_data", exist_ok=True)

    for i in range(5):
        generate_fake_test(f"rocket_data/test_A_{i+1}.csv", peak=10)

    for i in range(5):
        generate_fake_test(f"rocket_data/test_B_{i+1}.csv", peak=15)

    for i in range(5):
        generate_fake_test(f"rocket_data/test_C_{i+1}.csv", peak=8)

