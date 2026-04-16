import matplotlib.pyplot as plt
import glob
from thrust.analysis import load_file
import serial
import time
from motor_config import motors


# ===============================
# OVERLAY PLOTS
# ===============================
def plot_all_thrust_curves(folder_path):

    files = glob.glob(folder_path + "/*.csv")

    plt.figure(figsize=(10,6))

    for f in files:
        df = load_file(f)

        t = df["time_s"].values
        thrust = df["thrust_lbf"].values

        baseline = thrust[:100].mean()
        thrust_clean = thrust - baseline

        plt.plot(t - t[0], thrust_clean, label=f.split("/")[-1])

    plt.axhline(0, color='black', linestyle='--')
    plt.xlabel("Time (s)")
    plt.ylabel("Thrust (lbf)")
    plt.title("Thrust Comparison")
    plt.legend()
    plt.grid()
    plt.show()


# ===============================
# BASIC LIVE STREAM (NO ISP)
# ===============================
def live_thrust_stream(port="COM3", baud=115200):

    ser = serial.Serial(port, baud)

    times, thrusts = [], []

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], label="Thrust")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Thrust (lbf)")
    ax.set_title("Live Thrust")
    ax.grid()

    while True:
        try:
            data = ser.readline().decode().strip()

            if "," in data:
                t, f = data.split(",")

                times.append(float(t)/1000)
                thrusts.append(float(f))

                line.set_xdata(times)
                line.set_ydata(thrusts)

                ax.relim()
                ax.autoscale_view()

                plt.pause(0.01)

        except KeyboardInterrupt:
            print("\nStopping stream...")
            break

    ser.close()
    plt.ioff()
    plt.show()

    return times, thrusts


# ===============================
# LIVE STREAM WITH REAL-TIME ISP
# ===============================
def live_thrust_with_isp(port="COM3", baud=115200, motor_key="Motor_A"):

    ser = serial.Serial(port, baud)

    prop_mass = motors[motor_key]["propellant_mass_lb"]

    times = []
    thrusts = []
    impulses = []
    isps = []

    impulse = 0
    last_time = None

    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8,8))

    thrust_line, = ax1.plot([], [], label="Thrust (lbf)")
    isp_line, = ax2.plot([], [], label="ISP (s)", color='orange')

    ax1.set_title("Live Thrust")
    ax1.set_ylabel("lbf")
    ax1.grid()

    ax2.set_title("Live ISP")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Seconds")
    ax2.grid()

    while True:
        try:
            data = ser.readline().decode().strip()

            if "," in data:
                try:
                    t_ms, thrust = data.split(",")
                    t = float(t_ms) / 1000.0
                    f = float(thrust)
                except:
                    continue
                times.append(t)
                thrusts.append(f)

                # =========================
                # BETTER INTEGRATION (TRAPEZOID)
                # =========================
                if last_time is not None and len(thrusts) > 1:
                    dt = t - last_time
                    f_prev = thrusts[-2]
                    impulse += 0.5 * (f + f_prev) * dt

                last_time = t
                impulses.append(impulse)

                # =========================
                # ISP (WITH NOISE FILTER)
                # =========================
                if prop_mass > 0:
                    if f < 0.2:   # threshold (lbf)
                        isp = 0
                    else:
                        isp = impulse / prop_mass
                else:
                    isp = 0

                isps.append(isp)

                # =========================
                # UPDATE PLOTS
                # =========================
                thrust_line.set_xdata(times)
                thrust_line.set_ydata(thrusts)

                isp_line.set_xdata(times)
                isp_line.set_ydata(isps)

                ax1.relim()
                ax1.autoscale_view()

                ax2.relim()
                ax2.autoscale_view()

                plt.pause(0.01)

        except KeyboardInterrupt:
            print("\nStopping stream...")
            break

    ser.close()
    plt.ioff()
    plt.show()

    print(f"\nFinal Impulse: {impulse:.2f} lbf·s")
    print(f"Final ISP: {isp:.2f} s")

    return times, thrusts, impulses, isps
