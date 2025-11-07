#In this file all the stuff related to the plotting of the canvas is handled. 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.gridspec import GridSpec

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        #Initializes the plot canvas
        
        self.fig, self.ax = plt.subplots() #Create a figure and axis
        super().__init__(self.fig)
        self.setParent(parent)
        self.ui = parent
        self.parameters = {
            'type': 'IV',  # Type of measurement (IV, CV, Constant Voltage)
            'labels': ['Live Data'],
            'y_label': 'Current [A]',
            'x_label': 'Voltage [V]',
            
        }
        self.live_x_data = [] # Voltage for IV and CV, Number of Measurements for Constant Voltage
        self.live_y_data = [] # Current for IV and Constant Voltage
        self.raw_data = [] #Array that holds CV data
        self.voltage_cv = []
        self.frequencies_cv = []
        self.impedance_cv = [] 
        self.phase_cv = []

    def draw_plot(self):
        #This function will redraw the plot with the current data
        if self.parameters['type'] == 'CV':
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            self.ax4.clear()
            
            self.ax1.plot(self.voltage_cv, self.phase_cv, label='Phase', linestyle='none', marker = 'o', color='tab:blue')
            self.ax3.plot(self.voltage_cv, self.impedance_cv, label='Impedance', linestyle='none', marker = 'o', color='tab:orange')
            self.ax2.plot(self.frequencies_cv, self.phase_cv, label='Phase', linestyle='none', marker = 'o', color='tab:blue')
            self.ax4.plot(self.frequencies_cv, self.impedance_cv, label='Impedance', linestyle='none', marker = 'o', color='tab:orange')
            
            self.ax1.set_title('CV Voltage')
            self.ax2.set_title('CV Frequency')

            self.ax1.set_xlabel('Voltage [V]')
            self.ax2.set_xlabel('Frequency [Hz]')
            self.ax3.set_xlabel('Voltage [V]')
            self.ax4.set_xlabel('Frequency [Hz]')
            self.ax1.set_ylabel('Phase [°]')
            self.ax2.set_ylabel('Phase [°]')
            self.ax3.set_ylabel('Impedance [Ω]')
            self.ax4.set_ylabel('Impedance [Ω]')

            self.ax1.legend(loc='upper right')
            self.ax2.legend(loc='upper right')
            self.ax3.legend(loc='upper right')
            self.ax4.legend(loc='upper right')

            self.ax2.set_xscale('log')
            self.ax4.set_xscale('log')

            self.ax1.grid(True)
            self.ax2.grid(True)
            self.ax3.grid(True)
            self.ax4.grid(True)

            self.fig.tight_layout()
        else:
            live_data_lines = [line for line in self.ax.lines if line.get_label() == 'Live Data']
            for line in live_data_lines:
                line.remove()
            self.ax.set_title(self.parameters['type']+ ' Measurement')
            self.ax.set_xlabel(self.parameters['x_label'])
            self.ax.set_ylabel(self.parameters['y_label'])
            if self.parameters['type'] == 'IV':
                self.ax.plot(np.array(self.live_x_data), np.array(self.live_y_data), label=self.parameters['labels'][0], linestyle ='None', marker='o', color = 'tab:blue')   
            else: 
                self.ax.plot(np.arange(len(self.live_y_data)), np.array(self.live_y_data), label=self.parameters['labels'][0], linestyle ='None', marker='o', color = 'tab:blue')
            self.ax.grid(True)
            self.ax.legend()
            self.fig.tight_layout()
        
        self.draw()
    
    def update_data(self, x_data, y_data):
        #This function will update the data of the plot
        self.live_x_data.append(float(x_data))
        self.live_y_data.append(float(y_data))  

    def update_cv_data(self, voltage, frequency, impedance, phase):
        self.voltage_cv.append(float(voltage))
        self.frequencies_cv.append(float(frequency))
        self.impedance_cv.append(float(impedance))
        self.phase_cv.append(float(phase))

        
    def change_plot_type(self, type):
        #This function will change the plot type
        self.parameters['type'] = type
        self.parameters['labels'] = ['Live Data']
        self.live_x_data = []  #Clear all the data 
        self.live_y_data = []
        self.old_x_data = []
        self.old_y_data = []
        self.voltage_cv = []
        self.frequencies_cv = []
        self.impedance_cv = [] 
        self.phase_cv = []  

        self.fig.clear()  # Clear the figure   
        if type == 'IV':
            self.ax = self.fig.add_subplot(111)  # Add a new subplot
            self.parameters['x_label'] = 'Voltage [V]'
            self.parameters['y_label'] = 'Current [A]'
            self.ax.autoscale_view(scalex=True, scaley=True)
        elif type == 'CV':
            self.ax1 = self.fig.add_subplot(2, 2, 1)
            self.ax2 = self.fig.add_subplot(2, 2, 2)

            self.ax3= self.fig.add_subplot(2, 2, 3)
            self.ax4 = self.fig.add_subplot(2, 2, 4)    

#
            self.ax.autoscale_view(scalex=True, scaley=True)
        elif type == 'Constant Voltage':
            self.ax = self.fig.add_subplot(111)
            self.parameters['x_label'] = 'Number of Measurements'
            self.parameters['y_label'] = 'Current [A]'
            self.ax.autoscale_view(scalex=True, scaley=True)
        self.draw_plot()

    def clear_live_data(self):
        #This function will clear the live data
        self.live_x_data = []
        self.live_y_data = []
        self.voltage_cv = []  
        self.frequencies_cv = [] 
        self.impedance_cv = [] #Only for CV to store impedance data
        self.phase_cv = [] #Only for CV to store phase data        
        self.draw_plot()
        self.ax.autoscale_view(scalex=True, scaley=True)
        
    def clear_old_data(self):
        #This function will clear the old data
        old_data_lines = [line for line in self.ax.lines if line.get_label() != 'Live Data']
        for line in old_data_lines:
            line.remove()
        self.old_x_data = []
        self.old_y_data = []
        self.draw_plot()
        self.ax.autoscale_view(scalex=True, scaley=True)
        
    def load_old_data(self):
        #This function will load the old data
        file = QFileDialog.getOpenFileName(self.ui, 'Open File', self.ui.data_path, 'CSV files (*.csv);;All files (*)')[0]
        if file:
            if self.parameters['type'] == 'IV':
                self.old_x_data, self.old_y_data = np.loadtxt(file, delimiter=' ', unpack=True, skiprows=1, usecols = [1, 2])
                self.ax.plot(np.array(self.old_x_data), np.array(self.old_y_data), label=str(file), linestyle ='None', marker='o')   
            elif self.parameters['type'] == 'CV':
                print('This function is not available for CV Measurements.')
            elif self.parameters['type'] == 'Constant Voltage': 
                self.old_x_data, self.old_y_data = np.loadtxt(file, delimiter=' ', unpack=True, skiprows=1, usecols = [1, 2])
                self.ax.plot(np.arange(len(self.old_y_data)), np.array(self.old_y_data), label=str(file), linestyle ='None', marker='o')
            self.draw_plot()    