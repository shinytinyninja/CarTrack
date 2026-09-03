# 🚗 DIY Dragy Performance Monitor

An open-source, low-cost alternative to commercial performance meters (like Dragy or VBOX) designed to track vehicle acceleration metrics with millisecond precision. Built for car enthusiasts, tuners, and track-day drivers who want accessible performance telemetry using a laptop, Python, and off-the-shelf GPS hardware.

---

## 📌 Features

- **High-Frequency GPS Tracking:** Supports concurrent GNSS update rates from **1Hz up to 10Hz** (10 samples per second / 100ms updates).
- **1-Foot Rollout Simulation:** Standardized 1-foot rollout buffer (`0.0003048 km`) matching official drag strip timing protocols (NHRA/IHRA).
- **Anti-Drift Staging Protection:** Implements dual-parameter staging (Distance > 1ft + Speed > 2.0 km/h) to eliminate false launches caused by stationary GPS coordinate drift.
- **Speed Milestones:** Automatically measures **0–30 mph/kmh**, **0–60 mph/kmh**, and **0–100 mph/kmh**.
- **Distance Milestones:** Records split times for **100 Yards**, **1/8th Mile**, and **1/4th Mile**.
- **Automated CSV Logging:** Appends run results, starting coordinates, ending coordinates, and all milestone split times into `drag_race_events.csv`.
- **Tkinter GUI:** Clean visual interface showing staging status, current speed, live coordinates, and metric readouts.

---

## 🛠️ Hardware Requirements

| Component | Description | Recommendation / Details |
| :--- | :--- | :--- |
| **GNSS Receiver** | Beitian BN-808 USB GNSS Module | High-sensitivity receiver with magnetic base |
| **Placement** | Vehicle Roof (External) | Uses the metallic roof as a ground plane for zero satellite blockage |
| **Baud Rate** | `38400` bps | Configured for maximum throughput without serial buffer latency |
| **Refresh Rate** | `10Hz` (10Hz NMEA) | Set in receiver settings via u-center or NMEA commands |
| **Host System** | Vehicle Laptop | Runs Python 3.x with a USB/COM connection to the GPS module |

---

## 📐 How the Staging & Rollout Works
| Phase | Status Color | Vehicle State | Condition / Trigger | System Action |
| --- | --- | --- | --- | --- |
| **1. Staged** | Orange | Stationary | Start button pressed & GPS locked | Captures initial launch coordinates |
| **2. Rollout** | Yellow | Moving | Distance moved > 1 foot **AND** Speed > 2 km/h | Filters out GPS drift & arms timer |
| **3. Timing Active** | Yellow / Green | Accelerating | Rollout completed | Clock starts ($T = 0.00\text{s}$), records split times, and logs CSV at 1/4 Mile |

1. **Staging:** When you start the timer, the app captures the staging position (`$GNGLL` NMEA sentence).
2. **Launch & Rollout:** As you accelerate, the software measures distance from the staged point. Once the car moves **1 foot** *and* exceeds **2 km/h**, the timer officially starts.
3. **Tracking:** The loop evaluates `$GNVTG` (speed) and `$GNGLL` (location) packets, capturing elapsed times for each milestone.
4. **Finish:** Crossing the 1/4-mile mark automatically stops the run and saves the telemetry to disk.

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Dependencies

Ensure Python 3.x is installed on your laptop, then install required modules:

```bash
pip install pyserial pynmea2
```

### 2. GPS Module Setup (Beitian BN-808)
1. Connect the Beitian BN-808 USB cable to your laptop.
2. Place the magnetic antenna unit on the center of your vehicle roof.
3. (Optional) Use u-blox u-center to verify the BN-808 is set to 10Hz update rate and 38400 baud rate.
4. Identify your Windows COM Port (e.g., COM3) in Device Manager and update serial_port in the Python code if necessary.

### 3. Running the Ap
```Bash
python drag_tracker.py
```

1. Click Start in the Tkinter GUI.
2. Wait until the indicator changes to "Staged (Waiting for Rollout)" (Orange).
3. Launch the vehicle! The status will change to "Recording" (Yellow) as soon as rollout completes.

### CSV Log Format
All runs automatically append to drag_race_events.csv:

### Why DIY
Commercial drag timers cost anywhere from $150 to $1,000+. By leveraging cheap open-source GNSS hardware (~$15–$25) and Python's pynmea2 library, this project provides a fully customizable platform that you can modify for custom track distances, telemetry dashboards, or live OBD-II sensor integration.