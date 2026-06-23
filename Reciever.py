import serial
import csv
import time
from collections import deque
import matplotlib.pyplot as plt

# ---- CONFIG ----
PORT = "COM3"          # <-- change to YOUR port
BAUD = 115200
PLOT_WINDOW = 500      # how many recent samples to show on screen
CSV_NAME = f"imu_noise6.csv"   # unique filename each run
# ----------------

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)          # let the connection settle / board reset
ser.reset_input_buffer()

# rolling buffers for plotting
t   = deque(maxlen=PLOT_WINDOW)
ax_, ay_, az_ = deque(maxlen=PLOT_WINDOW), deque(maxlen=PLOT_WINDOW), deque(maxlen=PLOT_WINDOW)
gx_, gy_, gz_ = deque(maxlen=PLOT_WINDOW), deque(maxlen=PLOT_WINDOW), deque(maxlen=PLOT_WINDOW)

plt.ion()
fig, (ax_accel, ax_gyro) = plt.subplots(2, 1, figsize=(10, 6))
fig.tight_layout(pad=3)

csvfile = open(CSV_NAME, "w", newline="")
writer = csv.writer(csvfile)
writer.writerow(["time_ms", "ax", "ay", "az", "gx", "gy", "gz"])

print(f"Logging to {CSV_NAME}. Close the plot window or Ctrl+C to stop.")

last_draw = time.time()

try:
    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 7:
            continue                      # skip incomplete/garbage lines

        try:
            vals = [float(p) for p in parts]
        except ValueError:
            continue                      # skip a header or junk line

        writer.writerow(vals)             # log raw to CSV

        ts, ax, ay, az, gx, gy, gz = vals
        t.append(ts); ax_.append(ax); ay_.append(ay); az_.append(az)
        gx_.append(gx); gy_.append(gy); gz_.append(gz)

        # redraw ~20x/sec, not every sample (plotting is slow)
        if time.time() - last_draw > 0.05:
            ax_accel.clear(); ax_gyro.clear()
            ax_accel.plot(t, ax_, label="ax"); ax_accel.plot(t, ay_, label="ay"); ax_accel.plot(t, az_, label="az")
            ax_gyro.plot(t, gx_, label="gx"); ax_gyro.plot(t, gy_, label="gy"); ax_gyro.plot(t, gz_, label="gz")
            ax_accel.set_ylabel("accel (m/s²)"); ax_accel.legend(loc="upper left"); ax_accel.grid(True)
            ax_gyro.set_ylabel("gyro (rad/s)");  ax_gyro.legend(loc="upper left"); ax_gyro.grid(True)
            plt.pause(0.001)
            last_draw = time.time()

except KeyboardInterrupt:
    print("\nStopping.")
finally:
    csvfile.close()
    ser.close()
    print(f"Saved {CSV_NAME}")