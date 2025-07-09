#This file includes the functionality of the GUI and the device handling. Also the data saving class is included here.
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, QScrollArea, QFrame, QVBoxLayout, QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
import measurement_thread
import parameter_dialog
import devices
import data_handler
import config_manager
from device_handling import Device_Handler 
import numpy as np
import json
import os
from datetime import datetime 
import qdarkstyle



class Functionality:
    def __init__(self, ui):
        self.ui = ui
        self.darkmode = False
        self.config_manager = config_manager.config_manager(self.ui)
        self.open_parameter_dialogs = [] #List of open parameter dialogs, to be closed when the measurement is started
        self.device_handler = Device_Handler(self.ui.rm)  # Create the device handler object

    def openEvent(self):
        #This is called at the start of the program and sets up the UI
        config = self.config_manager.load_config(os.path.join(os.path.dirname(__file__), 'config', 'latest.json')) #Loads the latest config file (created on closing the program)
        self.change_measurement_type(type = config['measurement_type'] ,config = config) #Set the measurement type to the one in the config file for the UI to load properly

    def closeEvent(self):
        #This function is called when the program is closed and saves the current settings to a config file
        #It also closes all devices 
        for device in self.device_handler.smu_devices:
            device.close()
        for device in self.device_handler.voltmeter_devices:
            device.close()  
        for device in self.device_handler.lowV_devices:
            device.close()
        self.update_measurement_settings()
        config = self.config_manager.assemble_config()
        self.config_manager.save_config(config, os.path.join(os.path.dirname(__file__), 'config', 'latest.json'))

    def switch_darkmode(self):
        #This function switches the dark mode on and off (just for fun and my eyes in a dark lab)
        app = QApplication.instance()
        self.darkmode = not self.darkmode
        if self.darkmode:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet("")

    def update_darkmode(self):
        #This function updates the dark mode when the program is started
        app = QApplication.instance()
        if self.darkmode:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet("")

    def refresh_devices(self):
        #This function refreshes the list of available devices and adds them to the device handler
        self.device_handler.find_devices()
        self.ui.select_decive.clear()
        self.ui.select_decive.addItem('Select Device')
        for device in self.device_handler.device_candidates:
            self.ui.select_decive.addItem(device[2] + ', ID: '+ device[1])

    def add_device_entry(self): 
        #This function adds the selected device into the device handler and creates a widget for it
        index = self.ui.select_decive.currentIndex()  #Check the index that is selected in the list of available devices
        if index == 0:  # If the first entry is selected, it means no device is selected
            print('No device selected')
            return
        else:
            self.ui.select_decive.removeItem(index)  #Remove the selected device from the list of available devices
            self.ui.select_decive.setCurrentIndex(0) #Set the current index to 0 to be able to select another device
            candidate = self.device_handler.device_candidates[index-1] #Select the right device from the list of candidates (index shifts by 1 because of the default entry)
            self.device_handler.device_candidates.remove(candidate) #Remove the selected device from the list of candidates
            self.device_handler.used_ids.append(candidate[1]) #Add the selected device to the list of used ids to not be able to select it again
            if 'Keithley K2200 SMU' in candidate[2]: # Check the type of the device and create the respective object 
                device = devices.K2200(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
                self.K2200_warning()
            elif 'Keithley K2400 SMU' in candidate[2]:
                device = devices.K2400(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
            elif 'Keithley K2600 SMU' in candidate[2]:
                device = devices.K2600(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
            elif 'Keithley K6487 SMU' in candidate[2]:
                device = devices.K6487(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
            elif 'Keithley K2000 Voltmeter' in candidate[2]:
                device = devices.K2000(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.voltmeter_devices.append(device)
            elif 'Rhode&Schwarz NGE103B' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.lowV_devices.append(device)
            elif 'HAMEG HMP4040' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.lowV_devices.append(device)
            elif 'HAMEG HM8118' in candidate[2]:
                device = devices.Hameg8118(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.capacitancemeter_devices.append(device)
            elif 'Dummy' in candidate[2]: #For testing purposes 
                device = devices.Dummy_Device(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
            else:
                print('Device not supported')
                return 
            widget = self.create_device_widget(candidate, device) #create the widget for the device
            self.ui.device_widgets.append(widget)
            self.ui.device_scrollLayout.addWidget(widget) # Add the device to the scroll area

    def add_all_devices(self):
        #This functions combines the refresh and add device functions to add all connected devices at once. DO NOT USE if you have a lot of devices connected, you will loose the overview of the devices 
        self.device_handler.find_devices()
        self.ui.select_decive.clear()
        self.ui.select_decive.addItem('Select Device')
        for candidate in self.device_handler.device_candidates:
            self.device_handler.used_ids.append(candidate[1])
            if 'Keithley K2200 SMU' in candidate[2]: # Check the type of the device and create the respective object 
                device = devices.K2200(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
                self.K2200_warning()
            elif 'Keithley K2400 SMU' in candidate[2]:
                device = devices.K2400(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
            elif 'Keithley K2600 SMU' in candidate[2]:
                device = devices.K2600(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
            elif 'Keithley K6487 SMU' in candidate[2]:
                device = devices.K6487(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.smu_devices.append(device)
            elif 'Keithley K2000 Voltmeter' in candidate[2]:
                device = devices.K2000(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.voltmeter_devices.append(device)
            elif 'Rhode&Schwarz NGE103B' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.lowV_devices.append(device)
            elif 'HAMEG HMP4040' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.device_handler.lowV_devices.append(device)
            elif 'Dummy' in candidate[2]: #For testing purposes 
                device = devices.Dummy_Device(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
            else:
                print('Device not supported')
                return 
            widget = self.create_device_widget(candidate, device) #create the widget for the device
            self.ui.device_widgets.append(widget) # Adds the widget to the list of device widgets
            self.ui.device_scrollLayout.addWidget(widget) # Add the widget to the scroll area

    def create_device_widget(self, candidate, device):
        #This function creates the widget for the device and adds it to the scroll area
        #The widget contains the ID of the device, a reset button, a clear buffer button and a remove button
        #The widget is a QFrame with a QGridLayout
        device_widget = QFrame()
        device_widget.setFrameShape(QFrame.Box)
        device_layout = QGridLayout()
        
        device_layout.addWidget(QLabel(candidate[1]), 0, 0, 1, 3)  #Add the ID to the Layout
    
        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(lambda : self.reset_device(device))
        device_layout.addWidget(reset_button, 1, 0)
        clear_buffer_button = QPushButton('Clear Buffer')
        clear_buffer_button.clicked.connect(lambda : self.clear_buffer(device))
        device_layout.addWidget(clear_buffer_button, 1, 1)
        close_button = QPushButton('Remove')
        close_button.clicked.connect(lambda : self.remove_device(device, candidate[1], device_widget))
        device_layout.addWidget(close_button, 1, 2)
        if candidate[2] == 'Keithley K2000 Voltmeter':  # Add the pop up window to allow for advanced settings for the Keithley K2200 SMUs
            advanced_settings = QPushButton('Advanced Settings')
            advanced_settings.clicked.connect(lambda : self.open_parameter_dialog(device, candidate[1], candidate[2]))
            device_layout.addWidget(advanced_settings, 2, 0, 1, 3)
        if candidate[2] == 'Keithley K2400 SMU':  # Add the pop up window to allow for advanced settings for the Keithley K2400 SMUs
            advanced_settings = QPushButton('Advanced Settings')
            advanced_settings.clicked.connect(lambda : self.open_parameter_dialog(device, candidate[1], candidate[2]))
            device_layout.addWidget(advanced_settings, 2, 0, 1, 3)
        if candidate[2] == 'Keithley K2600 SMU':  # Add the pop up window to allow for advanced settings for the Keithley K2600 SMUs
            advanced_settings = QPushButton('Advanced Settings')
            advanced_settings.clicked.connect(lambda : self.open_parameter_dialog(device, candidate[1], candidate[2]))
            device_layout.addWidget(advanced_settings, 2, 0, 1, 3)
        
        device_widget.setLayout(device_layout) 
        return device_widget

    def open_parameter_dialog(self, device, id, type):
        #This function opens the parameter dialog for the device
        #It is used to set the parameters for the device, like voltage range, current range, etc.
        if type == 'Keithley K2000 Voltmeter':
            dialog = parameter_dialog.ParameterDialog_K2000(device, id, self.ui.rm, self)
            dialog.show()
            self.open_parameter_dialogs.append(dialog)
        if type == 'Keithley K2400 SMU':
            dialog = parameter_dialog.ParameterDiaglog_K2400(device, id, self.ui.rm, self)
            dialog.show()
            self.open_parameter_dialogs.append(dialog)
        if type == 'Keithley K2600 SMU':
            dialog = parameter_dialog.ParameterDialog_K2600(device, id, self.ui.rm, self)
            dialog.show()
            self.open_parameter_dialogs.append(dialog)
        
    def reset_device(self, device): 
        #Function for the device widget to reset the device
        try: 
            device.reset()
        except:
            pass 
    
    def clear_buffer(self, device):
        #Function for the device widget to clear the buffer of the device
        #This is not implemented for all devices, only for the ones that are supported
        try:
            device.clear_buffer()
        except:
            pass

    def remove_device(self, device, id, widget):
        #Function for the device widget to remove the device from the list of used devices
        #Remove the device from the list of used devices and delete the widget, this device can now be selected again
        self.device_handler.used_ids.remove(id)
        if widget in self.ui.device_widgets:
            self.ui.device_widgets.remove(widget)
            widget.deleteLater()
        if device in self.device_handler.smu_devices:
            self.device_handler.smu_devices.remove(device)
        if device in self.device_handler.voltmeter_devices:
            self.device_handler.voltmeter_devices.remove(device)
        if device in self.device_handler.lowV_devices:
            self.device_handler.lowV_devices.remove(device)
        if device in self.device_handler.capacitancemeter_devices:
            self.device_handler.capacitancemeter_devices.remove(device)

        device.close()
        return
     
    def enable_custom_sweep(self):
        #This function enables or disables the custom sweep mode 
        self.ui.custom_sweep = self.ui.use_custom_sweep_checkBox.isChecked()
        self.ui.custom_sweep_file.setEnabled(self.ui.custom_sweep)

    def select_folder(self):
        #This function opens a file dialog to select a folder for the data saving
        #It sets the folder path to the selected folder
        folder = QFileDialog.getExistingDirectory(self.ui, 'Select a Folder')
        if folder:
            self.ui.folder_path.setText(folder)
            return

    def change_measurement_type(self, type, config = None):
        # This function changes the measurement type and updates the UI accordingly. It saves the current settings, so if the user decides to switch back to the previous measurement type, the settings are still there.
        self.update_measurement_settings()
        self.ui.measurement_type = type
        if type == 'IV':
            layout = self.ui.changeUI_IV()
        elif type == 'CV':
            layout = self.ui.changeUI_CV()
        elif type == 'Constant Voltage':
            layout = self.ui.changeUI_ConstantVoltage()
        oldLayout = self.ui.measurement_settings.layout()
        if oldLayout is not None:
            QWidget().setLayout(oldLayout)  # Clear the old layout
        self.ui.measurement_settings.setLayout(layout) #Set the new layout
        if not config:
            config = self.config_manager.assemble_config() #Assemble the config from the UI
        self.config_manager.apply_config(config) #Apply the config to the new layout
        self.ui.canvas.change_plot_type(type) #Change the plot type to the new measurement type
        return

    def K2200_warning(self):
        #This function shows a warning message if the K2200 is selected as a device, as it is not able to apply negative voltages, so the user has to reverse the polarity on the device
        warning = QMessageBox.warning(self.ui, 'Warning', 'Please note that the K2200 is not able to apply negative voltages. To achieve that please physically reverse the polarity on this device.', QMessageBox.Ok, QMessageBox.Ok)

    def ui_changes_start(self): 
        #This function changes the UI when the measurement is started
        self.ui.abort_button.setEnabled(True)
        self.ui.start_button.setEnabled(False)
        self.ui.measurement_settings.setEnabled(False)
        for widget in self.ui.device_widgets:
            widget.setEnabled(False)
        
    def ui_changes_stop(self):
        #This function changes the UI when the measurement is stopped
        self.ui.abort_button.setEnabled(False)
        self.ui.start_button.setEnabled(True)
        self.ui.measurement_settings.setEnabled(True)
        for widget in self.ui.device_widgets:
            widget.setEnabled(True)
    
    def update_measurement_settings(self):
        #This function reads the measurement settings from the UI and updates the measurement settings
        #It is either called when ending the program or when the user clicks the start button
        if self.ui.measurement_type == 'IV':
            try: 
                self.ui.IV_settings = { # Dict to store the settings for the IV measurement
        'startV': self.ui.startV_spinBox.value(),
        'stopV': self.ui.stopV_spinBox.value(),
        'stepV': self.ui.stepV_spinBox.value(),
        'measurements_per_step': self.ui.measurements_per_step_spinBox.value(),
        'time_between_measurements': self.ui.time_between_measurements_spinBox.value(),
        'time_between_steps': self.ui.time_between_steps_spinBox.value(),
        'limitI': self.ui.limitI_spinBox.value(),
        'custom_sweep': self.ui.use_custom_sweep_checkBox.isChecked(),
        'custom_sweep_file': self.ui.custom_sweep_file.text(),
             }
            except Exception as e:
                raise e
                    
        elif self.ui.measurement_type == 'CV':
            try:
                self.ui.CV_settings = { # Dict to store the settings for the CV measurement
        'startV': self.ui.startV_spinBox.value(),
        'stopV': self.ui.stopV_spinBox.value(),
        'stepV': self.ui.stepV_spinBox.value(),
        'startFrequency': self.ui.start_frequency_spinBox.value(),
        'stopFrequency': self.ui.stop_frequency_spinBox.value(),
        'number_of_frequencies': self.ui.number_of_frequencies_spinBox.value(),#
        'logarithmic_frequency_steps': self.ui.logarithmic_frequency_steps_checkBox.isChecked(),
        'time_between_steps': self.ui.time_between_steps_spinBox.value(),
        'time_between_measurements': self.ui.time_between_measurements_spinBox.value(),
        'measurements_per_step': self.ui.measurements_per_step_spinBox.value(),
        'limitI': self.ui.limitI_spinBox.value(),
        'custom_sweep': self.ui.use_custom_sweep_checkBox.isChecked(),
        'custom_sweep_file': self.ui.custom_sweep_file.text(),
            }
            except Exception as e:
                raise e
        elif self.ui.measurement_type == 'Constant Voltage':
            try:
                self.ui.constantV_settings = { # Dict to store the settings for the Constant Voltage measurement
            'constant_voltage': self.ui.constant_voltage_spinBox.value(),
            'time_between_measurements': self.ui.time_between_measurements_spinBox.value(),
            'limitI': self.ui.limitI_spinBox.value(),
            }
            except Exception as e:
                raise e

    def start_measurement(self):
        #This function starts the measurement and creates the data saver object
        #It is called when the user clicks the start button
        self.update_measurement_settings() #Update the measurement settings
        for dialog in self.open_parameter_dialogs:
            dialog.close()
        if self.ui.measurement_type == 'IV': #Choose the parameters based on the measurement type
            parameters = self.ui.IV_settings
        elif self.ui.measurement_type == 'CV':
            parameters = self.ui.CV_settings
        elif self.ui.measurement_type == 'Constant Voltage':
            parameters = self.ui.constantV_settings
        
        if not self.safety_check(parameters = parameters, type = self.ui.measurement_type): #Perform various sanity checks before starting the measurement, mainly to prevent the user from doing things that are not intended
            return

        try:  #try to create the data saver object, if the file already exists, raise an error
            self.data_saver = data_handler.DataSaver(   #start the data save thread 
                filepath = self.ui.folder_path.text(),
                filename = self.ui.filename.text(),
                use_timestamp = self.ui.use_timestamp_checkBox.isChecked(),
                ui = self.ui,
                functionality = self)
            
        except FileExistsError:
            self.file_exists_error()
            return        
        
        self.measurement_thread = measurement_thread.MeasurementThread(ui = self.ui, device_handler= self.device_handler) #Create the measurement thread 
        try:
            self.measurement_thread.finished_signal.disconnect(self.finish_measurement)
        except TypeError:
            pass  # No existing connection, safe to proceed
        
        self.ui.canvas.clear_live_data() #Clear the live data from the plot
        self.ui_changes_start() #Change the UI to show that the measurement is running
        
        if self.ui.measurement_type == 'IV':  #Start IV measurement
            self.write_parameters(self.ui.IV_settings)
            self.measurement_thread.set_parameters('IV', self.ui.IV_settings)
            self.measurement_thread.data_signal.connect(self.receive_data)  #Handles the data signal from the measurement thread
            self.measurement_thread.finished_signal.connect(self.finish_measurement) # Handles the finished signal from the measurement thread
            self.measurement_thread.error_signal.connect(self.abort_measurement) #Handles the error signal from the measurement thread
            self.measurement_thread.start() #Start the measurement thread
        elif self.ui.measurement_type == 'CV': #Start CV measurement
            self.write_parameters(self.ui.CV_settings)
            self.measurement_thread.set_parameters('CV', self.ui.CV_settings)
            self.measurement_thread.data_signal.connect(self.receive_data)  #Handles the data signal from the measurement thread
            self.measurement_thread.finished_signal.connect(self.finish_measurement) # Handles the finished signal from the measurement thread
            self.measurement_thread.error_signal.connect(self.abort_measurement) #Handles the error signal from the measurement thread
            self.measurement_thread.start() #Start the measurement thread
        elif self.ui.measurement_type == 'Constant Voltage': #Start Constant Voltage measurement
            self.write_parameters(self.ui.constantV_settings)
            self.measurement_thread.set_parameters('Constant Voltage', self.ui.constantV_settings) 
            self.measurement_thread.data_signal.connect(self.receive_data)  #Handles the data signal from the measurement thread
            self.measurement_thread.finished_signal.connect(self.finish_measurement) # Handles the finished signal from the measurement thread
            self.measurement_thread.error_signal.connect(self.abort_measurement) #Handles the error signal from the measurement thread
            self.measurement_thread.start() #Start the measurement thread

    def receive_data(self, data):
        self.data_saver.write_data(data)
        self.ui.live_current_data.setText(f'{float(data[2])*1e9:.3f} nA') #Set the live data to the UI
        self.ui.live_voltage_data.setText(f'{float(data[1]):.3f} V')
        
        if self.ui.measurement_type == 'IV' or self.ui.measurement_type == 'Constant Voltage':
            self.ui.canvas.update_data(data[1], data[2]) #update the plot with the new data    
        elif self.ui.measurement_type == 'CV':
            self.ui.canvas.update_cv_data(data[1], data[-1], data[-3], data[-2])
        self.ui.canvas.draw_plot() #draw the plot with the new data

    def file_exists_error(self): #Handles the case when the file already exists
        self.ui.abort_button.setEnabled(False)
        warning = QMessageBox.warning(self.ui, 'Warning', 'Afile with this name already exists, please enter a different filename.', QMessageBox.Ok, QMessageBox.Ok)

    def safety_check(self, parameters=None, type = 'IV'): #This function performs various checks before starting the measurement
        #Check if all connected devices are communicating correctly
        if len(self.device_handler.smu_devices) == 0:
            self.abort_measurement('No SMU connected. Not able to perform a measurement')
            return False

        if type == 'CV' and len(self.device_handler.capacitancemeter_devices) == 0:
            self.abort_measurement('No capacitance meter connected. Not able to perform a CV measurement')
            return False

        if not self.test_communication():
            return False
        if parameters is None:
            self.abort_measurement('No parameters given')
            return False

        if type == 'IV': # Check the parameters for the IV measurement
            if parameters['startV'] == parameters['stopV']:
                self.abort_measurement('Start and stop voltage are the same, please enter different values.')
                return False
            if parameters['startV'] > parameters['stopV'] and parameters['stepV'] > 0:
                self.abort_measurement('Start voltage is greater than stop voltage, therefore a negative step voltages is required.')
                return False
            if parameters['startV'] < parameters['stopV'] and parameters['stepV'] < 0:
                self.abort_measurement('Start voltage is smaller than stop voltage, therefore a positive step voltages is required.')
                return False
            if abs(parameters['stepV']) > abs(parameters['stopV'] - parameters['startV']):
                self.abort_measurement('Step voltage is greater than the range of the sweep, please enter a smaller value.')
                return False

            if parameters['startV'] > 0 and parameters['stopV'] > 0:
                response = QMessageBox.warning(self.ui, 'Warning', 'You are about to apply a positive voltage to the device. Only proceed if this is intended, as it could damage the DUT.', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                if response == QMessageBox.Cancel:
                    self.abort_measurement('Measurement aborted by user.')
                    return False
            
            
        elif type == 'CV':
            if parameters['startV'] == parameters['stopV']:
                self.abort_measurement('Start and stop voltage are the same, please enter different values.')
                return False
            if parameters['startV'] > parameters['stopV'] and parameters['stepV'] > 0:
                self.abort_measurement('Start voltage is greater than stop voltage, therefore a negative step voltages is required.')
                return False
            if parameters['startV'] < parameters['stopV'] and parameters['stepV'] < 0:
                self.abort_measurement('Start voltage is smaller than stop voltage, therefore a positive step voltages is required.')
                return False
            if abs(parameters['stepV']) > abs(parameters['stopV'] - parameters['startV']):
                self.abort_measurement('Step voltage is greater than the range of the sweep, please enter a smaller value.')
                return False
            if parameters['startV'] > 0 and parameters['stopV'] > 0:
                response = QMessageBox.warning(self.ui, 'Warning', 'You are about to apply a positive voltage to the device. Only proceed if this is intended, as it could damage the DUT.', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                if response == QMessageBox.Cancel:
                    self.abort_measurement('Measurement aborted by user.')
                    return False
            if parameters['startFrequency'] == parameters['stopFrequency'] and parameters['number_of_frequencies'] != 1:
                self.abort_measurement('Start and stop frequency are the same, please enter different values.')
                return False
            
        elif type == 'Constant Voltage':
            if parameters['constant_voltage'] > 0:
                response = QMessageBox.warning(self.ui, 'Warning', 'You are about to apply a positive voltage to the device. Only proceed if this is intended, as it could damage the DUT.', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                if response == QMessageBox.Cancel:
                    self.abort_measurement('Measurement aborted by user.')
                    return False
                
        return True #If all checks are passed, return True

    def test_communication(self): #This function tests the communication with the connected devices by sending a *IDN? command and checking if the response is valid. If any of the devices fail, it will disconnect them and give a warning
        for device in self.device_handler.smu_devices:
            try:
                device.return_id()
            except:
                self.abort_measurement(f'Communication with {device.return_assigned_id()} failed. Please reconnect this device and try again.')
                return
        for device in self.device_handler.voltmeter_devices:
            try:
                device.return_id()
            except:
                self.abort_measurement(f'Communication with {device.return_assigned_id()} failed. Please reconnect this device and try again.')
                return
        for device in self.device_handler.lowV_devices:
            try:
                device.return_id()
            except:
                self.abort_measurement(f'Communication with {device.return_assigned_id()} failed. Please reconnect this device and try again.')
                return
        return True

    def abort_measurement(self, reason: str): #This function aborts the measurement and shows a message on why this happened
        #It is called when the measurement thread emits an error signal or when the user clicks the abort button
        self.ui_changes_stop()
        try:
            self.measurement_thread.abort_measurement()
        except Exception as e:
            print('WARNING: Measurement thread could not be stopped', e)
        warning = QMessageBox.warning(self.ui, 'Measurement aborted', 'The following problem has occured and your measurement has been stopped for safety reasons: \n' + reason, QMessageBox.Ok, QMessageBox.Ok)

    def finish_measurement(self): #Function that is called when the measurement is finished ordinally (only for IV and CV measurements, as constant voltage measurements are only finished manually)
        self.ui_changes_stop()
        self.data_saver.close()
    
    def save_config(self):
        #This function saves the current settings to a config file
        filename, ok = QFileDialog.getSaveFileName(self.ui, 'Save Config', os.path.join(os.path.dirname(__file__), 'config'), 'Config Files (*.json)')
        if not ok:
            return
        if not filename.endswith('.json'):
            filename += '.json'
        
        config = self.config_manager.assemble_config()
        self.config_manager.save_config(config, filename)
        
    def load_config(self):
        #This function loads the config file and applies it to the UI
        filename, ok = QFileDialog.getOpenFileName(self.ui, 'Load Config', os.path.join(os.path.dirname(__file__), 'config'), 'Config Files (*.json)')
        if not ok:
            return
        config = self.config_manager.load_config(filename)
        self.config_manager.apply_config(config)
        self.ui.canvas.restart_plot()
        self.ui.canvas.update_plot()

    def write_parameters(self, parameters):
        # This function writes the parameters of the measurement to a file so they can be used later
        filepath = self.ui.folder_path.text()
        filename = self.ui.filename.text()
        if self.ui.use_timestamp_checkBox.isChecked():
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file = os.path.join(filepath, filename+ '_' +  timestamp + '_MeasurementSettings' + '.json')
        else:
            file = os.path.join(filepath, filename + '_MeasurementSettings' + '.json')
        device_settings = {}
        for device in self.device_handler.smu_devices:
            device_settings[device.return_assigned_id()] = device.settings
        for device in self.device_handler.voltmeter_devices:
            device_settings[device.return_assigned_id()] = device.settings

        settings = {
            'measurement_type': self.ui.measurement_type,
            'parameters': parameters,
            'device_settings': device_settings
        }

        with open(file, 'w') as f:
            json.dump(settings, f, indent = 4)

