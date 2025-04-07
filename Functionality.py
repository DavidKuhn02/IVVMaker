from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, QScrollArea, QFrame, QVBoxLayout, QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
import Devices
import numpy as np
import time
import os

class Functionality:
    def __init__(self, ui):
        self.ui = ui

    def add_device_entry(self):
        index = self.ui.select_decive.currentIndex()
        if index == 0:
            print('No device selected')
            return
        else:
            self.ui.select_decive.removeItem(index)
            self.ui.select_decive.setCurrentIndex(0)
            candidate = self.ui.device_handler.device_candidates[index-1]
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
            elif 'Dummy' in candidate[2]:
                device = Devices.Dummy_Device(candidate[0], self.ui.rm)
            else:
                print('Device not supported')
                return  
            widget = self.create_device_widget(candidate, device)
            self.ui.device_widgets.append(widget)
            self.ui.device_scrollLayout.addWidget(widget) # Add the device to the scroll area
 
    def create_device_widget(self, candidate, device):
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
        if candidate[2] == 'Keithley K2000 Voltmeter':
            takeV = QRadioButton('Take Voltage')
            takeR = QRadioButton('Take Resistance')
            takeV.setChecked(True)
            takeR.setChecked(False)
            takeV.clicked.connect(lambda : self.switch_voltmeter_resistancemeter(device=device, statusV=takeV.isChecked()))
            takeR.clicked.connect(lambda : self.switch_voltmeter_resistancemeter(device=device, statusV=takeV.isChecked()))
            device_layout.addWidget(takeV, 2, 0)
            device_layout.addWidget(takeR, 2, 1)  
        
        if candidate[2] == 'Keithley K2611 SMU':
            enableHighC = QCheckBox()
            enableHighCLabel = QLabel('Enable High Capacitance Mode')
            enableHighC.clicked.connect(lambda : device.enable_highC(enableHighC.isChecked()))
            device_layout.addWidget(enableHighC, 2, 1)
            device_layout.addWidget(enableHighCLabel, 2, 0)
        
        return device_widget

    def refresh_devices(self):
        self.ui.device_handler.find_devices()
        self.ui.select_decive.clear()
        self.ui.select_decive.addItem('Select Device')
        for device in self.ui.device_handler.device_candidates:
            self.ui.select_decive.addItem(device[2] + ', ID: '+ device[1])

    def add_all_devices(self):
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
            elif 'Dummy' in candidate[2]:
                device = Devices.Dummy_Device(candidate[0], self.ui.rm)
            else:
                print('Device not supported')
                return  
            widget = self.create_device_widget(candidate, device)
            self.ui.device_widgets.append(widget)
            self.ui.device_scrollLayout.addWidget(widget) # Add the device to the scroll area

    def reset_device(self, device):
        try: 
            device.reset()
            print('Resetting', device.return_id())
        except:
            pass 
    
    def clear_buffer(self, device):
        try:
            device.clear_buffer()
            print('Clearing Buffer of', device.return_id())
        except:
            pass

    def remove_device(self, device, id, widget):
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
        self.fixed_voltage = self.ui.fixed_voltage_checkBox.isChecked()
        self.ui.startV.setEnabled(not self.fixed_voltage)
        self.ui.stopV.setEnabled(not self.fixed_voltage)
        self.ui.stepV.setEnabled(not self.fixed_voltage)
        self.ui.measurements_per_step.setEnabled(not self.fixed_voltage)
        self.ui.time_between_steps.setEnabled(not self.fixed_voltage)
        self.ui.use_custom_sweep_checkBox.setEnabled(not self.fixed_voltage)
        self.ui.fixed_voltage.setEnabled(self.fixed_voltage)
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
        self.ui.custom_sweep = self.ui.use_custom_sweep_checkBox.isChecked()
        self.ui.custom_sweep_file.setEnabled(self.ui.custom_sweep)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self.ui, 'Select a Folder')
        if folder:
            self.ui.folder_path.setText(folder)

    def select_canvas_file(self):
        file, _ = QFileDialog.getOpenFileName(self.ui, 'Select a file')
        if file:
            self.ui.select_canvas_file.setText(file)

    def load_canvas_file(self):
        self.ui.canvas.load_data(self.ui.select_canvas_file.text())

    def enable_custom_limits(self):
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
        self.ui.custom_limits = self.ui.canvas_custom_limits.isChecked()
        if self.ui.custom_limits:
            self.ui.canvas.custom_limits = True
            self.ui.canvas.xlim, self.ui.canvas.ylim = [self.ui.canvas_lower_x_limit.value(), self.ui.canvas_upper_x_limit.value()], [self.ui.canvas_lower_y_limit.value(), self.ui.canvas_upper_y_limit.value()]
            self.ui.canvas.set_custom_limits()
        else:
            self.ui.canvas.custom_limits = False
            self.ui.canvas.set_custom_limits(None, None)

    def K2200_warning(self):
        warning = QMessageBox.warning(self.ui, 'Warning', 'Please note that the K2200 is not able to apply negative voltages. To achieve that please physically reverse the polarity on this device.', QMessageBox.Ok, QMessageBox.Ok)

    def start_measurement(self):
        self.ui.abort_button.setEnabled(True)
        try:
            self.data_saver = DataSaver(   #start the data save thread 
                filepath = self.ui.folder_path.text(),
                filename = self.ui.filename.text(),
                ui = self.ui,
                functionality = self)
        except FileExistsError:
            self.file_exists_error()
            return    
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
            if len(sweep[0]) != 2:
                self.abort_measurement('Sweep file is not valid')
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
            
        self.measurement_thread = MeasurementThread( #start the measurement thread
            limit_I = self.ui.limitI.value()*1e-6, 
            sweep = sweep,
            constant_voltage = self.ui.fixed_voltage.value(),
            time_between_measurements = self.ui.time_between_measurements.value(),
            time_between_steps = self.ui.time_between_steps.value(),
            run_sweep = not self.ui.fixed_voltage_checkBox.isChecked(),
            device_handler = self.ui.device_handler,
            functionallity = self
                )
        self.ui.canvas.constant_voltage = self.ui.fixed_voltage_checkBox.isChecked()
        self.measurement_thread.start() #start the measurement
        self.measurement_thread.data_signal.connect(self.receive_data)  #handle collected data
        
    def receive_data(self, data):
        self.ui.canvas.update_plot_live_data(data[0], data[1], time_between_measurements=self.ui.time_between_measurements.value()) #update the plot with the new data 
        self.data_saver.write_data(data)
        
    def file_exists_error(self):
        self.ui.abort_button.setEnabled(False)
        warning = QMessageBox.warning(self.ui, 'Warning', 'Afile with this name already exists, please enter a different filename.', QMessageBox.Ok, QMessageBox.Ok)

    def safety_check(self, startV, stopV):
        if startV > 0 or stopV > 0:
            reply = QMessageBox.warning(self.ui, 'Chip Safety', 'Are you sure you want to apply a positive HV to the tested device?', QMessageBox.Yes| QMessageBox.No,  QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        else:
            return True

    def abort_measurement(self, reason: str):
        self.ui.abort_button.setEnabled(False)
        self.data_saver.file.close()
        try:
            self.measurement_thread.abort_measurement()
        except Exception as e:
            print('WARNING: Measurement thread could not be stopped', e)
        warning = QMessageBox.warning(self.ui, 'Measurement aborted', 'The following problem has occured and your measurement has been stopped for safety reasons: \n' + reason, QMessageBox.Ok, QMessageBox.Ok)

    def finish_measurement(self):
        self.measurement_thread.abort_measurement()
        self.ui.abort_button.setEnabled(False)
        self.data_saver.file.close()
        print('Measurement finished and data saved to ' + self.data_saver.filepath)
        
class Device_Handler:
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


class MeasurementThread(QThread):
    #Class that runs the actual measurement in a seperate thread, to prevent the UI Thread from being interupted
    data_signal = pyqtSignal(list)  #signal that is emitted when data is available
    finished_signal = pyqtSignal() #signal that is emitted when the measurement is finished or aborted

    def __init__(self, limit_I, sweep, constant_voltage, time_between_measurements, time_between_steps, run_sweep: bool , device_handler, functionallity):
        super().__init__()
        self.limit_I = float(limit_I) #current limit for the SMUs in A
        self.voltages = sweep[:, 0] #array of the voltages included in the sweep (first column of the sweep array)
        self.number_of_measurements = sweep[:, 1] #number of measurements per step (for statistic) (second column of the sweep array)
        self.constant_voltage = constant_voltage
        self.time_between_measurements = float(time_between_measurements)
        self.time_between_steps = float(time_between_steps)
        self.device_handler = device_handler
        self.running = True
        self.functionallity = functionallity
        self.sweep = run_sweep
        print('Measurement Thread started')

    def run(self):
        if self.sweep:
            self.run_sweep()
        else:
            self.run_constant()
        self.functionallity.finish_measurement()

    def start_measurement(self, start):
        self.running = True
        for smu in self.device_handler.smu_devices:
            smu.set_limit(self.limit_I)
            smu.enable_output(True)
            smu.clear_buffer()
        if start == 0:
            return
        else:
            self.rampup(start)

    def rampup(self, target):
        if target < 0:
            voltages = np.arange(0, target, -10)
        else:
            voltages = np.arange(0, target, 10)

        for voltage in voltages:
            self.set_voltages(voltage) 
            time.sleep(0.1)
        self.set_voltages(target)

    def run_sweep(self):
        self.start_measurement(self.voltages[0])
        for i in range(len(self.voltages)):
            if not self.running:
                break
            self.set_voltages(self.voltages[i])
            time.sleep(float(self.time_between_steps))

            for j in range(int(self.number_of_measurements[i])):
                if not self.running:
                    break
                data = self.read_data()
                self.send_data(data)
                time.sleep(self.time_between_measurements)

    def run_constant(self):
        self.start_measurement(self.constant_voltage)
        while self.running:
            data = self.read_data()
            self.send_data(data)
            time.sleep(self.time_between_measurements)

    def read_data(self):
        data = []
        for smu in self.device_handler.smu_devices: #measure the voltage and current for each SMU
            voltage_smu = smu.measure_voltage() 
            current_smu = smu.measure_current()
            data.append(voltage_smu)
            data.append(current_smu)
        
        for voltage_unit in self.device_handler.voltmeter_devices: #measure the additional voltages
            voltage = voltage_unit.measure_voltage()
            data.append(voltage)

        for resistance_unit in self.device_handler.resistancemeter_devices: #measure the additional resistances
            resistance = resistance_unit.measure_resistance()
            data.append(resistance) 

        for lowV_unit in self.device_handler.lowV_devices: #read the power drawn by the devices at the lowV power supplies (iterates over all channels)
            U, I = lowV_unit.read_output()
            data.append(U)
            data.append(I)

        return data
    
    def set_voltages(self, voltage):
        for smu in self.device_handler.smu_devices: #set the voltage for each SMU
                smu.set_voltage(voltage)

    def abort_measurement(self):
        self.running = False
        voltage = float(self.device_handler.smu_devices[0].measure_voltage())
        if voltage < -0.5:
            power_down_sequence = np.arange(voltage, 0, 10)
            for v in power_down_sequence:
                for smu in self.device_handler.smu_devices:
                    smu.set_voltage(0)
                time.sleep(1)
        elif voltage > 0.5:
            power_down_sequence = np.arange(voltage, 0, -10)
            for v in power_down_sequence:
                for smu in self.device_handler.smu_devices:
                    smu.set_voltage(0)
                    time.sleep(1)

        for smu in self.device_handler.smu_devices:
            smu.set_voltage(0)
            smu.enable_output(False)
        self.finished_signal.emit() #emit the finished signal to the main thread

    def send_data(self, data):
        self.data_signal.emit(data)  # sends the data to the main thread, acts like a button click w/ add data
    
class Sweep: #class that can create voltage sweeps 
    def __init__(self):
        pass
    
    def linear_sweep(self, start, stop, steps, number_of_measurements):
        voltages = np.arange(start, stop+steps, steps)
        n = np.ones(len(voltages))*number_of_measurements
        return np.column_stack([voltages, n])
    
    def read_sweep(self, file):
        return np.loadtxt(file, delimiter = ' ') #reads a csv file with the sweep data
    
class DataSaver():
    def __init__(self, filepath, filename, ui, functionality):
        self.functionality = functionality
        self.ui = ui
        self.create_file(filepath, filename)
        
    def create_file(self, filepath, filename):
        working_directory = os.getcwd()
        self.filepath = os.path.join(working_directory, filepath, filename + self.ui.filename_suffix.currentText())
        try:
            self.file = open(self.filepath, 'x', buffering=1)
            self.write_header()
        except FileExistsError:
            raise FileExistsError
            return
    
    def write_header(self):
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
        data_string = ' '.join(map(str, data)) + '\n'
        try:
            self.file.write(data_string)
        except:
            print('Data could not be safed')

