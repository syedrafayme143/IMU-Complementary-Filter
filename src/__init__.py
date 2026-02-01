"""
IMU Visualizer Package

A real-time visualization and analysis tool for IMU data with sensor fusion capabilities.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .DataPlot import DataPlot
from .imu import DataReader, IMUGui

__all__ = ["DataPlot", "DataReader", "IMUGui"]
