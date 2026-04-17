import numpy as np
import pandas as pd
from scipy.integrate import trapezoid
import glob
from motor_config import motors


# ===============================
# LOAD DATA
# ===============================
def load_file(file):
    df = pd.read_csv(file)
    df.columns = ["time_ms", "raw", "thrust_lbf"]
    df["time_s"] = df["time_ms"] / 1000.0
    df = df[df["time_s"] <= 2.0]

    return df


# ===============================
# IGNITION DETECTION
# ===============================
def detect_burn_window(time, thrust_clean):

    # Smooth signal slightly
    smooth = pd.Series(thrust_clean).rolling(5, center=True).mean().fillna(0).values

    # Compute derivative (rate of change)
    deriv = np.gradient(smooth)

    # Burn START = rapid rise
    start_candidates = np.where(deriv > np.max(deriv) * 0.3)[0]

    # Burn END = where signal collapses
    end_candidates = np.where(smooth < np.max(smooth) * 0.1)[0]

    if len(start_candidates) == 0 or len(end_candidates) == 0:
        return None, None

    start = start_candidates[0]
    end = end_candidates[-1]

    if end <= start:
        return None, None

    return start, end


# ===============================
# UNCERTAINTY
# ===============================
def compute_uncertainty(thrust_clean, time):

    noise_region = thrust_clean[:100]
    noise_std = np.std(noise_region)

    return noise_std, noise_std * (time[-1] - time[0])


# ===============================
# ISP (IMPERIAL)
# ===============================
def calculate_isp(impulse_lbf_s, propellant_lbm):
    return impulse_lbf_s / propellant_lbm


# ===============================
# SINGLE TEST ANALYSIS
# ===============================
def analyze_thrust(df):

    if "true_burn_time" in df.columns:
        return {
            "peak_thrust": np.max(df["thrust_lbf"]),
            "burn_time": df["true_burn_time"].iloc[0],
            "impulse": np.trapz(df["thrust_lbf"], df["time_s"]),
            "avg_thrust": np.mean(df["thrust_lbf"]),
            "peak_unc": 0,
            "impulse_unc": 0
        }

    time = df["time_s"].values
    thrust = df["thrust_lbf"].values

    baseline = np.median(thrust[:100])
    thrust_clean = thrust - baseline
    thrust[t > burn_time] = 0

    start, end = detect_burn_window(time, thrust_clean)

    print("DEBUG start:", start)
    print("DEBUG end:", end)
    print("DEBUG time range:", time[0], "→", time[-1])

    if start is None:
        return None

    thrust_active = thrust_clean[start:end]

    peak = np.max(thrust_active)
    burn_time = time[end] - time[start]
    impulse = trapezoid(thrust_active, time[start:end])
    avg = impulse / burn_time if burn_time > 0 else 0

    peak_unc, impulse_unc = compute_uncertainty(thrust_clean, time)

    return {
        "peak_thrust": peak,
        "burn_time": burn_time,
        "impulse": impulse,
        "avg_thrust": avg,
        "peak_unc": peak_unc,
        "impulse_unc": impulse_unc
    }


# ===============================
# BATCH ANALYSIS
# ===============================
def batch_analyze(folder_path, motor_key):

    files = glob.glob(folder_path + f"/test_{motor_key[-1]}_*.csv")
    results = []

    prop_mass = motors[motor_key]["propellant_mass_lb"]

    for f in files:

        df = load_file(f)
        res = analyze_thrust(df)

        if res is None:
            continue

        res["file"] = f
        res["isp"] = calculate_isp(res["impulse"], prop_mass)

        results.append(res)

    # CREATE FINAL DATAFRAME AFTER LOOP
    summary_df = pd.DataFrame(results)

    if summary_df.empty:
        return None

    return summary_df

def compare_motors(folder_path):

    all_results = []

    for motor_key in ["Motor_A", "Motor_B", "Motor_C"]:

        files = glob.glob(folder_path + f"/test_{motor_key[-1]}_*.csv")
        prop_mass = motors[motor_key]["propellant_mass_lb"]

        results = []

        for f in files:
            df = load_file(f)
            res = analyze_thrust(df)

            if res is None:
                continue

            res["isp"] = calculate_isp(res["impulse"], prop_mass)
            results.append(res)

        if len(results) == 0:
            continue

        df_motor = pd.DataFrame(results)

        summary = {
            "motor": motor_key,
            "avg_isp": df_motor["isp"].mean(),
            "avg_peak_thrust": df_motor["peak_thrust"].mean(),
            "avg_impulse": df_motor["impulse"].mean(),
            "avg_burn_time": df_motor["burn_time"].mean()
        }

        all_results.append(summary)

    leaderboard = pd.DataFrame(all_results)

    return leaderboard.sort_values(by="avg_isp", ascending=False)
