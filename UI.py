from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, QScrollArea, QFrame, QVBoxLayout, QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton
from PyQt5.QtCore import QThread, pyqtSignal
import pyvisa as visa
import Devices
import Plotting
from Functionality import Functionality, Device_Handler, Sweep

class Ui_MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.rm = visa.ResourceManager('@py') # Set up the resource manager
        self.device_handler = Device_Handler(self.rm) # Initialize the device handler
        self.sweep_creator = Sweep()
        self.logic = Functionality(self)
        self.setup_ui()

    def setup_ui(self):
       
        self.setWindowTitle('IVV Maker')  #Window settings
        self.setGeometry(320, 180, 1920, 1080)

        self.layout = QGridLayout(self)  #Creates the Layout for the window
        self.layout.setAlignment(QtCore.Qt.AlignTop) #Aligns the layout to the top
        self.layout.setAlignment(QtCore.Qt.AlignLeft) #Aligns the layout to the left

        self.device_groupBox = QGroupBox("Connected Devices")  #Creates a group box for the connected devices
       
        self.device_groupBox_layout = QVBoxLayout(self.device_groupBox)   

        self.device_scrollArea = QScrollArea()
        self.device_scrollArea.setWidgetResizable(True)
        self.device_groupBox.setMaximumSize(600, 600) 

        self.device_scrollWidget = QWidget()
        self.device_scrollLayout = QVBoxLayout(self.device_scrollWidget)
        self.device_scrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.device_scrollWidget.setLayout(self.device_scrollLayout)    

        self.device_widgets = []  # List to store the device widgets

        self.device_scrollArea.setWidget(self.device_scrollWidget)  

        self.device_groupBox_layout.addWidget(self.device_scrollArea)   
         
        self.layout.addWidget(self.device_groupBox, 0, 0, 2, 1)

        self.add_device_box = QGroupBox('Manage Devices')  #Creates a group box for adding devices
        self.add_device_layout = QVBoxLayout()
        self.add_device_layout.setAlignment(QtCore.Qt.AlignTop)

        self.select_decive = QComboBox()  #Select Device ComboBox
        self.select_decive.setCurrentText('Select Device')
        self.select_decive.addItem('Select Device')
        self.add_device_layout.addWidget(self.select_decive)

        self.refresh_button = QPushButton('Search Devices')  #Refresh Button
        self.refresh_button.clicked.connect(self.logic.refresh_devices)
        self.add_device_layout.addWidget(self.refresh_button)

        self.add_device_button = QPushButton('Add selected device')  #Add Device Button
        self.add_device_button.clicked.connect(self.logic.add_device_entry)
        self.add_device_layout.addWidget(self.add_device_button)
        
        self.add_all_devices_button = QPushButton('Search and add all connected Devices')
        self.add_all_devices_button.clicked.connect(self.logic.add_all_devices)
        self.add_device_layout.addWidget(self.add_all_devices_button)

        self.add_device_box.setLayout(self.add_device_layout)
        self.layout.addWidget(self.add_device_box, 2, 0, 1, 1)

        self.measurement_settings_box = QGroupBox('Measurement Settings') #Creates a group box for the measurement settings
        self.measurement_settings_box.setMaximumWidth(600)
        self.measurement_settings_layout = QGridLayout()
        self.measurement_settings_layout.setAlignment(QtCore.Qt.AlignTop)

        self.measurement_settings_layout.addWidget(QLabel('Start Voltage [V]'), 0, 0)  #Start Voltage SpinBox and Label
        self.startV = QDoubleSpinBox()
        self.startV.setRange(-1100, 1100)
        self.startV.setDecimals(0)
        self.startV.setSuffix(' V')
        self.startV.setValue(0) 
        self.measurement_settings_layout.addWidget(self.startV, 0, 1)

        self.measurement_settings_layout.addWidget(QLabel('Stop Voltage [V]'), 1, 0)  #End Voltage SpinBox and Label
        self.stopV = QDoubleSpinBox()
        self.stopV.setRange(-1100, 1100)
        self.stopV.setDecimals(0)
        self.stopV.setSuffix(' V')
        self.stopV.setValue(-160)
        self.measurement_settings_layout.addWidget(self.stopV, 1, 1)

        self.measurement_settings_layout.addWidget(QLabel('Step Voltage [V]'), 2, 0)  #Step Voltage SpinBox and Label
        self.stepV = QDoubleSpinBox()
        self.stepV.setRange(-1100, 1100)
        self.stepV.setDecimals(2)
        self.stepV.setSuffix(' V')
        self.stepV.setValue(-1)
        self.measurement_settings_layout.addWidget(self.stepV, 2, 1)

        self.measurement_settings_layout.addWidget(QLabel('Time between \nsteps [s]'), 3, 0)  #Delay SpinBox and Label
        self.time_between_steps = QDoubleSpinBox()
        self.time_between_steps.setRange(0, 1000)
        self.time_between_steps.setDecimals(2)
        self.time_between_steps.setSuffix(' s')
        self.time_between_steps.setValue(.5)
        self.measurement_settings_layout.addWidget(self.time_between_steps, 3, 1)

        self.measurement_settings_layout.addWidget(QLabel('Time between \nmeasurements [s]'), 4, 0)  #Delay SpinBox and Label
        self.time_between_measurements = QDoubleSpinBox()
        self.time_between_measurements.setRange(0, 1000)
        self.time_between_measurements.setDecimals(2)  
        self.time_between_measurements.setSuffix(' s')
        self.time_between_measurements.setValue(.4)
        self.measurement_settings_layout.addWidget(self.time_between_measurements, 4, 1)

        self.measurements_per_step_label = QLabel('Measurements \nper step')  #Delay SpinBox and Label
        self.measurement_settings_layout.addWidget(self.measurements_per_step_label, 5, 0)  
        self.measurements_per_step = QSpinBox()
        self.measurements_per_step.setRange(1, 1000)
        self.measurements_per_step.setValue(5)
        self.measurement_settings_layout.addWidget(self.measurements_per_step, 5, 1)

        self.measurement_settings_layout.addWidget(QLabel('Limit Current [uA]'), 6, 0)  #Limit Current SpinBox and Label
        self.limitI = QDoubleSpinBox()
        self.limitI.setRange(0, 1e6)
        self.limitI.setDecimals(2)
        self.limitI.setSuffix(' uA')
        self.limitI.setValue(10)
        self.measurement_settings_layout.addWidget(self.limitI, 6, 1)

        self.measurement_settings_layout.addWidget(QLabel('Use constant voltage'), 7, 0) #Constant Voltage CheckBox and Label
        self.fixed_voltage_checkBox = QCheckBox()
        self.fixed_voltage_checkBox.stateChanged.connect(self.logic.enable_fixed_voltage)
        self.measurement_settings_layout.addWidget(self.fixed_voltage_checkBox, 7, 1)

        self.measurement_settings_layout.addWidget(QLabel('Constant voltage [V]'), 8, 0)  #Fixed Voltage SpinBox and Label
        self.fixed_voltage = QDoubleSpinBox()
        self.fixed_voltage.setRange(-1100, 1100)
        self.fixed_voltage.setDecimals(2)
        self.fixed_voltage.setSuffix(' V')
        self.fixed_voltage.setValue(0)
        self.measurement_settings_layout.addWidget(self.fixed_voltage, 8, 1)
        self.fixed_voltage.setEnabled(False)

        self.use_custom_sweep_label = QLabel('Use custom sweep file') #Custom Sweep CheckBox and Label
        self.measurement_settings_layout.addWidget(self.use_custom_sweep_label, 10, 0)
        self.use_custom_sweep_checkBox = QCheckBox()
        self.measurement_settings_layout.addWidget(self.use_custom_sweep_checkBox, 10, 1)
        self.use_custom_sweep_checkBox.stateChanged.connect(self.logic.enable_custom_sweep)
        self.use_custom_sweep_label.setToolTip('The sweep file should be a csv file with the first column containing the voltages  '
        '\nand the second column containing the number of measurements at each voltage')

        self.custom_sweep_file = QLineEdit()   #Path to the custom sweep file
        self.measurement_settings_layout.addWidget(self.custom_sweep_file, 11, 0, 1, 2)
        self.custom_sweep_file.setEnabled(False)
        self.custom_sweep_file.setPlaceholderText('Enter path to sweep file')

        line = QFrame()   #Line to visaully separate the settings from the filename
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.measurement_settings_layout.addWidget(line, 12, 0)

        self.measurement_settings_layout.addWidget(QLabel('Select a file path and filename for the data'), 13, 0) #Title for the file path and filename

        self.folder_path = QLineEdit()    #Folder path for the data
        self.measurement_settings_layout.addWidget(self.folder_path, 14, 0)
        self.folder_path.setText('IVVMaker/data')

        self.search_folder_path = QPushButton('...')   #Button to select the folder path
        self.search_folder_path.clicked.connect(self.logic.select_folder)
        self.measurement_settings_layout.addWidget(self.search_folder_path, 14, 1   )

        self.filename = QLineEdit() #Filename for the datafile
        self.filename.setPlaceholderText('Enter filename')
        self.measurement_settings_layout.addWidget(self.filename, 15, 0)

        self.filename_suffix = QComboBox()   #Select the file suffix (default is .csv)
        self.filename_suffix.addItems(['.csv', '.dat', '.txt'])
        self.filename_suffix.setCurrentIndex(0)
        self.measurement_settings_layout.addWidget(self.filename_suffix, 15, 1)

        self.measurement_settings_box.setLayout(self.measurement_settings_layout)  #Add the layout to the group box
        self.layout.addWidget(self.measurement_settings_box, 3, 0, 3, 1)
        
        self.canvas = Plotting.PlotCanvas(self)     #Initialize the plot canvas
        self.layout.addWidget(self.canvas, 0, 1, 5, 3)

        self.canvas_settings = QGroupBox('Plot settings')    #Create a group box for the plot settings
        self.canvas_settings_layout = QGridLayout()
        self.canvas_settings_layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.addWidget(self.canvas_settings, 5, 1, 1, 3)

        self.canvas_custom_limits = QCheckBox()    #Custom Limits CheckBox and Label
        self.canvas_custom_limits.setChecked(False)
        self.canvas_settings_layout.addWidget(self.canvas_custom_limits, 0, 1)
        self.canvas_custom_limits.stateChanged.connect(self.logic.enable_custom_limits)
        self.canvas_settings_layout.addWidget(QLabel('Use custom limits in the plot'), 0, 0)

        self.canvas_clear_button = QPushButton('Clear plot')    #Clear Plot Button (Clears the plot and old data, if meausrement is running, the live data is not cleared)
        self.canvas_clear_button.clicked.connect(self.canvas.clear_plot)
        self.canvas_settings_layout.addWidget(self.canvas_clear_button, 0, 5)

        self.canvas_xlimits_label = QLabel('Voltage limits')      #Limits of the x axis, default is voltage, switches to seconds if constant voltage is enabled
        self.canvas_settings_layout.addWidget(self.canvas_xlimits_label, 1, 0)
        self.canvas_lower_x_limit = QDoubleSpinBox()
        self.canvas_lower_x_limit.setRange(-1100, 1100)
        self.canvas_lower_x_limit.setDecimals(2)
        self.canvas_lower_x_limit.setSuffix(' V')
        self.canvas_lower_x_limit.setValue(self.startV.value())
        self.canvas_settings_layout.addWidget(self.canvas_lower_x_limit, 1, 1)
        self.canvas_settings_layout.addWidget(QLabel('to'), 1, 2)
        self.canvas_upper_x_limit = QDoubleSpinBox()
        self.canvas_upper_x_limit.setRange(-1100, 1100)
        self.canvas_upper_x_limit.setDecimals(2)
        self.canvas_upper_x_limit.setSuffix(' V')
        self.canvas_upper_x_limit.setValue(self.stopV.value())
        self.canvas_settings_layout.addWidget(self.canvas_upper_x_limit, 1, 3)

        self.canvas_settings_layout.addWidget(QLabel('Current limits'), 2, 0)  #Limit for the y axis, default is current, maybe implement a second y axis for additional voltage measurements later
        self.canvas_lower_y_limit = QDoubleSpinBox()
        self.canvas_lower_y_limit.setRange(-1e6, 1e6)
        self.canvas_lower_y_limit.setDecimals(2)
        self.canvas_lower_y_limit.setSuffix(' uA')
        self.canvas_lower_y_limit.setValue(0)
        self.canvas_settings_layout.addWidget(self.canvas_lower_y_limit, 2, 1)
        self.canvas_settings_layout.addWidget(QLabel('to'), 2, 2)
        self.canvas_upper_y_limit = QDoubleSpinBox()
        self.canvas_upper_y_limit.setRange(-1e6, 1e6)
        self.canvas_upper_y_limit.setDecimals(2)
        self.canvas_upper_y_limit.setSuffix(' uA')
        self.canvas_upper_y_limit.setValue(-self.limitI.value())
        self.canvas_settings_layout.addWidget(self.canvas_upper_y_limit, 2, 3)

        self.canvas_lower_x_limit.setEnabled(False)  #Disable the limits until the user checks the box
        self.canvas_upper_x_limit.setEnabled(False)
        self.canvas_lower_y_limit.setEnabled(False)
        self.canvas_upper_y_limit.setEnabled(False)

        self.canvas_lower_x_limit.editingFinished.connect(self.logic.set_custom_limits)  #Connects the limits to the logic function
        self.canvas_upper_x_limit.editingFinished.connect(self.logic.set_custom_limits)
        self.canvas_lower_y_limit.editingFinished.connect(self.logic.set_custom_limits)
        self.canvas_upper_y_limit.editingFinished.connect(self.logic.set_custom_limits)

        self.canvas_settings_layout.addWidget(line, 3, 0, 1, 5)
        self.canvas_settings_layout.addWidget(QLabel('Add a previous measurement to the plot'), 4, 0)   #Title for the option to plot old measurements 
        
        self.select_canvas_file = QLineEdit()     #Path to the file to be plotted
        self.select_canvas_file.setPlaceholderText('Select file')
        self.canvas_settings_layout.addWidget(self.select_canvas_file, 5, 0, 1, 4)

        self.search_canvas_file = QPushButton('...') #Button to select the file to be plotted
        self.search_canvas_file.clicked.connect(self.logic.select_canvas_file)
        self.canvas_settings_layout.addWidget(self.search_canvas_file, 5, 4, 1, 1)

        self.canvas_load_file = QPushButton('Load file') #Button to load the file to be plotted
        self.canvas_load_file.clicked.connect(self.logic.load_canvas_file)
        self.canvas_settings_layout.addWidget(self.canvas_load_file, 5, 5, 1, 1)

        self.canvas_settings.setLayout(self.canvas_settings_layout)  #Add the layout to the group box

        self.start_button = QPushButton('Start Measurement') #Button to start the measurement 
        self.start_button.clicked.connect(self.logic.start_measurement)
        self.layout.addWidget(self.start_button, 6, 0, 1, 3)   

        self.abort_button = QPushButton('Abort Measurment') #Button to abort/stop the measurement
        self.abort_button.clicked.connect(lambda: self.logic.abort_measurement('Manually aborted'))
        self.layout.addWidget(self.abort_button, 6, 3, 1, 1)
        self.abort_button.setEnabled(False)

    def closeEvent(self, event): # Ask the user if they want to quit
        # If the user wants to quit, close all devices and quit the application
        # If the user does not want to quit, ignore the event
        # This is a standard close event for PyQt5 applications
        reply = QMessageBox.question(self, 'Quit?', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            for device in self.device_handler.smu_devices:
                device.close()
            for device in self.device_handler.voltmeter_devices:
                device.close()
            for device in self.device_handler.resistancemeter_devices:
                device.close()  
            for device in self.device_handler.lowV_devices:
                device.close()
        else:
            event.ignore()
