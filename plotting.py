import matplotlib.pyplot as plt
import glob
from analysis import load_file
import serial
import time


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

    plt.axhline(0)
    plt.xlabel("Time (s)")
    plt.ylabel("Thrust (lbf)")
    plt.title("Thrust Comparison")
    plt.legend()
    plt.grid()
    plt.show()


# ===============================
# LIVE STREAM
# ===============================
def live_thrust_stream(port="COM3", baud=115200):

    ser = serial.Serial(port, baud)

    times, thrusts = [], []

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [])

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
            break

    ser.close()
    plt.ioff()
    plt.show()
