from analysis import batch_analyze
from plotting import plot_all_thrust_curves, live_thrust_stream, live_thrust_with_isp
from datetime import datetime


# ===============================
# REPORT GENERATOR
# ===============================
def generate_report(df):

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("\n===== NASA-STYLE REPORT =====")
    print(f"Generated: {now}\n")

    print(df)

    print("\n=== AVERAGES ===")
    print(df.mean(numeric_only=True))


# ===============================
# MAIN CONTROL PANEL
# ===============================
if __name__ == "__main__":

    print("\n=== ROCKET TEST SYSTEM ===")
    print("1 → Batch Analysis")
    print("2 → Live Thrust Only")
    print("3 → Live Thrust + ISP")

    mode = input("\nSelect mode (1/2/3): ")

    folder = "./rocket_data"
    motor = "Motor_A"   # CHANGE THIS

    # ===============================
    # MODE 1: BATCH ANALYSIS
    # ===============================
    if mode == "1":

        summary = batch_analyze(folder, motor)

        if summary is not None and not summary.empty:
            generate_report(summary)
            plot_all_thrust_curves(folder)

        else:
            print("No valid test data found.")

    # ===============================
    # MODE 2: LIVE THRUST
    # ===============================
    elif mode == "2":

        port = input("Enter COM port (e.g., COM3): ")
        live_thrust_stream(port=port)

    # ===============================
    # MODE 3: LIVE THRUST + ISP
    # ===============================
    elif mode == "3":

        port = input("Enter COM port (e.g., COM3): ")
        live_thrust_with_isp(port=port, motor_key=motor)

    else:
        print("Invalid selection.")
