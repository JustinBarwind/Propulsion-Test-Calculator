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
    return df


# ===============================
# IGNITION DETECTION
# ===============================
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

    time = df["time_s"].values
    thrust = df["thrust_lbf"].values

    baseline = np.median(thrust[:100])
    thrust_clean = thrust - baseline

    start, end = detect_burn_window(time, thrust_clean)

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

    files = glob.glob(folder_path + "/*.csv")
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

        df = pd.DataFrame(results)

    if df.empty:
        print("No valid test data.")
        return df
