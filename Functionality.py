#This file includes the functionality of the GUI and the device handling. Also the data saving class is included here.
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, QScrollArea, QFrame, QVBoxLayout, QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
import MeasurementThread
import Devices
import numpy as np
import os

class Functionality:
    def __init__(self, ui):
        self.ui = ui

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
                device = Devices.K2200(candidate[0], self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
                self.K2200_warning() #Warn the user that the K2200 is not able to apply negative voltages
            elif 'Keithley K2470 SMU' in candidate[2]:
                device = Devices.K2400(candidate[0], self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2611 SMU' in candidate[2]:
                device = Devices.K2600(candidate[0], self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2000 Voltmeter' in candidate[2]:
                device = Devices.K2000(candidate[0], self.ui.rm)
                self.ui.device_handler.voltmeter_devices.append(device)
            elif 'Rhode&Schwarz NGE103B' in candidate[2]:
                device = Devices.LowVoltagePowerSupplies(candidate[0], self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
            elif 'HAMEG HMP4040' in candidate[2]:
                device = Devices.LowVoltagePowerSupplies(candidate[0], self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
            elif 'Dummy' in candidate[2]: #For testing purposes 
                device = Devices.Dummy_Device(candidate[0], self.ui.rm)
            else:
                print('Device not supported') #If the IDN of the device is not recognized as a supported decvice, print a message
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
                device = Devices.K2200(candidate[0], self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
                self.K2200_warning()
            elif 'Keithley K2470 SMU' in candidate[2]:
                device = Devices.K2400(candidate[0], self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2611 SMU' in candidate[2]:
                device = Devices.K2600(candidate[0], self.ui.rm)
                self.ui.device_handler.smu_devices.append(device)
            elif 'Keithley K2000 Voltmeter' in candidate[2]:
                device = Devices.K2000(candidate[0], self.ui.rm)
                self.ui.device_handler.voltmeter_devices.append(device)
            elif 'Rhode&Schwarz NGE103B' in candidate[2]:
                device = Devices.LowVoltagePowerSupplies(candidate[0], self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
            elif 'HAMEG HMP4040' in candidate[2]:
                device = Devices.LowVoltagePowerSupplies(candidate[0], self.ui.rm)
                self.ui.device_handler.lowV_devices.append(device)
            elif 'Dummy' in candidate[2]: #For testing purposes 
                device = Devices.Dummy_Device(candidate[0], self.ui.rm)
            elif 'Dummy' in candidate[2]:
                device = Devices.Dummy_Device(candidate[0], self.ui.rm)
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
        device_widget.setLayout(device_layout)
        device_layout.addWidget(QLabel(candidate[1]), 0, 0, 1, 2)
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
        
        if candidate[2] == 'Keithley K2611 SMU':  #For the K2611 SMU, add a checkbox to enable high capacitance mode, as this is a feature of the device 
            enableHighC = QCheckBox()
            enableHighCLabel = QLabel('Enable High Capacitance Mode')
            enableHighC.clicked.connect(lambda : device.enable_highC(enableHighC.isChecked()))
            device_layout.addWidget(enableHighC, 2, 1)
            device_layout.addWidget(enableHighCLabel, 2, 0)
        
        return device_widget

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

    def enable_fixed_voltage(self):
        #This function enables or disables the fixed voltage mode
        #It changes the UI accordingly and sets the fixed voltage variable
        self.fixed_voltage = self.ui.fixed_voltage_checkBox.isChecked()
        self.ui.startV.setEnabled(not self.fixed_voltage)
        self.ui.stopV.setEnabled(not self.fixed_voltage)
        self.ui.stepV.setEnabled(not self.fixed_voltage)
        self.ui.measurements_per_step.setEnabled(not self.fixed_voltage)
        self.ui.time_between_steps.setEnabled(not self.fixed_voltage)
        self.ui.use_custom_sweep_checkBox.setEnabled(not self.fixed_voltage)
        self.ui.fixed_voltage.setEnabled(self.fixed_voltage)
        self.ui.canvas.constant_voltage = self.ui.fixed_voltage_checkBox.isChecked()
        self.ui.canvas.clear_plot()
        self.ui.canvas.update_plot()
        if self.fixed_voltage:
            self.ui.canvas_xlimits_label.setText('Time limits')
            self.ui.canvas_lower_x_limit.setSuffix(' s')
            self.ui.canvas_upper_x_limit.setSuffix(' s')
            self.ui.canvas_lower_x_limit.setValue(0)
            self.ui.canvas_upper_x_limit.setValue(self.ui.time_between_measurements.value()*100)
        else:
            self.ui.canvas_xlimits_label.setText('Voltage limits')
            self.ui.canvas_lower_x_limit.setSuffix(' V')
            self.ui.canvas_upper_x_limit.setSuffix(' V')
            self.ui.canvas_lower_x_limit.setValue(self.ui.startV.value())
            self.ui.canvas_upper_x_limit.setValue(self.ui.stopV.value())
            
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

    def select_canvas_file(self):
        #This function opens a file dialog to select a file for the canvas
        #It sets the file path to the selected file
        file, _ = QFileDialog.getOpenFileName(self.ui, 'Select a file')
        if file:
            self.ui.select_canvas_file.setText(file)

    def load_canvas_file(self):
        #This function loads the data from the selected file into the canvas
        self.ui.canvas.load_data(self.ui.select_canvas_file.text())

    def enable_custom_limits(self):
        #This function enables or disables the custom limits for the canvas
        #It takes care of the UI while the actual changes to the plot are handeled in the Plotting.py file
        self.ui.custom_limits = self.ui.canvas_custom_limits.isChecked()
        if self.ui.custom_limits:
            self.ui.canvas_upper_x_limit.setEnabled(True)
            self.ui.canvas_lower_x_limit.setEnabled(True)
            self.ui.canvas_upper_y_limit.setEnabled(True)
            self.ui.canvas_lower_y_limit.setEnabled(True)
            self.ui.canvas.custom_limits = True
        else:
            self.ui.canvas_upper_x_limit.setEnabled(False)
            self.ui.canvas_lower_x_limit.setEnabled(False)
            self.ui.canvas_upper_y_limit.setEnabled(False)
            self.ui.canvas_lower_y_limit.setEnabled(False)
            self.ui.canvas.custom_limits = False
        
        self.ui.canvas.xlim, self.ui.canvas.ylim = [self.ui.canvas_lower_x_limit.value(), self.ui.canvas_upper_x_limit.value()], [self.ui.canvas_lower_y_limit.value(), self.ui.canvas_upper_y_limit.value()]
        self.ui.canvas.set_custom_limits()

    def set_custom_limits(self):
        #This function sets the custom limits for the canvas
        self.ui.custom_limits = self.ui.canvas_custom_limits.isChecked()
        if self.ui.custom_limits:
            self.ui.canvas.custom_limits = True
            self.ui.canvas.xlim, self.ui.canvas.ylim = [self.ui.canvas_lower_x_limit.value(), self.ui.canvas_upper_x_limit.value()], [self.ui.canvas_lower_y_limit.value(), self.ui.canvas_upper_y_limit.value()]
            self.ui.canvas.set_custom_limits()
        else:
            self.ui.canvas.custom_limits = False
            self.ui.canvas.set_custom_limits(None, None)

    def K2200_warning(self):
        #This function shows a warning message if the K2200 is selected as a device
        warning = QMessageBox.warning(self.ui, 'Warning', 'Please note that the K2200 is not able to apply negative voltages. To achieve that please physically reverse the polarity on this device.', QMessageBox.Ok, QMessageBox.Ok)

    def ui_changes_start(self): 
        #This function changes the UI when the measurement is started
        self.ui.startV.setEnabled(False)
        self.ui.stopV.setEnabled(False)
        self.ui.stepV.setEnabled(False)
        self.ui.measurements_per_step.setEnabled(False)
        self.ui.time_between_steps.setEnabled(False)
        self.ui.time_between_measurements.setEnabled(False)
        self.ui.limitI.setEnabled(False)
        self.ui.use_custom_sweep_checkBox.setEnabled(False)
        self.ui.custom_sweep_file.setEnabled(False)
        self.ui.fixed_voltage_checkBox.setEnabled(False)
        self.ui.abort_button.setEnabled(True)
        self.ui.start_button.setEnabled(False)
        self.ui.select_decive.setEnabled(False)
        self.ui.refresh_button.setEnabled(False)
        self.ui.add_device_button.setEnabled(False)
        self.ui.add_all_devices_button.setEnabled(False)
        
    def ui_changes_stop(self):
        #This function changes the UI when the measurement is stopped
        self.ui.startV.setEnabled(True)
        self.ui.stopV.setEnabled(True)
        self.ui.stepV.setEnabled(True)
        self.ui.measurements_per_step.setEnabled(True)
        self.ui.time_between_measurements.setEnabled(True)
        self.ui.limitI.setEnabled(True)
        self.ui.time_between_steps.setEnabled(True)
        self.ui.use_custom_sweep_checkBox.setEnabled(True)
        self.ui.custom_sweep_file.setEnabled(self.ui.use_custom_sweep_checkBox.isChecked())
        self.ui.fixed_voltage_checkBox.setEnabled(True)
        self.ui.fixed_voltage.setEnabled(self.ui.fixed_voltage_checkBox.isChecked())
        self.ui.abort_button.setEnabled(False)
        self.ui.start_button.setEnabled(True)
        self.ui.select_decive.setEnabled(True)
        self.ui.refresh_button.setEnabled(True)
        self.ui.add_device_button.setEnabled(True)
        self.ui.add_all_devices_button.setEnabled(True)

    def start_measurement(self):
        #This function is responsible for actually starting the measurement
        #It takes care of the UI changes and starts the measurement thread
        #It also takes care of the data saving and the sweep creation
        try:  #try to create the data saver object, if the file already exists, raise an error
            self.data_saver = DataSaver(   #start the data save thread 
                filepath = self.ui.folder_path.text(),
                filename = self.ui.filename.text(),
                ui = self.ui,
                functionality = self)
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
            if self.ui.startV.value() == self.ui.stopV.value():
                self.abort_measurement('Start and stop voltage are the same')
                return
            sweep = self.ui.sweep_creator.linear_sweep(
                start = self.ui.startV.value(), 
                stop = self.ui.stopV.value(), 
                steps = self.ui.stepV.value(), 
                number_of_measurements = self.ui.measurements_per_step.value())
            
        self.measurement_thread = MeasurementThread.MeasurementThread( #start the measurement thread with the given params
            limit_I = self.ui.limitI.value()*1e-6, 
            sweep = sweep,
            constant_voltage = self.ui.fixed_voltage.value(),
            time_between_measurements = self.ui.time_between_measurements.value(),
            time_between_steps = self.ui.time_between_steps.value(),
            run_sweep = not self.ui.fixed_voltage_checkBox.isChecked(),
            device_handler = self.ui.device_handler,
            functionallity = self)
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
                print('Could not open port', port) #Debug message
                continue                    
            #As some devices use different termination characters, we need to try different ones, if "\n" does not work we try "\r"
            device.write_termination = '\n'
            device.read_termination = '\n'
            device.baude_rate = 9600 # Set the baud rate to 9600 (default for most devices)
            device.timeout = 500
            try:
                id = device.query('*IDN?') # Query the identification string of the device
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
            elif 'Keithley' in id and '2470' in id:
                self.device_candidates.append([port, id, 'Keithley K2470 SMU'])
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
        voltages = np.arange(start, stop+steps, steps)
        n = np.ones(len(voltages))*number_of_measurements
        return np.column_stack([voltages, n])
    
    def read_sweep(self, file):
        return np.loadtxt(file, delimiter = ' ', usecols=[0, 1]) #reads a csv file with the sweep data
    
class DataSaver():
    #This class is responsible for saving the data to a file
    #It creates the file and writes the data to it
    def __init__(self, filepath, filename, ui, functionality):
        self.functionality = functionality
        self.ui = ui
        self.create_file(filepath, filename)
        
    def create_file(self, filepath, filename):  
        #This function creates the file and writes the header to it
        working_directory = os.getcwd()
        self.filepath = os.path.join(working_directory, filepath, filename + self.ui.filename_suffix.currentText())
        try:
            self.file = open(self.filepath, 'x', buffering=1)
            self.write_header()
        except FileExistsError:
            raise FileExistsError
            return
    
    def write_header(self):
        #The header is created based on the devices that are connected
        #It contains the names of the devices and their respective channels
        #The header is written to the file
        self.header = [] 
        for i in range(len(self.ui.device_handler.smu_devices)):
            self.header.append(f'Voltage_SMU_{i}[V]')
            self.header.append(f'Current_SMU_{i}[A]')
        for i in range(len(self.ui.device_handler.voltmeter_devices)):
            self.header.append(f'Voltage Voltmeter {i} [V]')
        for i in range(len(self.ui.device_handler.resistancemeter_devices)):
            self.header.append(f'Resistance_Resistancemeter_{i}[Ohm]')
        for i in range(len(self.ui.device_handler.lowV_devices)):
            num_channels = self.ui.device_handler.resistancemeter_devices[i].return_num_channels()
            if num_channels == 3:
                self.header.append(f'Voltage_lowV_{i}_Channel_1[V] Voltage_lowV_{i}_Channel_2[V] Voltage_lowV_{i}_Channel_3[V] Current_lowV_{i}_Channel_1[A] Current_lowV_{i}_Channel_2[A] Current_lowV_{i}_Channel_3[A]')
            else:
                self.header.append(f'Voltage_lowV_{i}_Channel_1[V] Voltage_lowV_{i}_Channel_2[V] Voltage_lowV_{i}_Channel_3[V] Voltage_lowV_{i}_Channel_4[V] Current_lowV_{i}_Channel_1[A] Current_lowV_{i}_Channel_2[A] Current_lowV_{i}_Channel_3[A] Current_lowV_{i}_Channel_4[A]')

        self.file.write(' '.join(self.header)+ '\n') 

    def write_data(self, data):
        #This function writes the data to the file
        data_string = ' '.join(map(str, data)) + '\n'
        try:
            self.file.write(data_string)
        except:
            print('Data could not be safed')

    def sweep_header(self, num_of_steps):
        #This function writes the header for the sweep data
        self.file.write('Steps: {} \n'.format(num_of_steps))
    
    def constant_header(self, time_between_points):
        #This function writes the header for the constant voltage data
        self.file.write('Time between points: {} \n'.format(time_between_points))

    def close(self):
        #This function closes the file
        self.file.close()
