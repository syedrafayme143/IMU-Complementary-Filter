"""
DataPlot Module - Real-time data visualization with recording capabilities.

This module provides a class for creating interactive real-time plots using DearPyGUI,
with support for data recording to CSV files and pause/resume functionality.
"""

import dearpygui.dearpygui as dpg
import os.path


class DataPlot:
    """
    A class for real-time plotting of multiple data series with recording capabilities.
    
    Attributes:
        labels_ (list): Labels for each data series
        maxnumpoints_ (int): Maximum number of points to display before scrolling
        recordFile_ (file): File handle for recording data (None if not recording)
        paused_ (bool): Whether the plot updates are paused
    """
    
    def __init__(self, labels, maxnumpoints, showRecordPause=False):
        """
        Initialize the DataPlot.
        
        Args:
            labels (tuple/list): Labels for each data series to plot
            maxnumpoints (int): Maximum number of data points to display
            showRecordPause (bool): Whether to show record and pause buttons
        """
        self.curves_ = []
        for i in range(len(labels)):
            self.curves_.append([])
        self.timedata_ = []
        self.series_ = []
        self.labels_ = labels
        self.maxnumpoints_ = maxnumpoints
        self.recordFile_ = None
        self.fileFirstLine_ = False
        self.paused_ = False
        self.showRecordPause_ = showRecordPause

    def recordCallback(self):
        """Toggle recording state and manage CSV file creation/closing."""
        if self.recordFile_ is None:
            fname = dpg.get_value(self.csvText_)
            if fname == "":
                fname = "bb8.csv"
            elif not fname.endswith(".csv"):
                fname = fname + ".csv"
            if os.path.isfile(fname):
                print(f"Appending to {fname}")
                self.recordFile_ = open(fname, "a")
                self.fileFirstLine_ = False
            else:
                print(f"Creating {fname}")
                self.recordFile_ = open(fname, "w")
                self.fileFirstLine_ = True
            dpg.configure_item(self.recordButton_, label="Stop")
        else:
            self.recordFile_.close()
            self.recordFile_ = None
            dpg.configure_item(self.recordButton_, label="Record")

    def pauseCallback(self):
        """Toggle pause state for plot updates."""
        if self.paused_:
            dpg.configure_item(self.pauseButton_, label="Pause")
            self.paused_ = False
        else:
            dpg.configure_item(self.pauseButton_, label="Continue")
            self.paused_ = True

    def createGUI(self, width, height, label=""):
        """
        Create the GUI elements for the plot.
        
        Args:
            width (int): Width of the plot (-1 for auto)
            height (int): Height of the plot (-1 for auto)
            label (str): Label for the plot window
        """
        if self.showRecordPause_:
            with dpg.group(horizontal=True):
                self.recordButton_ = dpg.add_button(label="Record", callback=self.recordCallback)
                self.csvText_ = dpg.add_input_text(label="CSV")
                self.pauseButton_ = dpg.add_button(label="Pause", callback=self.pauseCallback)

        with dpg.plot(label=label, width=width, height=height):
            dpg.add_plot_legend()
            self.xAxis_ = dpg.add_plot_axis(dpg.mvXAxis, label="t")
            self.yAxis_ = dpg.add_plot_axis(dpg.mvYAxis, label="value")
            for i in range(len(self.labels_)):
                self.series_.append(dpg.add_line_series([], [], label=self.labels_[i], parent=self.yAxis_))

    def addDataVector(self, timestamp, vector):
        """
        Add a new data point to the plot.
        
        Args:
            timestamp (float): Time value for x-axis
            vector (list): Data values for each series (must match number of labels)
        """
        # Validate input
        if len(vector) != len(self.labels_):
            print(f"Trying to add {len(vector)}-vector to data plot with size {len(self.labels_)}")
            return
            
        # Collect data
        for i in range(len(vector)):
            self.curves_[i].append(vector[i])
            while len(self.curves_[i]) > self.maxnumpoints_:
                del self.curves_[i][0]
        self.timedata_.append(timestamp)
        while len(self.timedata_) > self.maxnumpoints_:
            del self.timedata_[0]

        if self.paused_:
            return

        # Update plot
        for i in range(len(self.curves_)):
            dpg.set_value(self.series_[i], [self.timedata_, self.curves_[i]])
        dpg.set_axis_limits(self.xAxis_, self.timedata_[0], self.timedata_[-1])
        if len(self.timedata_) == 1:  # First entry
            self.autofit()

        if self.recordFile_ is None:
            return

        # Record to CSV if enabled
        if self.fileFirstLine_:
            print("# timestamp; ", end='', file=self.recordFile_)
            for label in self.labels_[:-1]:
                print(f"{label}; ", end='', file=self.recordFile_)
            print(self.labels_[-1], file=self.recordFile_)
            self.fileFirstLine_ = False
        print(f"{timestamp:f}; ", end='', file=self.recordFile_)
        for v in vector[:-1]:
            print(f"{v:f}; ", end='', file=self.recordFile_)
        print(f"{vector[-1]:f}", file=self.recordFile_)

    def autofit(self):
        """Auto-fit the y-axis to show all data."""
        dpg.fit_axis_data(self.yAxis_)
