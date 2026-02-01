# Algorithm Documentation

## Overview

This document explains the mathematical algorithms used in the IMU Visualizer for orientation estimation and sensor fusion.

## Table of Contents

1. [Accelerometer-based Orientation](#accelerometer-based-orientation)
2. [Gyroscope Integration](#gyroscope-integration)
3. [Complementary Filter](#complementary-filter)
4. [Coordinate Systems](#coordinate-systems)

## Accelerometer-based Orientation

### Principle

The accelerometer measures specific force (including gravity). When the IMU is stationary or moving at constant velocity, the accelerometer primarily measures the gravity vector.

### Mathematical Formulation

Given accelerometer readings `(ax, ay, az)` in m/s²:

**Roll angle (α):**
```
α = atan2(az, ay)
```

**Pitch angle (β):**
```
β = asin(ax / g)
```

where `g = 9.8 m/s²` is the gravitational acceleration.

### Advantages
- Absolute reference (no drift)
- Works well for slow movements

### Disadvantages
- Noisy during motion
- Affected by linear accelerations
- Cannot measure yaw (rotation around vertical axis)

## Gyroscope Integration

### Principle

The gyroscope measures angular velocity. By integrating over time, we can estimate orientation changes.

### Mathematical Formulation

Given gyroscope readings `(gx, gy, gz)` in rad/s:

**Discrete integration:**
```
α(t) = α(t-1) + gx * Δt
β(t) = β(t-1) + gy * Δt
```

where `Δt = t - t_prev` is the time step.

### Angle Wrapping

To keep angles in the range `[-π, π]`:

```python
if angle > π:
    angle = angle - 2π
if angle < -π:
    angle = angle + 2π
```

### Advantages
- High frequency response
- Not affected by linear accelerations
- Smooth output

### Disadvantages
- Drifts over time due to integration of noise
- Requires initial orientation
- Accumulates errors

## Complementary Filter

### Principle

The complementary filter combines accelerometer and gyroscope data to leverage the advantages of both sensors while minimizing their disadvantages.

### Mathematical Formulation

**General form:**
```
θ_fused = (1 - k) * θ_gyro + k * θ_accel
```

**Detailed implementation:**

For each angle (α, β):

1. **Predict from gyroscope:**
   ```
   θ_pred = θ_prev + gyro * Δt
   ```

2. **Measure from accelerometer:**
   ```
   θ_accel = f(ax, ay, az)
   ```

3. **Fuse:**
   ```
   θ_fused = (1 - k) * θ_pred + k * θ_accel
   ```

### Filter Coefficient (k)

The coefficient `k` determines the balance between sensors:

- **k = 0**: Pure gyroscope (will drift)
- **k = 1**: Pure accelerometer (will be noisy)
- **k ≈ 0.05** (default): Good balance for most applications

**Frequency interpretation:**
- Low-pass filter for accelerometer (removes high-frequency noise)
- High-pass filter for gyroscope (removes low-frequency drift)

### Tuning Guidelines

| Use Case | Recommended k | Reasoning |
|----------|--------------|-----------|
| Slow, smooth motion | 0.02 - 0.05 | Trust gyroscope more |
| Quick, jerky motion | 0.05 - 0.1 | Trust accelerometer more |
| Long-term stability | 0.05 - 0.15 | Prevent drift |
| Short-term accuracy | 0.01 - 0.03 | Smooth response |

## Coordinate Systems

### IMU Body Frame

```
     z (forward)
     ↑
     |
     |____→ y (right)
    /
   /
  ↙ x (down)
```

### Euler Angles

- **α (alpha)**: Roll - rotation around x-axis
- **β (beta)**: Pitch - rotation around y-axis  
- **γ (gamma)**: Yaw - rotation around z-axis (not estimated with 6-DOF IMU)

### Sign Conventions

- Positive rotation follows right-hand rule
- Angles measured in radians internally
- Converted to degrees for display (180/π factor)

## Implementation Details

### Initialization

At startup:
```python
alpha = 0
beta = 0
lastTimestamp = -1
```

### First Reading

On the first data point, we initialize from the accelerometer:
```python
if lastTimestamp == -1:
    alpha = processAccel(accel)[0]
    beta = processAccel(accel)[1]
```

### Steady State

For subsequent readings, the complementary filter is applied continuously.

## Limitations and Future Work

### Current Limitations

1. **No magnetometer**: Cannot estimate yaw (heading)
2. **Gimbal lock**: Euler angles suffer from gimbal lock at ±90° pitch
3. **Linear acceleration**: Affects accelerometer-based estimation during motion

### Possible Improvements

1. **Kalman Filter**: More sophisticated sensor fusion
2. **Quaternions**: Avoid gimbal lock, smoother interpolation
3. **Magnetometer Integration**: Full 9-DOF orientation (including yaw)
4. **Adaptive Filter**: Automatically adjust k based on motion characteristics

## References

1. Madgwick, S. (2010). "An efficient orientation filter for IMU and MARG sensor arrays"
2. Mahony, R. (2008). "Nonlinear complementary filters on the special orthogonal group"
3. Colton, S. (2007). "The balance filter: A simple solution for integrating accelerometer and gyroscope measurements"

## Example Calculations

### Sample Data Point

```
timestamp = 1.0
ax = -2.0 m/s²
ay = -0.1 m/s²
az = 9.6 m/s²
gx = 0.002 rad/s
gy = -0.003 rad/s
gz = 0.004 rad/s
```

### Accelerometer Processing

```
alpha_accel = atan2(9.6, -0.1) = 1.5808 rad ≈ 90.6°
beta_accel = asin(-2.0/9.8) = -0.2046 rad ≈ -11.7°
```

### Gyroscope Processing (Δt = 0.01s)

```
alpha_gyro = alpha_prev + 0.002 * 0.01 = alpha_prev + 0.00002
beta_gyro = beta_prev + (-0.003) * 0.01 = beta_prev - 0.00003
```

### Complementary Filter (k = 0.05)

```
alpha_fused = 0.95 * (alpha_prev + 0.00002) + 0.05 * 1.5808
beta_fused = 0.95 * (beta_prev - 0.00003) + 0.05 * (-0.2046)
```

---

*For questions or clarifications, please open an issue on GitHub.*
