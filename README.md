# 🎯 IMU Visualizer

A real-time visualization and analysis tool for Inertial Measurement Unit (IMU) data with sensor fusion capabilities.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

This application provides real-time visualization of IMU sensor data (accelerometer and gyroscope) and implements a complementary filter for orientation estimation. It supports both recorded data playback and live sensor streaming.

### Features

- ✨ Real-time plotting of 6-axis IMU data
- 🔄 Complementary filter for sensor fusion
- 📊 Multiple visualization tabs for different data perspectives
- 💾 CSV data recording functionality
- ⏸️ Pause/resume capability
- 🔌 Support for both file playback and device streams

## 🎬 Demo

![IMU Visualizer Demo](screenshots/demo.gif)
*Real-time visualization of accelerometer and gyroscope data*

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/imu-visualizer.git
cd imu-visualizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

#### Playback from file:
```bash
python src/imu.py data/imudata.txt
```

#### Live from device:
```bash
python src/imu.py /dev/ttyUSB0
```

## 📊 Data Format

Input data should be CSV formatted with 7 columns:
```
timestamp, ax, ay, az, gx, gy, gz
```

Where:
- `timestamp`: Time in seconds
- `ax, ay, az`: Accelerometer readings (m/s²)
- `gx, gy, gz`: Gyroscope readings (rad/s)

Example:
```
0.508000,-2.031250,-0.113281,9.613281,0.001953,-0.001953,0.005859
0.516000,-1.992188,-0.113281,9.652344,-0.001953,-0.005859,-0.003906
```

## 🏗️ Project Structure

```
imu-visualizer/
├── src/
│   ├── imu.py              # Main application
│   └── DataPlot.py         # Plotting module
├── data/
│   └── imudata.txt         # Sample IMU data
├── docs/
│   └── algorithms.md       # Algorithm documentation
├── screenshots/
│   └── demo.gif            # Demo screenshots
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT License
└── README.md              # This file
```

## 🧮 Algorithms

### Accelerometer-based Orientation
Calculates roll and pitch angles from gravity vector:
```python
alpha = atan2(az, ay)  # Roll
beta = asin(ax / g)    # Pitch
```

### Gyroscope Integration
Integrates angular velocity to estimate orientation:
```python
alpha(t) = alpha(t-1) + gx * dt
beta(t) = beta(t-1) + gy * dt
```

### Complementary Filter
Fuses accelerometer and gyroscope data:
```python
angle = (1 - k) * (angle_prev + gyro * dt) + k * accel_angle
```
where `k` is the filter coefficient (default: 0.05)

For detailed algorithm documentation, see [docs/algorithms.md](docs/algorithms.md).

## 🎨 Visualization Tabs

1. **Accel**: Raw accelerometer data (ax, ay, az)
2. **Gyro**: Raw gyroscope data (p, q, r) in degrees/second
3. **Accel Result**: Orientation from accelerometer
4. **Gyro Result**: Orientation from gyroscope integration
5. **Compl Result**: Fused orientation from complementary filter

## ⚙️ Configuration

You can customize the complementary filter coefficient when creating the GUI:

```python
gui = IMUGui(reader, complK=0.05)  # Default value
```

- Lower values (e.g., 0.02): More weight to gyroscope, smoother but may drift
- Higher values (e.g., 0.1): More weight to accelerometer, less drift but noisier

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [DearPyGUI](https://github.com/hoffstadt/DearPyGui)
- Complementary filter algorithm based on standard sensor fusion techniques



## 🗺️ Roadmap

- [ ] Add Kalman filter option
- [ ] Support for magnetometer data (9-DOF IMU)
- [ ] Export visualization to video
- [ ] GUI controls for filter parameters
- [ ] Quaternion-based orientation tracking
- [ ] 3D visualization of orientation

---

Made with ❤️ for robotics and sensor fusion enthusiasts
