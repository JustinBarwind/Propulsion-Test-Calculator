import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid
import glob
from datetime import datetime
from motor_config import motors


# =========================================================
# LOAD DATA
# =========================================================
def load_file(file):
    df = pd.read_csv(file)
    df.columns = ["time_ms", "raw", "thrust_lbf"]
    df["time_s"] = df["time_ms"] / 1000.0
    return df


# =========================================================
# IGNITION / BURN DETECTION (AUTO)
# =========================================================
def detect_burn_window(time, thrust_clean):

    smooth = pd.Series(thrust_clean).rolling(5, center=True).mean().fillna(0).values

    baseline = np.median(smooth[:100])
    signal = np.abs(smooth - baseline)

    threshold = np.std(signal[:100]) * 3

    active = signal > threshold

    if not np.any(active):
        return None, None

    start = np.argmax(active)
    end = len(active) - np.argmax(active[::-1]) - 1

    return start, end


# =========================================================
# UNCERTAINTY MODEL
# =========================================================
def compute_uncertainty(thrust_clean, time):

    noise_region = thrust_clean[:100]
    noise_std = np.std(noise_region)

    impulse_uncertainty = noise_std * (time[-1] - time[0])
    peak_uncertainty = noise_std

    return peak_uncertainty, impulse_uncertainty


# =========================================================
# CORE ANALYSIS
# =========================================================
def analyze_thrust(df):

    time = df["time_s"].values
    thrust = df["thrust_lbf"].values

    baseline = np.median(thrust[:100])
    thrust_clean = thrust - baseline

    start, end = detect_burn_window(time, thrust_clean)

    if start is None:
        print("No ignition detected.")
        return None

    time_active = time[start:end]
    thrust_active = thrust_clean[start:end]

    # METRICS
    peak_thrust = np.max(thrust_active)

    burn_time = time[end] - time[start]

    impulse = trapezoid(thrust_clean, time)

    avg_thrust = impulse / burn_time if burn_time > 0 else 0

    peak_unc, impulse_unc = compute_uncertainty(thrust_clean, time)

    # OUTPUT
    print("\n===== ROCKET THRUST ANALYSIS =====")
    print(f"Peak Thrust: {peak_thrust:.2f} ± {peak_unc:.2f} lbf")
    print(f"Burn Time:   {burn_time:.3f} s")
    print(f"Impulse:     {impulse:.2f} ± {impulse_unc:.2f} lbf·s")
    print(f"Avg Thrust:  {avg_thrust:.2f} lbf")

    # PLOT
    plt.figure(figsize=(10,5))
    plt.plot(time - time[0], thrust_clean, label="Thrust (baseline corrected)")
    plt.axhline(0, color='black', linestyle='--')
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


# =========================================================
# BATCH ANALYSIS
# =========================================================
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

summary["isp"] = summary["impulse"].apply(
    lambda x: calculate_isp(x, prop_mass_lb)
)

summary = pd.DataFrame(results)


# =========================================================
# OVERLAY PLOT (ALL TESTS)
# =========================================================
def plot_all_thrust_curves(folder_path):

    files = glob.glob(folder_path + "/*.csv")

    plt.figure(figsize=(10,6))

    for f in files:
        df = load_file(f)

        time = df["time_s"].values
        thrust = df["thrust_lbf"].values

        baseline = np.median(thrust[:100])
        thrust_clean = thrust - baseline

        plt.plot(time - time[0], thrust_clean, alpha=0.7, label=f.split("/")[-1])

    plt.axhline(0, color='black', linestyle='--')
    plt.title("Thrust Curve Comparison (All Tests)")
    plt.xlabel("Time (s)")
    plt.ylabel("Thrust (lbf)")
    plt.grid()
    plt.show()


# =========================================================
# NASA-STYLE REPORT GENERATOR
# =========================================================
def generate_nasa_report(summary_df, output_file="thrust_report.txt"):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, "w") as f:

        f.write("=========================================\n")
        f.write("        ROCKET THRUST TEST REPORT        \n")
        f.write("=========================================\n\n")

        f.write(f"Generated: {now}\n\n")

        f.write("=== OVERALL RESULTS ===\n\n")
        f.write(summary_df.to_string(index=False))
        f.write("\n\n")

        f.write("=== STATISTICS ===\n\n")
        f.write(f"Avg Peak Thrust: {summary_df['peak_thrust'].mean():.2f} lbf\n")
        f.write(f"Std Peak Thrust: {summary_df['peak_thrust'].std():.2f} lbf\n\n")

        f.write(f"Avg Impulse: {summary_df['impulse'].mean():.2f} lbf·s\n")
        f.write(f"Std Impulse: {summary_df['impulse'].std():.2f} lbf·s\n\n")

        f.write(f"Avg Burn Time: {summary_df['burn_time'].mean():.3f} s\n")
        f.write(f"Std Burn Time: {summary_df['burn_time'].std():.3f} s\n\n")

        f.write("=== ENGINEERING NOTES ===\n\n")
        f.write("- Load cell thrust measurement system\n")
        f.write("- Baseline corrected signal\n")
        f.write("- Automatic ignition detection\n")
        f.write("- Numerical integration (trapezoidal rule)\n")

    print(f"\nReport saved: {output_file}")


# =========================================================
# MAIN EXECUTION
# =========================================================
if __name__ == "__main__":

    folder = "./rocket_data"

    summary = batch_analyze(folder)

    if summary is not None and not summary.empty:

        generate_nasa_report(summary)

        plot_all_thrust_curves(folder)

import serial
import time
import matplotlib.pyplot as plt

def live_thrust_stream(port="COM3", baud=115200):

    ser = serial.Serial(port, baud)

    times = []
    thrusts = []

    plt.ion()
    fig, ax = plt.subplots()

    line, = ax.plot([], [], label="Live Thrust")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Thrust (lbf)")
    ax.set_title("Live Rocket Thrust Stream")
    ax.grid()

    start_time = time.time()

    while True:
        try:
            data = ser.readline().decode().strip()

            if "," in data:
                t_ms, thrust = data.split(",")

                t = float(t_ms) / 1000.0
                f = float(thrust)

                times.append(t)
                thrusts.append(f)

                line.set_xdata(times)
                line.set_ydata(thrusts)

                ax.relim()
                ax.autoscale_view()

                plt.pause(0.01)

        except KeyboardInterrupt:
            print("Stopping stream...")
            break

    ser.close()
    plt.ioff()
    plt.show()

    return times, thrusts

def calculate_isp(impulse_lbf_s, propellant_mass):

    g = 32.174

    mass_lb = propellant_mass

    weight_flow = mass_lb * g

    isp = impulse_lbf_s / weight_flow

    return isp
