from thrust_analysis import batch_analyze
from plotting import plot_all_thrust_curves, live_thrust_stream, live_thrust_with_isp
from datetime import datetime
from plotting import detect_arduino_port
import glob
import os


# ===============================
# REPORT GENERATOR
# ===============================
def generate_report(df):

    from datetime import datetime

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("\n" + "="*50)
    print("🚀 PROPULSION TEST REPORT")
    print("="*50)
    print(f"Generated: {now}\n")

    for i, row in df.iterrows():

        print(f"--- TEST: {row['file']} ---")
        print(f"Peak Thrust:   {row['peak_thrust']:.2f} lbf")
        print(f"Burn Time:     {row['burn_time']:.3f} s")
        print(f"Impulse:       {row['impulse']:.3f} lbf·s")
        print(f"Avg Thrust:    {row['avg_thrust']:.2f} lbf")
        print(f"ISP:           {row['isp']:.2f} s")
        print(f"Uncertainty:   ±{row['peak_unc']:.2f} lbf")
        print()

    print("="*50)
    print("📊 OVERALL AVERAGES")
    print("="*50)

    avg = df.mean(numeric_only=True)

    print(f"Avg Peak Thrust: {avg['peak_thrust']:.2f} lbf")
    print(f"Avg Burn Time:   {avg['burn_time']:.3f} s")
    print(f"Avg Impulse:     {avg['impulse']:.3f} lbf·s")
    print(f"Avg ISP:         {avg['isp']:.2f} s")
    print("="*50)


# ===============================
# MAIN CONTROL PANEL
# ===============================
if __name__ == "__main__":

    print("\n=== ROCKET TEST SYSTEM ===")
    print("1 → Batch Analysis")
    print("2 → Live Thrust Only")
    print("3 → Live Thrust + ISP")
    print("4 → Motor Comparison")

    mode = input("\nSelect mode (1/2/3/4): ")

    print("\nSelect Motor:")
    print("A → Motor_A")
    print("B → Motor_B")
    print("C → Motor_C")

    motor_input = input("Enter motor (A/B/C): ").upper()

    motor_map = {
        "A": "Motor_A",
        "B": "Motor_B",
        "C": "Motor_C"
    }

motor = motor_map.get(motor_input, "Motor_A")  # default A

folder = "rocket_data"
motor = "Motor_A"

    # ===============================
    # MODE 1: BATCH ANALYSIS
    # ===============================
if mode == "1":

        summary = batch_analyze(folder, motor)

        print("LOOKING IN:", folder)
        print("FOUND FILES:", glob.glob(os.path.join(folder, "*.csv")))

        if summary is not None and not summary.empty:
            generate_report(summary)
            plot_all_thrust_curves(folder)
        else:
            print("No valid test data found.")

    # ===============================
    # MODE 2: LIVE THRUST
    # ===============================
elif mode == "2":

        print("Auto-detecting device...")
        port = detect_arduino_port()

        if port:
            print(f"Arduino found on {port} → Running REAL mode")
            live_thrust_stream(port=port, simulate=False)
        else:
            print("No Arduino found → Running SIMULATION mode")
            live_thrust_stream(simulate=True)

    # ===============================
    # MODE 3: LIVE THRUST + ISP
    # ===============================
elif mode == "3":

        print("Auto-detecting device...")
        port = detect_arduino_port()

        if port:
            print(f"Arduino found on {port} → Running REAL ISP mode")
            live_thrust_with_isp(port=port, simulate=False)
        else:
            print("No Arduino found → Running ISP SIMULATION")
            live_thrust_with_isp(simulate=True)

elif mode == "4":

        from thrust_analysis import compare_motors
        from plotting import plot_motor_comparison

        leaderboard = compare_motors(folder)

        print("\n=== MOTOR LEADERBOARD ===")
        print(leaderboard)

        plot_motor_comparison(folder)

else:
    print("Invalid selection")
