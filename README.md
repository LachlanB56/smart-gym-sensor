# Metric — Wearable Rep Detection & Form Analysis

An end-to-end wearable system that uses inertial sensors to automatically detect gym repetitions and analyse exercise form. Raw motion data is captured from a body-worn IMU, streamed to a host machine, processed into per-rep biomechanical metrics (range of motion, tempo), and classified using machine learning.

Built solo from the firmware up: embedded C on an STM32 microcontroller, a custom serial data-acquisition pipeline, signal-processing in Python, and two scikit-learn models — one for form quality, one for distinguishing exercise from background noise.

> **Status:** Working research prototype. Validated on bicep curls; the pipeline generalises to other single-joint movements.

---

## Why this project

Wearable form-analysis products (smart compression garments, EMG sleeves) have historically struggled not on the sensing side but on turning noisy real-world motion into reliable, meaningful feedback. This project tackles that core problem on a single representative exercise — taking raw accelerometer/gyroscope data and producing trustworthy rep counts and movement metrics — as the foundation for a larger smart-apparel concept.

---

## System Overview

```
   ┌─────────────┐   I²C    ┌──────────────┐   USB serial   ┌────────────────┐
   │  MPU-6050   │ ───────► │  STM32 (F411)│ ─────────────► │  Python host   │
   │  6-axis IMU │          │  firmware    │  100 Hz stream │  acquisition   │
   └─────────────┘          └──────────────┘                └────────┬───────┘
                                                                      │
                          ┌───────────────────────────────────────────┘
                          ▼
        ┌──────────────────────────┐     ┌───────────────────────────┐
        │  Signal processing       │     │  Machine learning          │
        │  • orientation / angle   │ ──► │  • form quality (good/bad) │
        │  • rep detection (peaks) │     │  • exercise vs. noise      │
        │  • ROM & tempo per rep   │     │    (segmentation)          │
        └──────────────────────────┘     └───────────────────────────┘
```

---

## Pipeline

**1. Embedded firmware (C / STM32 / Arduino framework)**
Reads the MPU-6050 over I²C and streams timestamped 6-axis IMU samples (`time, ax, ay, az, gx, gy, gz`) over USB serial at a fixed 100 Hz, using a non-blocking `millis()`-based scheduler to hold a stable sample rate.

**2. Data acquisition (Python)**
A serial receiver reads the live stream, parses each sample, logs every reading to CSV, and renders a throttled real-time plot for capture verification.

**3. Signal processing (NumPy / pandas / SciPy)**
- Derives a drift-free tilt angle from the accelerometer via `arctan2` on the gravity vector (no gyro integration / no drift).
- Detects individual reps as peaks in the smoothed angle signal, with adaptive spacing constraints to reject double-counting.
- Computes per-rep **range of motion** (angle swept between valley and peak) and **tempo** (time between reps).
- Uses **autocorrelation** to estimate the underlying rep period directly from the signal, and explored bandpass / activity-based segmentation for noise rejection.

**4. Machine learning (scikit-learn)**
- **Form-quality model** — a classifier trained on per-rep features (ROM, tempo) to rate reps along independent quality dimensions.
- **Segmentation model** — a windowed classifier trained on raw-signal shape features (variance, oscillation strength, rotational energy) to distinguish real exercise from handling/background noise, enabling automatic isolation of the active workout.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Hardware | STM32 Nucleo-F411RE, InvenSense MPU-6050 (6-axis IMU) |
| Firmware | C, Arduino framework, PlatformIO, I²C |
| Processing | Python, NumPy, pandas, SciPy |
| Machine learning | scikit-learn (Random Forest classification) |
| Tooling | Jupyter, Matplotlib |

---

## Repository Structure

```
├── src/main.cpp            # STM32 firmware: IMU read + serial stream
├── platformio.ini          # Firmware build config
├── Receiver.py             # Serial acquisition → CSV + live plot
├── RepAnalysis.ipynb       # Signal processing: angle, rep detection, ROM, tempo
├── Appender.py             # Combines session CSVs into training datasets
├── RepRatingML.ipynb       # Form-quality model
└── CurlDetectionML.ipynb   # Exercise-vs-noise segmentation model
```

---

## Key Results

- Clean, drift-free per-rep **ROM** measurement validated against recorded movement (≈80–95° on full-range curls, with measured rep-to-rep variation).
- Reliable **rep detection** and **tempo** extraction from raw IMU data via peak detection on a derived angle signal.
- **Segmentation model** distinguishing curls from background noise at ~85% accuracy on held-out windows — a working basis for automatic workout isolation.

---

## What I Learned

This project spans three normally-separate disciplines — embedded systems, digital signal processing, and machine learning — and the most valuable lessons were at their seams:

- **The sensors are the easy part; the data is the hard part.** Reliable feature extraction and a clean, well-labelled dataset matter far more than model choice.
- **Compute what you can; learn what you can't.** Rep count, ROM, and tempo are deterministic (peak detection, geometry) — ML is reserved for genuine judgments like form quality and noise rejection, with the deterministic metrics feeding the models as features.
- **Validate visually at every step.** Plotting intermediate signals (and overlaying detected peaks) was the single most effective debugging tool across the whole pipeline.

---

## Future Work

- Sensor fusion (complementary filter) for higher-accuracy angles during fast motion.
- Multi-sensor capture for bilateral / symmetry analysis.
- Expanded, varied dataset to make the segmentation and form models robust across users and exercises.
- On-device inference for an untethered, garment-integrated wearable.

---

*Designed and built independently — from microcontroller firmware through to machine-learning models.*
