#This file contains the MeasurementThread class, which is used to run the measurement in a separate thread
from PyQt5.QtCore import QThread, pyqtSignal
import time
import numpy as np

class MeasurementThread(QThread):
    #Class that runs the actual measurement in a seperate thread, to prevent the UI Thread from being interupted
    data_signal = pyqtSignal(list)  #signal that is emitted when data is available
    finished_signal = pyqtSignal() #signal that is emitted when the measurement is finished or aborted

    def __init__(self, limit_I, sweep, constant_voltage, time_between_measurements, time_between_steps, run_sweep: bool , device_handler, functionallity):
        super().__init__()
        self.limit_I = float(limit_I) #current limit for the SMUs in A
        self.voltages = sweep[:, 0] #array of the voltages included in the sweep (first column of the sweep array)
        self.number_of_measurements = sweep[:, 1] #number of measurements per step (for statistic) (second column of the sweep array)
        self.constant_voltage = constant_voltage #Constnant voltage for the constant voltage measurement
        self.time_between_measurements = float(time_between_measurements) #time between measurements in seconds
        self.time_between_steps = float(time_between_steps) #time between steps in seconds
        self.device_handler = device_handler #Device handler object that contains all the devices
        self.running = True #flag that indicates if the measurement is running
        self.functionallity = functionallity #Passes the logic into this class, as this could be needed
        self.sweep = run_sweep #True if the measurement is a sweep measurement, False if it is a constant voltage measurement
        print('Measurement started')  #Debug message
        print('Sweep:', sweep)  #Debug message
    def run(self): 
        #Main function that runs the measurement
        #This function is called when the thread is started
        if self.sweep:
            self.run_sweep()
        else:
            self.run_constant()

    def start_measurement(self, start):
        #Function that is called when the measurement is started
        #This function sets the voltage and current limits for the SMUs and clears the buffer
        #It also enables the output of the SMUs
        #and sets the voltage to the start voltage
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
        #Ramps up the voltage to the target voltage
        #This function is called when the measurement is started
        #It sets the voltage to the target voltage in steps of 10V, as big voltage steps are not optimal for the measurement
        if target < 0:
            voltages = np.arange(0, target, -10)
        else:
            voltages = np.arange(0, target, 10)

        for voltage in voltages:
            self.set_voltages(voltage) 
            time.sleep(0.1)
        self.set_voltages(target)

    def run_sweep(self):
        #Function that is called when the measurement is a sweep measurement
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
        self.abort_measurement()

    def run_constant(self):
        #Function that is called when the measurement is a constant voltage measurement
        self.start_measurement(self.constant_voltage)
        while self.running:
            data = self.read_data()
            self.send_data(data)
            time.sleep(self.time_between_measurements)

    def read_data(self):
        #Function to read the data from all active devices
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
        #Funtion to set the voltage for all active SMUs
        for smu in self.device_handler.smu_devices: #set the voltage for each SMU
                smu.set_voltage(voltage)

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
                    smu.set_voltage(0)
                time.sleep(1)
        elif voltage > 0.5:
            power_down_sequence = np.arange(voltage, 0, -10)
            for v in power_down_sequence:
                for smu in self.device_handler.smu_devices:
                    smu.set_voltage(0)
                    time.sleep(1)
        self.finished_signal.emit() #emit the finished signal to the main thread
        for smu in self.device_handler.smu_devices:
            smu.set_voltage(0)
            smu.enable_output(False)

    def send_data(self, data):
        self.data_signal.emit(data)  # sends the data to the main thread, acts like a button click w/ add data#