#This file includes the functionality of the GUI and the device handling. Also the data saving class is included here.
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, QScrollArea, QFrame, QVBoxLayout, QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
import measurement_thread
import parameter_dialog
import devices
import data_handler
import config_manager
import numpy as np
import os
from datetime import datetime 
import qdarkstyle


class Functionality:
    def __init__(self, ui):
        self.ui = ui
        self.darkmode = False
        self.config_manager = config_manager.config_manager(self.ui)

    def openEvent(self):
        print('Loading latest config')
        config = self.config_manager.load_config(os.path.join(os.path.dirname(__file__), 'config', 'latest.json'))
        self.config_manager.apply_config(config)

    def closeEvent(self):
        for device in self.ui.device_handler.smu_devices:
            device.close()
        for device in self.ui.device_handler.voltmeter_devices:
            device.close()
        for device in self.ui.device_handler.resistancemeter_devices:
            device.close()  
        for device in self.ui.device_handler.lowV_devices:
            device.close()
        self.update_measurement_settings()
        config = self.config_manager.assemble_config()
        self.config_manager.save_config(config, os.path.join(os.path.dirname(__file__), 'config', 'latest.json'))

    def switch_darkmode(self):
        app = QApplication.instance()
        self.darkmode = not self.darkmode
        if self.darkmode:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet("")

    def update_darkmode(self):
        app = QApplication.instance()
        if self.darkmode:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet("")

    def refresh_devices(self):
        #This function refreshes the list of available devices and adds them to the device handler
        self.ui.device_handler.find_devices()
        self.ui.select_decive.clear()
        self.ui.select_decive.addItem('Select Device')
        for device in self.ui.device_handler.device_candidates:
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
            candidate = self.ui.device_handler.device_candidates[index-1] #Select the right device from the list of candidates (index shifts by 1 because of the default entry)
            self.ui.device_handler.device_candidates.remove(candidate) #Remove the selected device from the list of candidates
            self.ui.device_handler.used_ids.append(candidate[1]) #Add the selected device to the list of used ids to not be able to select it again
            if 'Keithley K2200 SMU' in candidate[2]: # Check the type of the device and create the respective object 
                device = devices.K2200(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
                self.K2200_warning()
            elif 'Keithley K2400 SMU' in candidate[2]:
                device = devices.K2400(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2611 SMU' in candidate[2]:
                device = devices.K2600(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2000 Voltmeter' in candidate[2]:
                device = devices.K2000(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.voltmeter_devices.append(device)
            elif 'Rhode&Schwarz NGE103B' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
            elif 'HAMEG HMP4040' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
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
        self.ui.device_handler.find_devices()
        self.ui.select_decive.clear()
        self.ui.select_decive.addItem('Select Device')
        for candidate in self.ui.device_handler.device_candidates:
            self.ui.device_handler.device_candidates.remove(candidate)
            self.ui.device_handler.used_ids.append(candidate[1])
            if 'Keithley K2200 SMU' in candidate[2]: # Check the type of the device and create the respective object 
                device = devices.K2200(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
                self.K2200_warning()
            elif 'Keithley K2400 SMU' in candidate[2]:
                device = devices.K2400(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2611 SMU' in candidate[2]:
                device = devices.K2600(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2000 Voltmeter' in candidate[2]:
                device = devices.K2000(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.voltmeter_devices.append(device)
            elif 'Rhode&Schwarz NGE103B' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
            elif 'HAMEG HMP4040' in candidate[2]:
                device = devices.LowVoltagePowerSupplies(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
            elif 'Dummy' in candidate[2]: #For testing purposes 
                device = devices.Dummy_Device(port = candidate[0], id = candidate[1], rm =  self.ui.rm)
            else:
                print('Device not supported')
                return 
            widget = self.create_device_widget(candidate, device)
            self.ui.device_widgets.append(widget)
            self.ui.device_scrollLayout.addWidget(widget) # Add the device to the scroll area

    def create_device_widget(self, candidate, device):
        #This function creates the widget for the device and adds it to the scroll area
        #The widget contains the ID of the device, a reset button, a clear buffer button and a remove button
        #The widget is a QFrame with a QGridLayout
        device_widget = QFrame()
        device_widget.setFrameShape(QFrame.Box)
        device_layout = QGridLayout()
        device_widget.setLayout(device_layout) # 
        if 'Keithley K2611 SMU' in candidate[2] or 'Keithley K2200 SMU' in candidate[2] or 'Keithley K2400 SMU' in candidate[2]: 
            device_layout.addWidget(QLabel(f'SMU {len(self.ui.device_handler.smu_devices)-1}: ' + candidate[1]) , 0, 0, 1, 2) #Add the naem from the savefile to the layout
        else: 
            device_layout.addWidget(QLabel(candidate[1]), 0, 0, 1, 2)  #Add the ID to the Layout
    
        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(lambda : self.reset_device(device))
        device_layout.addWidget(reset_button, 1, 0)
        clear_buffer_button = QPushButton('Clear Buffer')
        clear_buffer_button.clicked.connect(lambda : self.clear_buffer(device))
        device_layout.addWidget(clear_buffer_button, 1, 1)
        close_button = QPushButton('Remove')
        close_button.clicked.connect(lambda : self.remove_device(device, candidate[1], device_widget))
        device_layout.addWidget(close_button, 1, 2)
        if candidate[2] == 'Keithley K2000 Voltmeter': #For the Keithley K2000 Voltmeter, add a checkbox to select if the device should be used as a voltmeter or resistancemeter, as both options are available
            takeV = QRadioButton('Take Voltage')
            takeR = QRadioButton('Take Resistance')
            takeV.setChecked(True)
            takeR.setChecked(False)
            takeV.clicked.connect(lambda : self.switch_voltmeter_resistancemeter(device=device, statusV=takeV.isChecked()))
            takeR.clicked.connect(lambda : self.switch_voltmeter_resistancemeter(device=device, statusV=takeV.isChecked()))
            device_layout.addWidget(takeV, 2, 0)
            device_layout.addWidget(takeR, 2, 1)  
        
        if candidate[2] == 'Keithley K2400 SMU':  # Add the pop up window to allow for advanced settings for the Keithley K2400 SMUs
            advanced_settings = QPushButton('Advanced Settings')
            device_settings = {}
            advanced_settings.clicked.connect(lambda : self.open_parameter_dialog(device, candidate[1]))
            device_layout.addWidget(advanced_settings, 2, 1, 1, 2)
        
        return device_widget

    def open_parameter_dialog(self, device, id):
        #This function opens the parameter dialog for the device
        #It is used to set the parameters for the device, like voltage range, current range, etc.
        self.parameter_dialog = parameter_dialog.ParameterDiaglog_K2400(device, id, self.ui.rm)
        self.parameter_dialog.show()
    
    def reset_device(self, device): 
        #Function for the device widget to reset the device
        try: 
            device.reset()
            print('Resetting', device.return_id())
        except:
            pass 
    
    def clear_buffer(self, device):
        #Function for the device widget to clear the buffer of the device
        #This is not implemented for all devices, only for the ones that are supported
        try:
            device.clear_buffer()
            print('Clearing Buffer of', device.return_id())
        except:
            pass

    def remove_device(self, device, id, widget):
        #Function for the device widget to remove the device from the list of used devices
        #Remove the device from the list of used devices and delete the widget, this device can now be selected again
        self.ui.device_handler.used_ids.remove(id)
        print('Removing', id)
        if widget in self.ui.device_widgets:
            self.ui.device_widgets.remove(widget)
            widget.deleteLater()
        if device in self.ui.device_handler.smu_devices:
            self.ui.device_handler.smu_devices.remove(device)
        if device in self.ui.device_handler.voltmeter_devices:
            self.ui.device_handler.voltmeter_devices.remove(device)
        if device in self.ui.device_handler.resistancemeter_devices:
            self.ui.device_handler.resistancemeter_devices.remove(device)
        if device in self.ui.device_handler.lowV_devices:
            self.ui.device_handler.lowV_devices.remove(device)

        device.close()
    
    def switch_voltmeter_resistancemeter(self, device, statusV):
        #Function for the device widget to switch the device between voltmeter and resistancemeter mode
        #This is only implemented for the Keithley K2000 Voltmeter, as this device can be used in both modes
        if statusV:
            if device not in self.ui.device_handler.voltmeter_devices:
                self.ui.device_handler.voltmeter_devices.append(device)
            
            if device in self.ui.device_handler.resistancemeter_devices:
                self.ui.device_handler.resistancemeter_devices.remove(device)
        else:
            if device not in self.ui.device_handler.resistancemeter_devices:
                self.ui.device_handler.resistancemeter_devices.append(device)
            if device in self.ui.device_handler.voltmeter_devices:
                self.ui.device_handler.voltmeter_devices.remove(device)

        print(self.ui.device_handler.voltmeter_devices)
        print(self.ui.device_handler.resistancemeter_devices)
     
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

    def change_measurement_type(self, type):
        self.ui.measurement_type = type
        if type == 'IV':
            layout = self.ui.changeUI_IV()
        elif type == 'CV':
            layout = self.ui.changeUI_CV()
        elif type == 'Constant Voltage':
            layout = self.ui.changeUI_ConstantVoltage()
        self.update_measurement_settings()
        
        oldLayout = self.ui.measurement_settings.layout()
        if oldLayout is not None:
            QWidget().setLayout(oldLayout)  # Clear the old layout
        self.ui.measurement_settings.setLayout(layout) #Set the new layout
        config = self.config_manager.assemble_config() #Assemble the config from the UI
        self.config_manager.apply_config(config) #Apply the config to the new layout

    def K2200_warning(self):
        #This function shows a warning message if the K2200 is selected as a device
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
            self.ui.IV_settings = { # Dict to store the settings for the IV measurement
        'startV': self.ui.startV_spinBox.value(),
        'stopV': self.ui.stopV_spinBox.value(),
        'stepV': self.ui.stepV_spinBox.value(),
        'measurements_per_step': self.ui.measurements_per_step_spinBox.value(),
        'time_between_measurements': self.ui.time_between_measurements_spinBox.value(),
        'time_between_steps': self.ui.time_between_steps_spinBox.value(),
        'limitI': self.ui.limitI_spinBox.value(),
        'custom_sweep': self.ui.use_custom_sweep_checkBox.isChecked(),
        }
        elif self.ui.measurement_type == 'CV':
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
        'limitI': self.ui.limitI_spinBox.value()
            }
        elif self.ui.measurement_type == 'Constant Voltage':
            self.ui.ConstantVoltage_settings = { # Dict to store the settings for the Constant Voltage measurement
            'constant_voltage': self.ui.constant_voltage_spinBox.value(),
            'time_between_measurements': self.ui.time_between_measurements_spinBox.value(),
            'limitI': self.ui.limitI_spinBox.value(),
            }

    def start_measurement(self):
        #This function is responsible for actually starting the measurement
        #It takes care of the UI changes and starts the measurement thread
        #It also takes care of the data saving and the sweep creation
        self.update_measurement_settings() #Update the measurement settings
        settings = self.ui.IV_settings if self.ui.measurement_type == 'IV' else self.ui.CV_settings if self.ui.measurement_type == 'CV' else self.ui.constantV_settings
        self.ui_changes_start()
        if self.ui.measurement_type == 'IV':
            if settings['custom_sweep']:
                sweep = self.ui.sweep_creator.read_sweep(self.ui.custom_sweep_file.text())
            else:
                try:
                    sweep = self.ui.sweep_creator.linear_sweep(
                        start = settings['startV'],
                        stop = settings['stopV'],
                        steps = settings['stepV'],
                        number_of_measurements = settings['measurements_per_step'])
                except Exception as e:
                    self.abort_measurement('Error creating sweep. Please check your sweep parameters and try again. ' + str(e))
                    return
        elif self.ui.measurement_type == 'CV':
            return



        if self.ui.use_custom_sweep_checkBox.isChecked(): #if a custom sweep is selected, read the data from the file
            try:
                sweep = self.ui.sweep_creator.read_sweep(self.ui.custom_sweep_file.text())
            except FileNotFoundError:
                self.abort_measurement('File not found')
                return
            if len(sweep) == 0:
                self.abort_measurement('Sweep file is empty')
                return

        else: #Create sweep from the given params if no custom sweep is selected
            try:
                sweep = self.ui.sweep_creator.linear_sweep(
                    start = self.ui.startV.value(), 
                    stop = self.ui.stopV.value(), 
                    steps = self.ui.stepV.value(), 
                    number_of_measurements = self.ui.measurements_per_step.value())
            except Exception as e: 
                self.abort_measurement('Error creating sweep. Please check your sweep parameters and try again. ' + str(e))
                return
        
        
        try:  #try to create the data saver object, if the file already exists, raise an error
            self.data_saver = data_handler.DataSaver(   #start the data save thread 
                filepath = self.ui.folder_path.text(),
                filename = self.ui.filename.text(),
                ui = self.ui,
                functionality = self,
                sweep = sweep)
            
        except FileExistsError:
            self.file_exists_error()
            return
        
        self.ui_changes_start()
        if not self.safety_check(startV= self.ui.startV.value(), stopV=self.ui.stopV.value()): # Check if a positive voltage is gonna be applied, if yes ask user to proceed
            self.abort_measurement('Safety Check failed, preventing chip damage')
            return
        if not self.ui.device_handler.smu_devices:   #abort measurement if no SMU connected
            self.abort_measurement('No SMU connected')
            return
        if not self.test_communication(): #Test the communication with the devices, if it fails, abort the measurement
            return

        self.measurement_thread = measurement_thread.MeasurementThread( #start the measurement thread with the given params
            limit_I = self.ui.limitI.value()*1e-6, 
            sweep = sweep,
            constant_voltage = self.ui.fixed_voltage.value(),
            time_between_measurements = self.ui.time_between_measurements.value(),
            time_between_steps = self.ui.time_between_steps.value(),
            run_sweep = not self.ui.fixed_voltage_checkBox.isChecked(),
            device_handler = self.ui.device_handler,
            functionallity = self)
        if self.ui.canvas_keep_measurement.isChecked():
            self.ui.canvas.keep_data(self.data_saver.filepath, self.ui.time_between_measurements.value())
        self.ui.canvas.restart_plot()
        self.ui.canvas.update_plot()
        self.measurement_thread.start() #start the measurement
        self.measurement_thread.data_signal.connect(self.receive_data)  #Handles the data signal from the measurement thread
        self.measurement_thread.finished_signal.connect(self.finish_measurement) # Handles the finished signal from the measurement thread

    def receive_data(self, data):
        #Function that receives the data from the measurement thread, saves the data and updates the plot
        self.ui.canvas.update_plot(data[0], data[1], time_between_measurements=self.ui.time_between_measurements.value()) #update the plot with the new data 
        self.data_saver.write_data(data)
        
    def file_exists_error(self): #Handles the case when the file already exists
        self.ui.abort_button.setEnabled(False)
        warning = QMessageBox.warning(self.ui, 'Warning', 'Afile with this name already exists, please enter a different filename.', QMessageBox.Ok, QMessageBox.Ok)

    def safety_check(self, startV, stopV):  
        #This function checks if the start and stop voltage are positive, if yes, ask the user to proceed, because HV-MAPS dont like positive voltages
        if startV > 0 or stopV > 0:
            reply = QMessageBox.warning(self.ui, 'Chip Safety', 'Are you sure you want to apply a positive HV to the tested device?', QMessageBox.Yes| QMessageBox.No,  QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        else:
            return True

    def test_communication(self): #This function tests the communication with the connected devices by sending a *IDN? command and checking if the response is valid. If any of the devices fail, it will disconnect them and give a warning
        for device in self.ui.device_handler.smu_devices:
            try:
                device.return_id()
            except:
                self.abort_measurement(f'Communication with {device.return_assigned_id()} failed. Please reconnect this device and try again.')
                return
        for device in self.ui.device_handler.voltmeter_devices:
            try:
                device.return_id()
            except:
                self.abort_measurement(f'Communication with {device.return_assigned_id()} failed. Please reconnect this device and try again.')
                return
        for device in self.ui.device_handler.resistancemeter_devices:
            try:
                device.return_id()
            except:
                self.abort_measurement(f'Communication with {device.return_assigned_id()} failed. Please reconnect this device and try again.')
                return
        for device in self.ui.device_handler.lowV_devices:
            try:
                device.return_id()
            except:
                self.abort_measurement(f'Communication with {device.return_assigned_id()} failed. Please reconnect this device and try again.')
                return
#        print('All devices are communicating correctly')
        return True

    def abort_measurement(self, reason: str): #This function aborts the measurement and shows a warning message for various cases
        self.ui_changes_stop()
        try:
            self.measurement_thread.abort_measurement()
        except Exception as e:
            print('WARNING: Measurement thread could not be stopped', e)
        warning = QMessageBox.warning(self.ui, 'Measurement aborted', 'The following problem has occured and your measurement has been stopped for safety reasons: \n' + reason, QMessageBox.Ok, QMessageBox.Ok)

    def finish_measurement(self): #Function that is called when the measurement is finished ordinally 
        self.ui_changes_stop()
        self.data_saver.close()
        print('Measurement finished and data saved to ' + self.data_saver.filepath)
    

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
        
class Device_Handler:   #Class that handles the devices and their IDs
    def __init__(self, rm):
        self.rm = rm
        self.ports = self.rm.list_resources() # Get all available ports for possible devices
        self.device_candidates = [] # List of device candidates, contains [port, id, type] 
        self.smu_devices = [] # List of used SMUs
        self.voltmeter_devices = [] # List of used voltmeters
        self.resistancemeter_devices = [] # List of used volmeters used to measure resistance
        self.lowV_devices = [] # List of used low voltage power supplies
        self.used_ids = [] # List of the ids of used devices

    def find_devices(self):
        self.ports = self.rm.list_resources() # search devices and clear all canidates for that, to prevent double entries
        print(self.ports)
        self.clear()
#        self.device_candidates.append(['Dummy Port', 'Dummy Device', 'Dummy']) # Add a dummy device for testing purposes
        for port in self.ports:
            try:
                device = self.rm.open_resource(port) # Try to open the port 
            except:
#                print('Could not open port', port) #Debug message
                continue                    
            #As some devices use different termination characters, we need to try different ones, if "\n" does not work we try "\r"
            device.write_termination = '\n'
            device.read_termination = '\n'
            device.baude_rate = 9600 # Set the baud rate to 9600 (default for most devices)
            device.timeout = 500
            try:
                id = device.query('*IDN?') # Query the identification string of the device
                print(port, id)
            except:
                device.write_termination = '\r' # Change the termination characters to "\r"
                device.read_termination = '\r'
                try:
                    id = device.query('*IDN?')
                except:
                    print('Could not get ID from', port) #Debug message
                    continue
            # Now we need to sort the devices into their respective categories.
            if id in self.used_ids: # Check if the device is already in use
                print(id, ' already in use')
                continue
            if 'Keithley' in id and '2200' in id:
                self.device_candidates.append([port, id, 'Keithley K2200 SMU'])
            elif 'KEITHLEY' in id and ('2470' in id or '2450' in id):
                self.device_candidates.append([port, id, 'Keithley K2400 SMU'])
            elif 'Keithley' in id and '2611' in id:
                self.device_candidates.append([port, id, 'Keithley K2611 SMU'])
            elif 'KEITHLEY' in id and '2000'in id:
                self.device_candidates.append([port, id, 'Keithley K2000 Voltmeter'])
            elif 'NGE103B' in id:
                self.device_candidates.append([port, id, 'Rhode&Schwarz NGE103B'])
            elif 'HMP4040' in id: 
                self.device_candidates.append([port, id, 'HAMEG HMP4040'])
            else:
                self.device_candidates.append([port, id, 'Uncharacterized'])
            device.close()

        return np.array(self.device_candidates)

    def clear(self):
        self.device_candidates = []

    
class Sweep: #class that can create voltage sweeps, for now only linear sweeps are implemented
    def __init__(self):
        pass
    
    def linear_sweep(self, start, stop, steps, number_of_measurements): 
        #This function creates a linear sweep from start to stop with the given number of steps
        if start == stop:
            raise ValueError('Start and stop voltage are the same, no sweep possible')
        if start > stop:
            if steps > 0:
                raise ValueError('Steps must be negative if start is greater than stop')
            if abs(stop-start) < abs(steps):
                raise ValueError('Steps are too big for the given range')
        else:
            if steps < 0:
                raise ValueError('Steps must be positive if start is less than stop')
            if abs(stop-start) < abs(steps):
                raise ValueError('Steps are too big for the given range')
        if steps == 0:
            raise ValueError('Steps must not be zero')
        if number_of_measurements <= 0:
            raise ValueError('Number of measurements must be greater than 0')
        

        voltages = np.arange(start, stop+steps, steps)
        n = np.ones(len(voltages))*number_of_measurements
        return np.column_stack([voltages, n])
    
    def read_sweep(self, file):
        return np.loadtxt(file, delimiter = ' ', usecols=[0, 1]) #reads a csv file with the sweep data
    
    def read_frequency_sweep(self, file):
        voltages, n = np.loadtxt(file, delimiter= ' ', unpack= True, usecols = [0, 1])
        frequencies = np.loadtxt(file, delimiter= ' ', unpack= True, usecols= [2])
        return np.array(np.column_stack(voltages, n), frequencies) 

    def frequency_sweep_log(self, startV, stopV, stepV, number_of_measurements, startF, stopF, number_of_frequencies):
        #Creates an array for voltage and frequency sweeps [voltage, [frequencies at this voltage step]]
        #For the frequency sweep, the frequencies are logarithmically spaced, and for all voltages the same frequencies are used
        #If you use different frequencies for each voltage, you need to create the array manually
        if startV == stopV:
            raise ValueError('Start and stop voltage are the same, no sweep possible')
        if startV > stopV:
            if stepV > 0:
                raise ValueError('Steps must be negative if start is greater than stop')
            if abs(stopV-startV) < abs(stepV):
                raise ValueError('Steps are too big for the given range')
        else:
            if stepV < 0:
                raise ValueError('Steps must be positive if start is less than stop')
            if abs(stopV-startV) < abs(stepV):
                raise ValueError('Steps are too big for the given range')
        if stepV == 0:
            raise ValueError('Steps must not be zero')
        if startF == stopF:
            raise ValueError('Start and stop frequency are the same, no sweep possible')
        if startF > stopF:
            raise ValueError('Start frequency must be less than stop frequency')
        
        voltages = np.arange(startV, stopV+stepV, stepV)
        n = np.ones(len(voltages))*number_of_measurements
        frequencies = np.logspace(np.log10(startF), np.log10(stopF), number_of_frequencies, endpoint=True)
        
        sweep = np.array([np.column_stack(voltages, n), frequencies])

