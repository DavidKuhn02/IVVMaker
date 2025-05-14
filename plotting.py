#In this file all the stuff related to the plotting of the canvas is handled. 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import numpy as np


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
        self.live_x_data = []
        self.live_y_data = []
        self.draw_plot() #Draw the initial plot

    def draw_plot(self):
        #This function will redraw the plot with the current data
        live_data_lines = [line for line in self.ax.lines if line.get_label() == 'Live Data']
        for line in live_data_lines:
            line.remove()
        self.ax.set_title(self.parameters['type']+ ' Measurement')
        self.ax.set_xlabel(self.parameters['x_label'])
        self.ax.set_ylabel(self.parameters['y_label'])
        if self.parameters['type'] == 'IV' or self.parameters['type'] == 'CV':
            self.ax.plot(np.array(self.live_x_data), np.array(self.live_y_data), label=self.parameters['labels'][0], linestyle ='None', marker='o', color = 'tab:blue')   
        else: 
            self.ax.plot(np.arange(len(self.live_y_data)), np.array(self.live_y_data), label=self.parameters['labels'][0], linestyle ='None', marker='o', color = 'tab:blue')
        self.ax.grid(True)
        self.ax.legend()
        self.draw()
    
    def update_data(self, x_data, y_data):
        #This function will update the data of the plot
        self.live_x_data.append(x_data)
        self.live_y_data.append(y_data)  
        
    
    def change_plot_type(self, type):
        #This function will change the plot type
        self.parameters['type'] = type
        self.parameters['labels'] = ['Live Data']
        self.live_x_data = []  #Clear all the data 
        self.live_y_data = []
        self.old_x_data = []
        self.old_y_data = []
        if type == 'IV':
            self.parameters['x_label'] = 'Voltage [V]'
            self.parameters['y_label'] = 'Current [A]'
            self.ax.autoscale_view()
        elif type == 'CV':
            self.parameters['x_label'] = 'Voltage [V]'
            self.parameters['y_label'] = 'Current [A]'
            self.ax.autoscale_view()
        elif type == 'Constant Voltage':
            self.parameters['x_label'] = 'Number of Measurements'
            self.parameters['y_label'] = 'Current [A]'
            self.ax.autoscale_view()
        self.draw_plot()
    
    def clear_live_data(self):
        #This function will clear the live data
        self.live_x_data = []
        self.live_y_data = []
        self.draw_plot()

    def clear_old_data(self):
        #This function will clear the old data
        old_data_lines = [line for line in self.ax.lines if line.get_label() != 'Live Data']
        for line in old_data_lines:
            line.remove()
        self.old_x_data = []
        self.old_y_data = []
        self.draw_plot()
        
    def load_old_data(self):
        #This function will load the old data
        file = QFileDialog.getOpenFileName(self.ui, 'Open File', self.ui.data_path, 'CSV files (*.csv);;All files (*)')[0]
        if file:
            if self.parameters['type'] == 'IV':
                self.old_x_data, self.old_y_data = np.loadtxt(file, delimiter=' ', unpack=True, skiprows=1, usecols = [1, 2])
                self.ax.plot(np.array(self.old_x_data), np.array(self.old_y_data), label=str(file), linestyle ='None', marker='o')   
            elif self.parameters['type'] == 'CV':
                self.old_x_data, self.old_y_data = np.loadtxt(file, delimiter=' ', unpack=True, skiprows=1, usecols = [1, 2])
                self.ax.plot(np.array(self.old_x_data), np.array(self.old_y_data), label=str(file), linestyle ='None', marker='o')
            elif self.parameters['type'] == 'Constant Voltage': 
                self.old_x_data, self.old_y_data = np.loadtxt(file, delimiter=' ', unpack=True, skiprows=1, usecols = [1, 2])
                self.ax.plot(np.arange(len(self.old_y_data)), np.array(self.old_y_data), label=str(file), linestyle ='None', marker='o')
            self.draw_plot()    