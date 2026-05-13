import serial
import pandas as pd
from datetime import datetime

def record_test(port, baud):

    ser = serial.Serial(port, baud)

    data = []

    print("Recording thrust data...")
    print("Press CTRL+C to stop.\n")

    try:

        while True:

            line = ser.readline().decode().strip()

            if "," in line:

                t, thrust = line.split(",")

                data.append([
                    float(t),
                    0,
                    float(thrust)
                ])

                print(line)

    except KeyboardInterrupt:

        print("\nRecording stopped.")

    ser.close()

    df = pd.DataFrame(
        data,
        columns=["time_ms", "raw", "thrust_lbf"]
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"./rocket_data/test_{timestamp}.csv"

    df.to_csv(filename, index=False)

    print(f"\nSaved: {filename}")

    return filename
