#In this file all the stuff related to the plotting of the canvas is handled. 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        #Initializes the plot canvas
        self.fig, self.ax = plt.subplots() #Create a figure and axis
        super().__init__(self.fig)
        self.setParent(parent)
        self.constant_voltage = False  # True if the measurement is a constant voltage measurement, then the current is plotted against time
        self.custom_limits = False  # True if the user has set custom limits
        self.xlim = None  #Array of the x limits
        self.ylim = None  #Array of the y limits
        self.live_xdata = []  #Array of the live x data (always given by SMU0)
        self.live_ydata = []  #Array of the live y data (always given by SMU0)
        self.old_xdata = []   #Arrays of old data (either from file or from prev measurement)
        self.old_ydata = []   #Arrays of arrays 
        self.labels = []      #Array of lables of old data
        self.old_time_between_steps = [] #Time between steps of the old data 
        self.start_plot() #Start the plot with the default settings

    def start_plot(self):
        self.clear_data() #Clear the live data
        self.clear_plot() #Clear the plot
        self.update_plot()

    def restart_plot(self):
        self.clear_data() 
        self.update_plot()

    def update_plot(self, new_x = None , new_y = None, time_between_measurements = 1):
        #Update the plot with new data, 
        self.ax.clear() #Clear the plot
        if new_x != None and new_y != None: #If new data is given, append it to the live data
            self.live_xdata.append(float(new_x))
            self.live_ydata.append(float(new_y))
        if self.constant_voltage:   #If the measurement is a constant voltage measurement, plot the current against time
            self.update_plot_live_data_constant_voltage(time_between_points=time_between_measurements)
        else:                       #If the measurement is a IV measurement, plot the current against voltage
            self.update_plot_live_data()

    def update_plot_live_data(self):
        #Update the plot with the live data
        if len(self.live_ydata) != 0:
            self.ax.plot(np.array(self.live_xdata), np.array(self.live_ydata)*1e6, label = 'Live IV Data (SMU0)', linestyle = 'none', marker = '.')  #Plot the live data
        _, labels = self.ax.get_legend_handles_labels()
        for i in range(len(self.old_xdata)):
            if self.labels[i] in labels:
                continue
            self.ax.plot(np.array(self.old_xdata[i]), np.array(self.old_ydata[i])*1e6, label = self.labels[i], linestyle = 'none', marker = '.') #Plot the old data, which is not already plotted
        self.ax.set_xlabel('Voltage [V]')
        self.ax.set_ylabel('Current [uA]')
        self.ax.set_title('Live IV data')
        self.ax.legend()
        self.ax.grid(True)
        if self.custom_limits:
            self.set_custom_limits()
        self.draw()
        
    def update_plot_live_data_constant_voltage(self, time_between_points = 1):
        #Update the plot with the live data for constant voltage measurement
        if len(self.live_ydata) != 0:
            self.ax.plot(np.arange(len(self.live_ydata))*time_between_points, np.array(self.live_ydata)*1e6, label = 'Live It Data (SMU0)', linestyle = 'none', marker = '.') #Plot the live data
        _, labels = self.ax.get_legend_handles_labels()
        for i in range(len(self.old_xdata)):
            if self.labels[i] in labels:
                continue
            self.ax.plot(np.arange(len(self.old_ydata[i]))*self.old_time_between_steps[i], np.array(self.old_ydata[i])*1e6, label = self.labels[i], linestyle = 'none', marker = '.') #Plot the old data, which is not already plotted
        self.ax.set_xlabel('Time [s]') #Change the x axis label to time
        self.ax.set_ylabel('Current [uA]')
        self.ax.set_title('Live It data')
        self.ax.grid(True)
        self.ax.legend()
        self.draw()

    def clear_plot(self):
        #This function clears the old data from the plot 
        self.ax.clear()
        if self.constant_voltage:
            self.ax.set_xlabel('Time [s]')
            self.ax.set_ylabel('Current [uA]')
            self.ax.set_title('Live It data')
        else:
            self.ax.set_xlabel('Voltage [V]')
            self.ax.set_ylabel('Current [uA]')
            self.ax.set_title('Live IV data')
        self.ax.legend() 
        self.old_xdata = []
        self.old_ydata = []
        self.labels = []
        self.ax.grid(True)
        self.draw(),

    def clear_data(self):
        #Clear the live data for multiple following measurements
        self.live_xdata = []
        self.live_ydata = []

    def load_data(self, file):
        #Load data from a file
        #The file should contain two columns, the first column is the x data and the second column is the y data
        if file in self.labels:
            return
        try:
            type, time_between_steps = np.loadtxt(file, max_rows = 1, dtype = str, usecols = [0, 1], delimiter=' ') #Load the first two columns of the file 
            x, y = np.loadtxt(file, skiprows = 2, unpack = True, usecols = [0, 1])
            print(type, time_between_steps)
            if type == 'Time_between_points:':
                self.old_time_between_steps.append(float(time_between_steps))
        except FileNotFoundError:
            print(file, ' not found')

        self.old_xdata.append(x)
        self.old_ydata.append(y)
        self.labels.append(file)
        self.update_plot()
    
    def keep_data(self, label, time_between_step = 0):
        #Keep the data from the last measurement
        #This function is called when the measurement is stopped
        if len(self.live_xdata) == 0:
            return
        self.old_xdata.append(self.live_xdata)
        self.old_ydata.append(self.live_ydata)
        self.labels.append(label)
        self.old_time_between_steps.append(time_between_step)
        self.update_plot()
        self.clear_data()

    def set_custom_limits(self):
        #Set cutom limits for the plot
        #The limits are set by the user in the GUI
        if self.xlim is not None:
            self.ax.set_xlim(self.xlim[0], self.xlim[1])
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim[0], self.ylim[1])
        self.draw()