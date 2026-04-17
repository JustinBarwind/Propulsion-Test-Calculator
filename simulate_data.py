import numpy as np
import pandas as pd
import os


def generate_fake_test(filename, peak=10, burn_time=1.5, noise_level=0.2):

    t = np.linspace(0, 1.7, 600)
    t_ms = t * 1000

    center = burn_time / 2
    sigma = burn_time / 5

   # Gaussian thrust curve
    thrust = peak * np.exp(-((t - burn_time/2)/(burn_time/5))**2)

    # Add noise
    noise = np.random.normal(0, noise_level, len(t))
    thrust_noisy = thrust + noise + 0.5

    # Apply cutoff AFTER noise
    cutoff = burn_time
    thrust_noisy = np.where(t <= cutoff, thrust_noisy, 0)

    for i, time in enumerate(t):
        if time < center:
            thrust[i] = peak * np.exp(-((time - center)/sigma)**2)
        else:
            thrust[i] = peak * np.exp(-((time - center)/sigma)**2)

    noise = np.random.normal(0, noise_level, len(t))
    thrust_noisy = thrust + noise

    baseline = 0.1
    thrust_noisy = thrust_noisy + baseline

    thrust_noisy = np.clip(thrust_noisy, 0, None)
    thrust[t > burn_time] = 0

    df = pd.DataFrame({
        "time_ms": t_ms,
        "raw": thrust_noisy * 1000,
        "thrust_lbf": thrust_noisy,
        "true_burn_time": burn_time
    })

    df.to_csv(filename, index=False)
    print(f"Saved: {filename}")


if __name__ == "__main__":

    os.makedirs("rocket_data", exist_ok=True)

    for i in range(5):
        generate_fake_test(f"rocket_data/test_A_{i+1}.csv", peak=10)

    for i in range(5):
        generate_fake_test(f"rocket_data/test_B_{i+1}.csv", peak=15)

    for i in range(5):
        generate_fake_test(f"rocket_data/test_C_{i+1}.csv", peak=8)

def load_fake_stream(filename):
    df = pd.read_csv(filename)

    for i in range(len(df)):
        yield df["time_ms"][i], df["thrust_lbf"][i]
        
