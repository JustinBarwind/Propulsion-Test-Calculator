from analysis import batch_analyze
from plotting import plot_all_thrust_curves
from datetime import datetime


def generate_report(df):

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("\n===== NASA-STYLE REPORT =====")
    print(f"Generated: {now}\n")

    print(df)

    print("\nAverages:")
    print(df.mean(numeric_only=True))


if __name__ == "__main__":

    folder = "./rocket_data"
    motor = "Motor_A"   # CHANGE THIS

    summary = batch_analyze(folder, motor)

    if not summary.empty:
        generate_report(summary)
        plot_all_thrust_curves(folder)
