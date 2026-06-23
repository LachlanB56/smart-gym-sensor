


import glob
import pandas as pd
import numpy as np

files = glob.glob("features_curls_test*.csv")   # the * matches 1,2,3...10 and any others
print(files)                                      # see what it found

master = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
master.to_csv("master_dataset.csv", index=False)


rows = []
for f in glob.glob("imu_bicep_reps*.csv"):
    df = pd.read_csv(f)
    df["label"] = "curls"
    rows.append(df)


for f in glob.glob("imu_noise*.csv"):
    df = pd.read_csv(f)
    df["label"] = "noise"
    rows.append(df)


combined = pd.concat(rows, ignore_index=True)

WINDOW = 100          # samples per window (100 = 1 second at 100Hz)
STEP   = 50           # slide forward 50 samples each time (50% overlap)

window_rows = []
for start in range(0, len(combined) - WINDOW, STEP):
    chunk = combined.iloc[start:start + WINDOW]      # one window of samples

    # only use windows that are all one label (skip mixed-label boundaries)
    if chunk["label"].nunique() != 1:
        continue

    # compute shape-features for this window
    accmag = np.sqrt(chunk["ax"]**2 + chunk["ay"]**2 + chunk["az"]**2)
    gyromag = np.sqrt(chunk["gx"]**2 + chunk["gy"]**2 + chunk["gz"]**2)

    window_rows.append({
        "acc_std":   accmag.std(),        # how much acceleration varies (movement)
        "acc_range": accmag.max() - accmag.min(),
        "gyro_std":  gyromag.std(),        # how much rotation varies
        "gyro_mean": gyromag.mean(),
        "ay_std":    chunk["ay"].std(),    # variation in the curl axis
        "label":     chunk["label"].iloc[0],
    })

windows = pd.DataFrame(window_rows)
print(windows.shape)
print(windows["label"].value_counts())
print(windows.head())

windows.to_csv("Curl_Detection_Dataset.csv", index=False)
