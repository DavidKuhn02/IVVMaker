from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QGridLayout, QFormLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, QScrollArea, QFrame, QVBoxLayout, QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton, QSizePolicy
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import QThread, pyqtSignal
import pyvisa as visa
import devices
import plotting
from logic import Functionality, Device_Handler
from config_manager import config_manager
import os 

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') #Path to the data folder
if not os.path.exists(data_path): #Create the data folder if it does not exist
    os.makedirs(data_path)


class Ui_MainWindow(QWidget):
    def __init__(self, rm):
        super().__init__()
        self.rm = rm
        self.IV_settings = { # Dict to store the settings for the IV measurement
        'startV': 0,
        'stopV': 0,
        'stepV': 0,
        'time_between_steps': 0,
        'time_between_measurements': 0,
        'measurements_per_step': 0,
        'limitI': 0,
        'custom_sweep': False,
        'custom_sweep_file': '',
        }
        self.constantV_settings = { # Dict to store the settings for the constant voltage measurement
            'constant_voltage': 0,
            'time_between_measurements': 0,
            'limitI': 0,
        }
        self.CV_settings = { # Dict to store the settings for the CV measurement
            'startV': 0,
            'stopV': 0,
            'stepV': 0,
            'startFrequency': 0,
            'stopFrequency': 0,
            'number_of_frequencies': 0,
            'logarithmic_frequency_steps': True,
            'time_between_steps': 0,
            'time_between_measurements': 0,
            'measurements_per_step': 0,
            'limitI': 0,
            'custom_sweep': False,
            'custom_sweep_file': '',
        }
        self.logic = Functionality(self)
        self.canvas = plotting.PlotCanvas(self) # Initialize the plot canvas
        self.measurement_type = 'IV'  # Default measurement type
        self.data_path = data_path # Default data path
        self.setup_ui()
        self.logic.openEvent()



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
        self.measurement_settings_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.measurement_settings_layout.setColumnStretch(0, 1)

        self.measurement_type_comboBox = QComboBox()  #Select Measurement Type ComboBox
        self.measurement_type_comboBox.addItems(['IV', 'Constant Voltage', 'CV']) 
        self.measurement_type_comboBox.setToolTip('Select the measurement type\n IV for a current-voltage measurement\n Constant Voltage for a current measurement with constant voltage \n CV for a capacitance-voltage measurement')   
        self.measurement_type_comboBox.setCurrentText(self.measurement_type)
        self.measurement_type_comboBox.currentTextChanged.connect(lambda: self.logic.change_measurement_type(self.measurement_type_comboBox.currentText())) #Connects the ComboBox to the logic function
        self.measurement_settings_layout.addWidget(QLabel('Select Measurement Type'), 0, 0)
        self.measurement_settings_layout.addWidget(self.measurement_type_comboBox, 0, 1) #Add the ComboBox to the layout

        self.measurement_settings = QWidget()  #Creates a widget for the measurement settings
        self.measurement_settings.setLayout(self.changeUI_IV())
        #Sets the layout of the widget to the IV settings by default
        self.measurement_settings_scrollArea = QScrollArea()
        self.measurement_settings_scrollArea.setWidget(self.measurement_settings)
        self.measurement_settings_scrollArea.setWidgetResizable(True)
        self.measurement_settings_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn) #Always show the vertical scroll bar
        self.measurement_settings_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.measurement_settings_scrollArea.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding) #Set the size policy of the scroll area
        self.measurement_settings_scrollArea.setMinimumSize(300, 300) #Sets the minimum size of the scroll area
        self.measurement_settings_layout.addWidget(self.measurement_settings_scrollArea, 1, 0, 1, 2) #Add the widget to the layout

        self.measurement_settings_box.setLayout(self.measurement_settings_layout)  #Add the layout to the group box
        self.layout.addWidget(self.measurement_settings_box, 3, 0, 2, 1)

        self.savefile_settings_box = QGroupBox('Savefile Settings') #Creates a group box for the savefile settings
        self.savefile_settings_box.setMaximumWidth(600)
        self.savefile_settings_layout = QGridLayout()
        self.savefile_settings_layout.setAlignment(QtCore.Qt.AlignTop)

        self.folder_path = QLineEdit()    #Folder path for the data
        self.savefile_settings_layout.addWidget(self.folder_path, 0, 0, 1, 2)
        self.folder_path.setText(data_path) #Default path is the current working directory /data

        self.search_folder_path = QPushButton('...')   #Button to select the folder path
        self.search_folder_path.clicked.connect(self.logic.select_folder)
        self.savefile_settings_layout.addWidget(self.search_folder_path, 0, 2)

        self.filename = QLineEdit() #Filename for the datafile
        self.filename.setPlaceholderText('Enter filename')
        self.savefile_settings_layout.addWidget(self.filename, 1, 0)

        self.use_timestamp_checkBox = QCheckBox('Timestamp')  #Checkbox to use a timestamp in the filename
        self.use_timestamp_checkBox.setChecked(True)
        self.use_timestamp_checkBox.setToolTip('If checked, the filename will include a timestamp')
        self.savefile_settings_layout.addWidget(self.use_timestamp_checkBox, 1, 1)

        self.filename_suffix = QComboBox()   #Select the file suffix (default is .csv)
        self.filename_suffix.addItems(['.csv', '.dat', '.txt'])
        self.filename_suffix.setCurrentIndex(0)
        self.savefile_settings_layout.addWidget(self.filename_suffix, 1, 2)

        self.savefile_settings_box.setLayout(self.savefile_settings_layout)
        self.layout.addWidget(self.savefile_settings_box, 5, 0, 1, 1) #Add the group box to the layout

            #Initialize the plot canvas
        self.layout.addWidget(self.canvas, 0, 1, 5, 3)

        self.toolbar = NavigationToolbar(self.canvas, self)  # Create the toolbar
        self.layout.addWidget(self.toolbar, 5, 1, 1, 2)  # Add it below the plot

        self.canvas_settings = QWidget()    #Create a group box for the plot settings
        self.canvas_settings.setLayout(self.canvas_settings_UI())  #Add the layout to the group box
        self.layout.addWidget(self.canvas_settings, 5, 3, 2, 1) #Add the group box to the layout

        self.start_button = QPushButton('Start Measurement') #Button to start the measurement 
        self.start_button.clicked.connect(self.logic.start_measurement)
        self.layout.addWidget(self.start_button, 6, 1, 3, 2)   
        self.start_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_button.setStyleSheet("""
                                            QPushButton {
                                                font-weight: bold;
                                                font-size: 22px;
                                                border: 2px solid green;
                                                border-radius: 5px;
                                                padding: 5px;
                                            }
                                        """)

        self.abort_button = QPushButton('Abort Measurment') #Button to abort/stop the measurement
        self.abort_button.clicked.connect(lambda: self.logic.abort_measurement('Manually aborted'))
        self.layout.addWidget(self.abort_button, 6, 3, 3, 1)
        self.abort_button.setEnabled(False)
        self.abort_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.abort_button.setStyleSheet("""
                                            QPushButton {
                                                font-weight: bold;
                                                font-size: 22px;
                                                border: 2px solid red;
                                                border-radius: 5px;
                                                padding: 5px;
                                            }
                                        """)

        self.save_config_button = QPushButton('Save Config') #Button to save the config
        self.save_config_button.clicked.connect(self.logic.save_config)
        self.layout.addWidget(self.save_config_button, 6, 0, 1, 1)

        self.load_config_button = QPushButton('Load Config') #Button to load the config
        self.load_config_button.clicked.connect(self.logic.load_config)
        self.layout.addWidget(self.load_config_button, 7, 0, 1, 1)

        self.switch_darkmode = QPushButton('Toggle darkmode')
        self.switch_darkmode.clicked.connect(self.logic.switch_darkmode)
        self.layout.addWidget(self.switch_darkmode, 8, 0, 1, 1)

    def closeEvent(self, event): # Ask the user if they want to quit
        # If the user wants to quit, close all devices and quit the application
        # If the user does not want to quit, ignore the event
        # This is a standard close event for PyQt5 applications
        reply = QMessageBox.question(self, 'Quit?', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logic.closeEvent()
            event.accept()
        else:
            event.ignore()

    def changeUI_IV(self):
        # Function to change the UI to the IV measurement
        outer_layout = QVBoxLayout()  #This is needed to align the settings to the top of the box
        outer_layout.setAlignment(QtCore.Qt.AlignTop)
        outer_layout.setAlignment(QtCore.Qt.AlignLeft)

        layout = QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        self.startV_spinBox = QDoubleSpinBox()
        self.startV_spinBox.setRange(-1100, 1100)
        self.startV_spinBox.setDecimals(2)
        self.startV_spinBox.setSuffix(' V')
        layout.addWidget(QLabel('Start Voltage [V]'), 0, 0)
        layout.addWidget(self.startV_spinBox, 0, 1)

        self.stopV_spinBox = QDoubleSpinBox()
        self.stopV_spinBox.setRange(-1100, 1100)
        self.stopV_spinBox.setDecimals(2)
        self.stopV_spinBox.setSuffix(' V')
        layout.addWidget(QLabel('Stop Voltage [V]'), 1, 0)
        layout.addWidget(self.stopV_spinBox, 1, 1)

        self.stepV_spinBox = QDoubleSpinBox()
        self.stepV_spinBox.setRange(-1100, 1100)
        self.stepV_spinBox.setDecimals(2)
        self.stepV_spinBox.setSuffix(' V')
        layout.addWidget(QLabel('Step Voltage [V]'), 2, 0)
        layout.addWidget(self.stepV_spinBox, 2, 1)

        self.time_between_steps_spinBox = QDoubleSpinBox()
        self.time_between_steps_spinBox.setRange(0, 1000)
        self.time_between_steps_spinBox.setDecimals(2)
        self.time_between_steps_spinBox.setSuffix(' s')
        layout.addWidget(QLabel('Time between steps [s]'), 3, 0)
        layout.addWidget(self.time_between_steps_spinBox, 3, 1)

        self.time_between_measurements_spinBox = QDoubleSpinBox()
        self.time_between_measurements_spinBox.setRange(0, 1000)
        self.time_between_measurements_spinBox.setDecimals(2)
        self.time_between_measurements_spinBox.setSuffix(' s')
        layout.addWidget(QLabel('Time between measurements [s]'), 4, 0)
        layout.addWidget(self.time_between_measurements_spinBox, 4, 1)

        self.measurements_per_step_spinBox = QSpinBox()
        self.measurements_per_step_spinBox.setRange(1, 1000)
        layout.addWidget(QLabel('Number of measurements per step'), 5, 0)
        layout.addWidget(self.measurements_per_step_spinBox, 5, 1)

        self.limitI_spinBox = QDoubleSpinBox()
        self.limitI_spinBox.setRange(0, 1e6)
        self.limitI_spinBox.setDecimals(2)
        self.limitI_spinBox.setSuffix(' uA')
        layout.addWidget(QLabel('Current limit [uA]'), 6, 0)
        layout.addWidget(self.limitI_spinBox, 6, 1)

        self.use_custom_sweep_checkBox = QCheckBox()
        self.use_custom_sweep_checkBox.stateChanged.connect(self.logic.enable_custom_sweep)
        self.use_custom_sweep_checkBox.setToolTip(
            'The sweep file should be a csv file with the first column containing the voltages\n'
            'and the second column containing the number of measurements at each voltage'
        )
        layout.addWidget(QLabel('Use custom sweep file for sweep'), 7, 0)
        layout.addWidget(self.use_custom_sweep_checkBox, 7, 1)

        self.custom_sweep_file = QLineEdit()
        self.custom_sweep_file.setEnabled(False)
        self.custom_sweep_file.setPlaceholderText('Enter path to sweep file')
        layout.addWidget(self.custom_sweep_file, 8, 0, 1, 2)

        outer_layout.addLayout(layout)
        outer_layout.setAlignment(QtCore.Qt.AlignTop)
        outer_layout.setAlignment(QtCore.Qt.AlignLeft)
        
        return outer_layout

    def changeUI_ConstantVoltage(self): 
        # Function to change the UI to the Constant Voltage measurement
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(QtCore.Qt.AlignTop)
        outer_layout.setAlignment(QtCore.Qt.AlignLeft)

        layout = QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        self.constant_voltage_spinBox = QDoubleSpinBox()
        self.constant_voltage_spinBox.setRange(-1100, 1100)
        self.constant_voltage_spinBox.setDecimals(2)
        self.constant_voltage_spinBox.setSuffix(' V')
        layout.addWidget(QLabel('Constant Voltage [V]'), 0, 0)
        layout.addWidget(self.constant_voltage_spinBox, 0, 1)

        self.time_between_measurements_spinBox = QDoubleSpinBox()
        self.time_between_measurements_spinBox.setRange(0, 1000)
        self.time_between_measurements_spinBox.setDecimals(2)
        self.time_between_measurements_spinBox.setSuffix(' s')
        layout.addWidget(QLabel('Time between measurements [s]'), 1, 0)
        layout.addWidget(self.time_between_measurements_spinBox, 1, 1)

        self.limitI_spinBox = QDoubleSpinBox()
        self.limitI_spinBox.setRange(0, 1e6)
        self.limitI_spinBox.setDecimals(2)
        self.limitI_spinBox.setSuffix(' uA')
        layout.addWidget(QLabel('Current limit [uA]'), 2, 0)
        layout.addWidget(self.limitI_spinBox, 2, 1)

        outer_layout.addLayout(layout)
        outer_layout.setAlignment(QtCore.Qt.AlignTop)

        return outer_layout
    
    def changeUI_CV(self):
        # Function to change the UI to the CV measurement
        outer_layout = QVBoxLayout()
        
        layout = QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        self.startV_spinBox = QDoubleSpinBox()
        self.startV_spinBox.setRange(-1100, 1100)
        self.startV_spinBox.setDecimals(2)
        self.startV_spinBox.setSuffix(' V')
        layout.addWidget(QLabel('Start Voltage [V]'), 0, 0)
        layout.addWidget(self.startV_spinBox, 0, 1)

        self.stopV_spinBox = QDoubleSpinBox()
        self.stopV_spinBox.setRange(-1100, 1100)
        self.stopV_spinBox.setDecimals(2)
        self.stopV_spinBox.setSuffix(' V')
        layout.addWidget(QLabel('Stop Voltage [V]'), 1, 0)
        layout.addWidget(self.stopV_spinBox, 1, 1)

        self.stepV_spinBox = QDoubleSpinBox()
        self.stepV_spinBox.setRange(-1100, 1100)
        self.stepV_spinBox.setDecimals(2)
        self.stepV_spinBox.setSuffix(' V')
        layout.addWidget(QLabel('Step Voltage [V]'), 2, 0)
        layout.addWidget(self.stepV_spinBox, 2, 1)

        self.start_frequency_spinBox = QDoubleSpinBox()
        self.start_frequency_spinBox.setRange(20, 200e3)
        self.start_frequency_spinBox.setDecimals(0)
        self.start_frequency_spinBox.setSuffix(' Hz')
        layout.addWidget(QLabel('Start Frequency [Hz]'), 3, 0)
        layout.addWidget(self.start_frequency_spinBox, 3, 1)

        self.stop_frequency_spinBox = QDoubleSpinBox()
        self.stop_frequency_spinBox.setRange(20, 200e3)
        self.stop_frequency_spinBox.setDecimals(0)
        self.stop_frequency_spinBox.setSuffix(' Hz')
        layout.addWidget(QLabel('Stop Frequency [Hz]'), 4, 0)
        layout.addWidget(self.stop_frequency_spinBox, 4, 1)

        self.number_of_frequencies_spinBox = QSpinBox()
        self.number_of_frequencies_spinBox.setRange(1, 69)
        layout.addWidget(QLabel('Number of Frequencies'), 5, 0)
        layout.addWidget(self.number_of_frequencies_spinBox, 5, 1)

        self.logarithmic_frequency_steps_checkBox = QCheckBox()
        self.logarithmic_frequency_steps_checkBox.setChecked(True)
        self.logarithmic_frequency_steps_checkBox.setToolTip('If checked, the frequency steps will be logarithmic')
        layout.addWidget(QLabel('Logarithmic Frequency Steps'), 6, 0)
        layout.addWidget(self.logarithmic_frequency_steps_checkBox, 6, 1)

        self.time_between_steps_spinBox = QDoubleSpinBox()
        self.time_between_steps_spinBox.setRange(0, 1000)
        self.time_between_steps_spinBox.setDecimals(2)
        self.time_between_steps_spinBox.setSuffix(' s')
        layout.addWidget(QLabel('Time between steps [s]'), 7, 0)
        layout.addWidget(self.time_between_steps_spinBox, 7, 1)

        self.time_between_measurements_spinBox = QDoubleSpinBox()
        self.time_between_measurements_spinBox.setRange(0, 1000)
        self.time_between_measurements_spinBox.setDecimals(2)
        self.time_between_measurements_spinBox.setSuffix(' s')
        layout.addWidget(QLabel('Time between measurements [s]'), 8, 0)
        layout.addWidget(self.time_between_measurements_spinBox, 8, 1)

        self.measurements_per_step_spinBox = QSpinBox()
        self.measurements_per_step_spinBox.setRange(1, 1000)
        layout.addWidget(QLabel('Number of measurements per step'), 9, 0)
        layout.addWidget(self.measurements_per_step_spinBox, 9, 1)

        self.limitI_spinBox = QDoubleSpinBox()
        self.limitI_spinBox.setRange(0, 1e6)
        self.limitI_spinBox.setDecimals(2)
        self.limitI_spinBox.setSuffix(' uA')
        layout.addWidget(QLabel('Current limit [uA]'), 10, 0)
        layout.addWidget(self.limitI_spinBox, 10, 1)

        self.use_custom_sweep_checkBox = QCheckBox()
        self.use_custom_sweep_checkBox.stateChanged.connect(self.logic.enable_custom_sweep)
        self.use_custom_sweep_checkBox.setToolTip(
            'The sweep file should be a csv file with the first column containing the voltages\n'
            'and the second column containing the number of measurements at each voltage'
        )
        layout.addWidget(QLabel('Use custom sweep file for sweep'), 11, 0)
        layout.addWidget(self.use_custom_sweep_checkBox, 11, 1)

        self.custom_sweep_file = QLineEdit()
        self.custom_sweep_file.setEnabled(False)
        self.custom_sweep_file.setPlaceholderText('Enter path to sweep file')
        layout.addWidget(self.custom_sweep_file, 12, 0, 1, 2)

        outer_layout.addLayout(layout)
        outer_layout.setAlignment(QtCore.Qt.AlignTop)
        outer_layout.setAlignment(QtCore.Qt.AlignLeft)

        return outer_layout
    
    def canvas_settings_UI(self):
        layout = QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        self.clear_data_button = QPushButton('Clear Old Data') #Button to clear the live data
        self.clear_data_button.clicked.connect(self.canvas.clear_old_data)
        layout.addWidget(self.clear_data_button, 0, 0)

        self.load_data_button = QPushButton('Load Old Data') #Button to load data from a file        
        self.load_data_button.clicked.connect(self.canvas.load_old_data)
        layout.addWidget(self.load_data_button, 1, 0)

        self.live_current_label = QLabel('Live Current:')
        layout.addWidget(self.live_current_label, 0, 1)

        self.live_voltage_label = QLabel('Live Voltage:')
        layout.addWidget(self.live_voltage_label, 1, 1)

        self.live_current_data = QLabel('0 nA')
        layout.addWidget(self.live_current_data, 0, 2)

        self.live_voltage_data = QLabel('0 V')
        layout.addWidget(self.live_voltage_data, 1, 2)

        return layout