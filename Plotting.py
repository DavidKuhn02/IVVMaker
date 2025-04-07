from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setParent(parent)
        self.constant_voltage = False  # True if the measurement is a constant voltage measurement, then the current is plotted against time
        self.custom_limits = False  # True if the user has set custom limits
        self.xlim = None
        self.ylim = None
        self.live_xdata = []  #Array of the live x data (always given by SMU0)
        self.live_ydata = []  #Array of the live y data (always given by SMU0)
        self.old_xdata = []   #Arrays of old data (either from file or from prev measurement)
        self.old_ydata = []   #Arrays of arrays 
        self.labels = []      #Array of lables of old data 
        self.start_plot()

    def start_plot(self):
        self.clear_data()
        self.update_plot_old_data()
        self.ax.set_xlabel('Voltage [V]')
        self.ax.set_ylabel('Current [uA]')
        self.ax.set_title('Live IV data')
        self.ax.grid(True)

    def update_plot_live_data(self, new_x = None , new_y = None,time_between_measurements = 1):
        if self.constant_voltage:
            self.update_plot_live_data_constant_voltage(new_y = new_y, time_between_points=time_between_measurements)
            return
        
        self.ax.clear()
        self.live_xdata.append(float(new_x))
        self.live_ydata.append(float(new_y))
        self.ax.plot(np.array(self.live_xdata), np.array(self.live_ydata)*1e6, label = 'Live IV Data (SMU0)', linestyle = 'none', marker = '.')
        self.update_plot_old_data()

    def update_plot_old_data(self):
        _, labels = self.ax.get_legend_handles_labels()
        for i in range(len(self.old_xdata)):
            if self.labels[i] in labels:
                self.ax.legend()
                self.ax.grid(True)
                continue
            self.ax.plot(np.array(self.old_xdata[i]), np.array(self.old_ydata[i])*1e6, label = self.labels[i], linestyle = 'none', marker = '.')
        self.ax.set_xlabel('Voltage [V]')
        self.ax.set_ylabel('Current [uA]')
        self.ax.set_title('Live IV data')
        self.ax.legend()
        self.ax.grid(True)
        if self.custom_limits:
            self.set_custom_limits()
        self.draw()

    def update_plot_live_data_constant_voltage(self, new_y = None, time_between_points = 1):
        self.ax.clear()
        self.live_ydata.append(float(new_y))
        self.ax.plot(np.arange(len(self.live_ydata))*time_between_points, np.array(self.live_ydata)*1e6, label = 'Live It Data (SMU0)', linestyle = 'none', marker = '.')
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Current [uA]')
        self.ax.set_title('Live It data')
        self.ax.grid(True)
        self.ax.legend()
        self.draw()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('Voltage [V]')
        self.ax.set_ylabel('Current [uA]')
        self.ax.set_title('Live IV data')
        self.ax.legend() 
        self.old_xdata = []
        self.old_ydata = []
        self.labels = []
        self.ax.grid(True)
        self.draw()

    def clear_data(self):
        self.live_xdata = []
        self.live_ydata = []

    def load_data(self, file):
        if file in self.labels:
            return
        try:
            x, y = np.loadtxt(file, skiprows = 1, unpack = True, usecols = [0, 1])
        except FileNotFoundError:
            print(file, ' not found')

        self.old_xdata.append(x)
        self.old_ydata.append(y)
        self.labels.append(file)
        self.update_plot_old_data()
 
    def set_custom_limits(self):
        
        if self.xlim is not None:
            self.ax.set_xlim(self.xlim[0], self.xlim[1])
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim[0], self.ylim[1])
        self.draw()