"""
IMU Visualization Application

This application reads IMU (Inertial Measurement Unit) data and visualizes accelerometer
and gyroscope readings in real-time. It implements sensor fusion using a complementary
filter to estimate orientation angles.

Data format: timestamp, ax, ay, az, gx, gy, gz
Where:
    - timestamp: Time in seconds
    - ax, ay, az: Accelerometer readings (m/s²)
    - gx, gy, gz: Gyroscope readings (rad/s)
"""

import dearpygui.dearpygui as dpg
import sys
import select
import time
import math

from DataPlot import DataPlot


class DataReader:
    """
    Reads lines of comma-separated floats from a file or device.
    
    Supports both recorded data files and real-time device streams (e.g., /dev/ttyUSB0).
    For file playback, timestamps are used to simulate real-time data delivery.
    """
    
    def __init__(self, filename: str):
        """
        Initialize the DataReader.
        
        Args:
            filename (str): Path to data file or device (e.g., '/dev/ttyUSB0')
        """
        self.file = open(filename, "r")
        self.dataFromDevice = filename.startswith("/dev/")
        self.lastTimestamp = -1

    def readDataLine(self, floatcount: int = -1) -> list:
        """
        Read and parse one line of data.
        
        Args:
            floatcount (int): Expected number of floats (-1 to accept any count)
            
        Returns:
            list: Parsed float values, or None if no data available or parse error
            
        For non-device files, this method simulates real-time playback by sleeping
        according to the timestamps in the data.
        """
        if self.dataFromDevice:
            r, w, x = select.select([self.file], [], [], 0)
            if len(r) == 0:
                return None
        line = self.file.readline()
        if line == "":
            return None
        vector = line.split(",")
        if floatcount != -1 and len(vector) != floatcount:
            return None
        try:
            vector = list(map(float, vector))
        except:
            return None
        if not self.dataFromDevice:
            if self.lastTimestamp != -1:
                time.sleep(vector[0] - self.lastTimestamp)
        self.lastTimestamp = vector[0]
        return vector


