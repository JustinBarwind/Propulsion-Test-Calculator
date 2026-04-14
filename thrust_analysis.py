import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid
import glob

# LOAD DATA
# CSV format:
# time_ms, raw, filtered_lbf

def load_file(file):
    df = pd.read_csv(file)
    df.columns = ["time_ms", "raw", "thrust_lbf"]
    
    # convert time to seconds
    df["time_s"] = df["time_ms"] / 1000.0
    
    return df

# ANALYSIS FUNCTION
def analyze_thrust(df, noise_threshold=0.5):
    
    time = df["time_s"].values
    thrust = df["thrust_lbf"].values

    # Remove baseline noise
    baseline = np.mean(thrust[:100])  # first 100 samples
    thrust_clean = thrust - baseline

    # Only keep meaningful thrust (> threshold)
    active_mask = np.abs(thrust_clean) > noise_threshold

    time_active = time[active_mask]
    thrust_active = thrust_clean[active_mask]

     # SAFETY CHECK
    if len(thrust_active) == 0:
        print("No thrust detected above threshold.")
        return None

    # METRICS
    peak_thrust = np.max(thrust_active)
    
    burn_start = np.where(active_mask)[0][0]
    burn_end = np.where(active_mask)[0][-1]

    burn_time = time[burn_end] - time[burn_start]

    impulse = trapezoid(thrust_clean, time)

    avg_thrust = impulse / burn_time if burn_time > 0 else 0

    # OUTPUT
    print("\n===== ROCKET THRUST ANALYSIS =====")
    print(f"Peak Thrust: {peak_thrust:.2f} lbf")
    print(f"Burn Time:   {burn_time:.3f} s")
    print(f"Impulse:     {impulse:.2f} lbf·s")
    print(f"Avg Thrust:  {avg_thrust:.2f} lbf")

    # PLOT
    plt.figure(figsize=(10,5))
    plt.plot(time - time[0], thrust_clean, label="Thrust (baseline corrected)")
    plt.axhline(0, color='black', linestyle='--', linewidth=1)

    plt.xlabel("Time (s)")
    plt.ylabel("Thrust (lbf)")
    plt.title("Rocket Motor Thrust Curve")
    plt.legend()
    plt.grid()

    plt.show()

    return {
        "peak_thrust": peak_thrust,
        "burn_time": burn_time,
        "impulse": impulse,
        "avg_thrust": avg_thrust
    }

# MULTIPLE TEST ANALYSIS
def batch_analyze(folder_path):
    files = glob.glob(folder_path + "/*.csv")

    results = []

    for f in files:
        print(f"\nFILE: {f}")

        df = load_file(f)

        print(f"Samples: {len(df)}")

        res = analyze_thrust(df)

        if res is None:
            continue
        
        res["file"] = f
        results.append(res)

    summary = pd.DataFrame(results)

    print("\n===== SUMMARY ACROSS TESTS =====")
    print(summary)

    print("\n===== AVERAGES =====")
    print(summary.mean(numeric_only=True))

    return summary

# RUN EXAMPLE
if __name__ == "__main__":
    # Single file:
    # df = load_file("test1.csv")
    # analyze_thrust(df)

    # Batch mode (recommended for your 5x3 motor tests):
    batch_analyze("./rocket_data")
    generate_nasa_report(summary)
