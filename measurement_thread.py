#This file contains the MeasurementThread class, which is used to run the measurement in a separate thread
from PyQt5.QtCore import QThread, pyqtSignal
import time
import numpy as np

class MeasurementThread(QThread):
    #Class that runs the actual measurement in a seperate thread, to prevent the UI Thread from being interupted
    data_signal = pyqtSignal(list)  #signal that is emitted when data is available
    finished_signal = pyqtSignal() #signal that is emitted when the measurement is finished or aborted
    error_signal = pyqtSignal(str) #signal that is emitted when an error occurs

    def __init__(self, ui, device_handler): #Set up the thread
        super().__init__()
        self.ui = ui
        self.device_handler = device_handler
    
    def run(self): #This function is called when the thread is started
        # Before this function is called, the set_parameters function is called to set the parameters for the measurement
        try:
            self.running = True
            if self.type == 'IV':
                self.run_IV_measurement(self.parameters)
            elif self.type == 'Constant Voltage':
                self.run_constantV_measurement(self.parameters)
            elif self.type == 'CV':
                self.run_cv_measurement(self.parameters)
            else:
                raise ValueError('Unknown measurement type')
            self.abort_measurement() #call the abort function when the measurement is finished or aborted
        except Exception as e:
            self.error_signal.emit(str(e))
            
    def set_parameters(self, type, parameters):
        self.type = type
        self.parameters = parameters
        # This function is called to set the parameters for the measurement

    def start_measurement(self, start):
        #Function that is called when the measurement is started
        #This function sets the voltage and current limits for the SMUs and clears the buffer
        #It also enables the output of the SMUs
        #and sets the voltage to the start voltage 
        self.running = True #Flag to indicate that the measurement is running 
        for smu in self.device_handler.smu_devices:   #Reset the SMUs and set the current limit
            smu.set_limit(float(self.limit_I))
            smu.enable_output(True)
            smu.clear_buffer()
        if start == 0:   #If the start voltage is not 0, a rampup sequence is started
            return 
        else:
            self.rampup(start)

    def rampup(self, target):
        #Ramps up the voltage to the target voltage
        #This function is called when the measurement is started
        #It sets the voltage to the target voltage in steps of 10V, as big voltage steps are not optimal for the measurement
        if target < 0:
            voltages = np.arange(0, target, -10)
        else:
            voltages = np.arange(0, target, 10)

        for voltage in voltages:
            self.set_voltages(voltage) 
            QThread.msleep(100)
        self.set_voltages(target)

        

    def run_IV_measurement(self, parameters):
        #Function that is called when the measurement is a IV measurement
        if parameters['custom_sweep'] == True:  #Checks wether a sweep needs to be created or read from a file
            self.voltages, self.number_of_measurements = self.read_sweep(parameters['custom_sweep_file'])
        else: #Creates the linear sweep 
            self.voltages, self.number_of_measurements = self.linear_sweep(parameters['startV'], parameters['stopV'], parameters['stepV'], parameters['measurements_per_step'])
        self.time_between_steps = int(parameters['time_between_steps']*1000)
        self.time_between_measurements = int(parameters['time_between_measurements']*1000)
        self.limit_I = parameters['limitI']  

        self.start_measurement(self.voltages[0]) #The measurement is started with the first voltage
        for i in range(len(self.voltages)):  #Loops over all voltages
            if not self.running:  #Checks if the measurement is still running or has been aborted by the user
                break
            self.set_voltages(self.voltages[i]) #Set the voltage at the SMUs
            QThread.msleep(self.time_between_steps)  #Wait for built up charge to flow away 
            for j in range(int(self.number_of_measurements[i])): #Loop over the number of measurements for this voltage
                if not self.running:  #Checks if the measurement is still running or has been aborted by the user
                    break 
                data = self.read_data(self.voltages[i]) #Accumulate the data from all devices
                self.send_data(data) #Sends the data to the main thread to be saved
                QThread.msleep(self.time_between_measurements) #Sleep for the time between measurements
        if self.running: #  If the measurement is still running, the abort function is called, after the measurement is finished
            self.abort_measurement()

    def run_constantV_measurement(self, parameters):
        #Function that is called when the measurement is a constant voltage measurement
        self.constant_voltage = parameters['constant_voltage']
        self.time_between_measurements = int(parameters['time_between_measurements']*1000)
        self.limit_I = parameters['limitI']

        self.start_measurement(self.constant_voltage) #Start the measurement with the constant voltage
        while self.running: #Continuously measure the current at the constant voltage as long as the measurement flag is set to True
            data = self.read_data(self.constant_voltage) #Accumulate the data from all devices
            self.send_data(data) #Sends the data to the main thread to be saved
            QThread.msleep(self.time_between_measurements) #Sleep for the time between measurements

    def run_cv_measurement(self, parameters):
        #This function is used to do CV measurements. This works only with a HAMEG 8118 connected.
        if parameters['custom_sweep'] == True: #Checks wether a sweep needs to be created or read from a file
            self.voltages, self.number_of_measurements, self.frequencies = self.read_frequency_sweep(parameters['custom_sweep_file'])
        else: #Creates the sweep (log or linear)
            if parameters['logarithmic_frequency_steps'] == True:
                self.voltages, self.number_of_measurements, self.frequencies = self.frequency_sweep_log(parameters['startV'], parameters['stopV'], parameters['stepV'], parameters['measurements_per_step'], parameters['startFrequency'], parameters['stopFrequency'], parameters['number_of_frequencies'])
            else:
                self.voltages, self.number_of_measurements, self.frequencies = self.frequency_sweep_linear(parameters['startV'], parameters['stopV'], parameters['stepV'], parameters['measurements_per_step'], parameters['startFrequency'], parameters['stopFrequency'], parameters['number_of_frequencies'])
        self.time_between_steps = int(parameters['time_between_steps']*1000)
        self.time_between_measurements = int(parameters['time_between_measurements']*1000)
        self.limit_I = parameters['limitI']
        self.start_measurement(self.voltages[0]) #The measurement is started with the first voltage
        for i in range(len(self.voltages)): #Loops over all voltages
            if not self.running: #Checks if the measurement is still running or has been aborted by the user
                break
            self.set_voltages(self.voltages[i]) #Set the voltage at the SMUs
            QThread.msleep(self.time_between_steps) #Wait for built up charge to flow away

            for j in range(len(self.frequencies)): #Loops over all frequencies at this voltage
                if not self.running: #Checks if the measurement is still running or has been aborted by the user
                    break
                self.set_frequencies(self.frequencies[j]) #Set the frequency at the capacitance meter
                data = self.read_data(self.voltages[i], self.frequencies[j]) #Accumulate the data from all devices
                self.send_data(data) #Sends the data to the main thread to be saved
                QThread.msleep(self.time_between_measurements) #Sleep for the time between measurements
        if self.running:
            self.abort_measurement()
        #If the measurement is still running, the abort function is called, after the measurement is finished
        return 


    def read_data(self, voltage = None, frequency = None):
        #Function to read the data from all active devices
        data = []
        data.append(str(voltage)) #append the voltage to the data list

        for smu in self.device_handler.smu_devices: #measure the voltage and current for each SMU
            voltage_smu = smu.measure_voltage() 
            current_smu = smu.measure_current()
            data.append(float(voltage_smu))
            data.append(float(current_smu))
        
        for voltage_unit in self.device_handler.voltmeter_devices: #measure the quantities for each voltmeter
            quantity = voltage_unit.measure()
            data.append(float(quantity))

        for lowV_unit in self.device_handler.lowV_devices: #read the power drawn by the devices at the lowV power supplies (iterates over all channels)
            U, I = lowV_unit.read_output()
            data.append(float(U))
            data.append(float(I))

        for capacitance_unit in self.device_handler.capacitancemeter_devices: 
            frequency = capacitance_unit.measure_frequency() # Measure the frequency that is set at the capacitance meter
            impedance, phase = capacitance_unit.measure_impedance_phase() #Returns the impedance and phase of the capacitance meter

            data.append(float(impedance))
            data.append(float(phase))
            data.append(float(frequency))
        return data
    
    def set_voltages(self, voltage):
        #Funtion to set the voltage for all active SMUs
        for smu in self.device_handler.smu_devices: #set the voltage for each SMU
                smu.set_voltage(voltage)
    
    def set_frequencies(self, frequency):
        #Function to set the frequency for all capacitance meters
        for device in self.device_handler.capacitancemeter_devices: #set the frequency for each capacitance meter
            device.set_frequency(frequency)
    def abort_measurement(self):
        #Function to abort the measurement
        #This function is called when the measurement is aborted or finished
        #It sets the voltage to 0 and disables the output of the SMUs
        #It also sets the running flag to False
        #and emits the finished signal to the main thread
        self.running = False
        voltage = float(self.device_handler.smu_devices[0].measure_voltage())
        if voltage < -0.5:
            power_down_sequence = np.arange(voltage, 0, 10)
            for v in power_down_sequence:
                for smu in self.device_handler.smu_devices:
                    smu.set_voltage(v)
                time.sleep(.2)
        elif voltage > 0.5:
            power_down_sequence = np.arange(voltage, 0, -10)
            for v in power_down_sequence:
                for smu in self.device_handler.smu_devices:
                    smu.set_voltage(v)
                    time.sleep(.2)
        self.finished_signal.emit() #emit the finished signal to the main thread
        for smu in self.device_handler.smu_devices:
            smu.set_voltage(0)
            smu.enable_output(False)

    def send_data(self, data):
        self.data_signal.emit(data)  # sends the data to the main thread, acts like a button click w/ add data#

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
        return voltages, n
    
    def read_sweep(self, file):
        return np.loadtxt(file, delimiter = ' ', usecols=[0, 1], unpack= True) #reads a csv file with the sweep data
    
    def read_frequency_sweep(self, file):
        voltages, n = np.loadtxt(file, delimiter= ' ', unpack= True, usecols = [0, 1])
        frequencies = np.loadtxt(file, delimiter= ' ', unpack= True, usecols= [2])
        return np.array(np.column_stack(voltages, n), frequencies) 

    def frequency_sweep_log(self, startV, stopV, stepV, number_of_measurements, startF, stopF, number_of_frequencies):
        #Creates an array for voltage and frequency sweeps [voltage, [frequencies at this voltage step]]
        #For the frequency sweep, the frequencies are logarithmically spaced, and for all voltages the same frequencies are used
        #If you use different frequencies for each voltage, you need to create the array manually
#
        voltages = np.arange(startV, stopV+stepV, stepV)
        n = np.ones(len(voltages))*number_of_measurements
        frequencies = np.logspace(np.log10(startF), np.log10(stopF), number_of_frequencies, endpoint=True)
        
        return voltages, n, frequencies
    
    def frequency_sweep_linear(self, startV, stopV, stepV, number_of_measurements, startF, stopF, number_of_frequencies):
        #Creates an array for voltage and frequency sweeps [voltage, [frequencies at this voltage step]]
        #For the frequency sweep, the frequencies are linearly spaced, and for all voltages the same frequencies are used
        #If you use different frequencies for each voltage, you need to create the array manually
        voltages = np.arange(startV, stopV+stepV, stepV)
        n = np.ones(len(voltages))*number_of_measurements
        frequencies = np.linspace(startF, stopF, number_of_frequencies, endpoint=True)
        return voltages, n, frequencies