class IMUGui:
    """
    GUI application for IMU data visualization and orientation estimation.
    
    Displays:
        - Raw accelerometer data (ax, ay, az)
        - Raw gyroscope data (p, q, r in degrees/s)
        - Accelerometer-derived angles (alpha, beta)
        - Gyroscope-integrated angles (alpha, beta)
        - Complementary filter fusion result (alpha, beta)
    """
    
    def __init__(self, dataReader, complK=0.05):
        """
        Initialize the IMU GUI.
        
        Args:
            dataReader (DataReader): Data source
            complK (float): Complementary filter coefficient (0-1)
                          Higher values give more weight to accelerometer
        """
        # Create all data plots to hold 1000 points before scrolling
        self.accelPlot = DataPlot(("ax", "ay", "az"), 1000)
        self.gyroPlot = DataPlot(("p", "q", "r"), 1000)
        self.accelResPlot = DataPlot(("alpha", "beta", "gamma"), 1000)
        self.gyroResPlot = DataPlot(("alpha", "beta", "gamma"), 1000)
        self.complResPlot = DataPlot(("alpha", "beta", "gamma"), 1000)

        # Initialize timestamp to show that we haven't read anything yet
        self.lastTimestamp = -1

        # Integration results from gyro (raw) and complementary filter
        self.alphaGInt = self.betaGInt = 0
        self.alphaCInt = self.betaCInt = 0

        # Complementary filter coefficient
        self.complK = complK

        # We will use this to read data
        self.dataReader = dataReader

    def createWindow(self):
        """Create the main GUI window with tabbed plots."""
        with dpg.window(tag="Status"):
            with dpg.tab_bar():
                with dpg.tab(label="Accel"):
                    self.accelPlot.createGUI(-1, -1)
                with dpg.tab(label="Gyro"):
                    self.gyroPlot.createGUI(-1, -1)
                with dpg.tab(label="Accel Result"):
                    self.accelResPlot.createGUI(-1, -1)
                with dpg.tab(label="Gyro Result"):
                    self.gyroResPlot.createGUI(-1, -1)
                with dpg.tab(label="Compl Result"):
                    self.complResPlot.createGUI(-1, -1)

    def processAccel(self, timestamp, vec):
        """
        Calculate orientation angles from accelerometer data.
        
        Assumes gravity vector dominates accelerometer readings.
        
        Args:
            timestamp (float): Current timestamp
            vec (list): [ax, ay, az] in m/s²
            
        Returns:
            tuple: (alpha, beta, gamma) angles in radians
        """
        try:
            alpha = math.atan2(vec[2], vec[1])
        except:
            alpha = 0
            print(f"Error processing atan2({vec[2]}, {vec[1]})")
        try:
            beta = math.asin(vec[0] / 9.8)
        except:
            beta = 0
            print(f"Error processing asin({vec[0] / 9.8})")
        return (alpha, beta, 0)

    def processGyro(self, timestamp, vec):
        """
        Integrate gyroscope data to estimate orientation angles.
        
        Args:
            timestamp (float): Current timestamp
            vec (list): [gx, gy, gz] angular velocities in rad/s
            
        Returns:
            tuple: (alpha, beta, gamma) integrated angles in radians
        """
        deltaT = timestamp - self.lastTimestamp
        self.alphaGInt = self.alphaGInt + vec[0] * deltaT
        self.betaGInt = self.betaGInt + vec[1] * deltaT
        
        # Wrap angles to [-π, π]
        if self.alphaGInt > math.pi:
            self.alphaGInt = self.alphaGInt - 2 * math.pi
        if self.alphaGInt < -math.pi:
            self.alphaGInt = self.alphaGInt + 2 * math.pi
        if self.betaGInt > math.pi:
            self.betaGInt = self.betaGInt - 2 * math.pi
        if self.betaGInt < -math.pi:
            self.betaGInt = self.betaGInt + 2 * math.pi
            
        self.lastTimestamp = timestamp  # FIXED: Was self.lasttimestamp (typo)
        return (self.alphaGInt, self.betaGInt, 0)

    def processCompl(self, timestamp, accel, gyro):
        """
        Apply complementary filter for sensor fusion.
        
        Combines high-frequency gyroscope data with low-frequency accelerometer
        data to get robust orientation estimates.
        
        Args:
            timestamp (float): Current timestamp
            accel (list): [ax, ay, az] accelerometer readings
            gyro (list): [gx, gy, gz] gyroscope readings
            
        Returns:
            tuple: (alpha, beta, gamma) fused angles in radians
        """
        deltaT = timestamp - self.lastTimestamp
        accelC = self.processAccel(timestamp, accel)

        # Complementary filter: (1-k)*gyro + k*accel
        alpha = (self.alphaCInt + gyro[0] * deltaT) * (1 - self.complK)
        alpha = alpha + accelC[0] * self.complK

        beta = (self.betaCInt + gyro[1] * deltaT) * (1 - self.complK)
        beta = beta + accelC[1] * self.complK

        self.alphaCInt = alpha
        self.betaCInt = beta

        # Wrap angles to [-π, π]
        if self.alphaCInt > math.pi:
            self.alphaCInt = self.alphaCInt - 2 * math.pi
        if self.alphaCInt < -math.pi:
            self.alphaCInt = self.alphaCInt + 2 * math.pi
        if self.betaCInt > math.pi:
            self.betaCInt = self.betaCInt - 2 * math.pi
        if self.betaCInt < -math.pi:
            self.betaCInt = self.betaCInt + 2 * math.pi
            
        self.lastTimestamp = timestamp

        return (alpha, beta, 0)

    def run(self):
        """Main application loop."""
        dpg.create_context()
        dpg.create_viewport()
        self.createWindow()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Status", True)
        print("Waiting for data...")
        
        while dpg.is_dearpygui_running():
            while True:
                data = self.dataReader.readDataLine(7)
                if data is None:
                    dpg.render_dearpygui_frame()
                    break
                    
                # Update plots with data
                self.accelPlot.addDataVector(data[0], data[1:4])
                self.gyroPlot.addDataVector(data[0], [(180.0 / math.pi) * v for v in data[4:7]])
                self.accelResPlot.addDataVector(data[0], self.processAccel(data[0], data[1:4]))
                self.gyroResPlot.addDataVector(data[0], self.processGyro(data[0], data[4:7]))
                self.complResPlot.addDataVector(
                    data[0], 
                    [(180.0 / math.pi) * v for v in self.processCompl(data[0], data[1:4], data[4:7])]
                )
                dpg.render_dearpygui_frame()
                
        dpg.destroy_context()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file_or_port>")
        print("\nExamples:")
        print(f"  {sys.argv[0]} imudata.txt")
        print(f"  {sys.argv[0]} /dev/ttyUSB0")
        sys.exit(-1)
        
    reader = DataReader(sys.argv[1])
    gui = IMUGui(reader)
    gui.run()
