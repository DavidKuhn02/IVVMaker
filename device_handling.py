import json
0import pyvisa as visa
import numpy as np
# This module handles the connected devices

class Device_Handler:   #Class that handles the devices and their IDs
    def __init__(self, rm):
        self.rm = rm
        self.ports = self.rm.list_resources() # Get all available ports for possible devices
        self.device_candidates = [] # List of device candidates, contains [port, id, type] 
        self.smu_devices = [] # List of used SMUs
        self.voltmeter_devices = [] # List of used voltmeters
        self.lowV_devices = [] # List of used low voltage power supplies
        self.capacitancemeter_devices = [] # List of used capacitance meters
        self.used_ids = [] # List of the ids of used devices
        with open('devices/supported_devices.json', 'r') as f:
            self.supported_devices = json.load(f)  # Load the supported devices from the JSON file

    def find_devices(self):
        self.ports = self.rm.list_resources() # search devices and clear all canidates for that, to prevent double entries
        self.clear()
        #self.device_candidates.append(['Dummy Port', 'Dummy Device', 'Dummy']) # Add a dummy device for testing purposes
        for port in self.ports:
            try:
                device = self.rm.open_resource(port) # Try to open the port 
            except:
                continue                    
            #As some devices use different termination characters, we need to try different ones, if "\n" does not work we try "\r"
            device.write_termination = '\n'
            device.read_termination = '\n'
            device.baude_rate = 9600 # Set the baud rate to 9600 (default for most devices)
            device.timeout = 500
            try:
                id = device.query('*IDN?').strip('').strip('') # Query the identification string of the device
                print(port, id)
            except:
                device.write_termination = '\r' # Change the termination characters to "\r"
                device.read_termination = '\r'
                try:
                    id = device.query('*IDN?').strip('').strip('') #Try again if the device is not responding with "\n" terminations  
                except:
                    #print('Could not get ID from', port) #Debug message
                    continue
            # Now we need to sort the devices into their respective categories.
            # If you want to add a new device, you need to add it here 
            found = False
            for entry in self.supported_devices:
                if all(match_id in id for match_id in entry['match_id']):
                    self.device_candidates.append([port, id, entry['type'], entry['config']])  # Add the device candidate
                    found = True
            if not found:
                print('Device not supported', id, port)  # Debug message for unsupported devices


            device.close()

        print('Device search complete', self.device_candidates)  # Debug message for the found devices
    def add_device(self, candidate_id):
        #This function adds a device to the list of used devices
        return
            



    def clear(self):

        self.device_candidates = []

class Device:
    def __init__(self, port, id, rm, dev_type, cfg_path, device_handler):
        self.port = port
        self.assigned_id = id
        self.rm = rm
        self.type = dev_type
        self.device_handler = device_handler  # Reference to the Device_Handler instance
        self.device = self.rm.open_resource(port)  # Open the port
        with open(cfg_path, 'r') as f:
            self.config = json.load(f)  # Load the device configuration from the JSON file
        self.init_device()
        self.add_to_device_list()

    def add_to_device_list(self):
        if self.type =='SMU':
            self.device_handler.smu_devices.append(self)
        elif self.type == 'Voltmeter':
            self.device_handler.voltmeter_devices.append(self)
        elif self.type == 'Powersupply':
            self.device_handler.lowV_devices.append(self)
        elif self.type == 'LCR':
            self.device_handler.capacitancemeter_devices.append(self)
    
    def remove_from_device_list(self):
        self.device_handler.used_ids.remove(self.assigned_id)
        self.device_handler.smu_devices = [dev for dev in self.device_handler.smu_devices if dev != self]
        self.device_handler.voltmeter_devices = [dev for dev in self.device_handler.voltmeter_devices if dev != self]
        self.device_handler.lowV_devices = [dev for dev in self.device_handler.lowV_devices if dev != self]
        self.device_handler.capacitancemeter_devices = [dev for dev in self.device_handler.capacitancemeter_devices if dev != self]
        self.device.close()  # Close the device connection

    def init_device(self):
        for cmd in self.config['init_commands']:
            self.device.write(cmd)

    def reset(self):
        cmd = self.config['commands']['reset']
        if cmd:
            self.device.write(cmd)

    def clear_buffer(self):
        cmds = self.config['commands']['clear_buffer']
        if cmds:
            if isinstance(cmds, str):
                self.device.write(cmds)
            elif isinstance(cmds, list):
                for cmd in cmds:
                    self.device.write(cmd)

    def return_id(self):
        cmd = self.config['commands']['return_id']
        if cmd:
            id = self.device.query(cmd)
            return id

    def return_port(self):
        cmd = self.config['commands']['return_port']
        if cmd:
            port = self.device.query(cmd)
            return port
        
    def close(self):
        self.device.close()

    def set_limit(self, limitI):
        cmd = self.config['commands']['set_limit']
        if cmd:
            self.device.write(cmd.format(limitI=limitI))

    def enable_output(self, state):
        if state:
            cmd = self.config['commands']['enable_output']
        else:
            cmd = self.config['commands']['disable_output']
        if cmd:
            self.device.write(cmd)

    def set_voltage(self, voltage):   #Available only for SMUs
        cmd = self.config['commands']['set_voltage']
        if cmd:
            self.device.write(cmd.format(voltage=voltage))

    def set_frequency(self, frequency):  # Available only for LCRs
        cmd = self.config['commands']['set_frequency']
        if cmd:
            self.device.write(cmd.format(frequency=frequency))

    def measure_voltage(self):  #Available only for SMUs
        cmd = self.config['commands']['measure_voltage']
        if cmd:
            voltage = float(self.device.query(cmd))
            return voltage
    
    def measure_current(self):  #Available only for SMUs
        cmd = self.config['commands']['measure_current']
        if cmd:
            current = float(self.device.query(cmd))
            return current

    def measure(self):  #Available only for Voltmeters
        cmd = self.config['commands']['measure']
        if cmd:
            measurement = float(self.device.query(cmd))
            return measurement

    def read_output(self):   #Only for LowV PS
        U, I = [], []
        query_voltage = self.config['commands']['read_voltage']
        query_current = self.config['commands']['read_current']
        for i in range(self.config['num_channels']):
            self.device.write(self.config['commands']['set_channel'].format(channel=i+1))  # Set the channel
            if query_voltage:
                U.append(float(self.device.query(query_voltage)))
            if query_current:
                I.append(float(self.device.query(query_current)))
        return U, I
        
    def measure_frequency(self):  #Only for LCR
        cmd = self.config['commands']['measure_frequency']
        if cmd:
            measurement = float(self.device.query(cmd))
            return measurement

    def measure_impedance_phase(self): #Only for LCR
        cmd = self.config['commands']['measure_impedance_phase']
        if cmd:
            measurement = float(self.device.query(cmd))
            return measurement

    def set_voltage_range(self, range):
        ranges = {
            "100mV": 100E-3,
            "200mV": 200E-3,
            "1V": 1,
            "2V": 2,
            "10V": 10,
            "20V": 20,
            "100V": 100,
            "200V": 200,
            "1000V": 1000,
            "Auto": "AUTO"
        }
        range = ranges.get(range, None)
        if range is not None:
            if range == "AUTO":
                cmd = self.config['commands']['set_voltage_range_auto_on']
                if cmd:
                    self.device.write(cmd)
            else:
                cmd = self.config['commands']['set_voltage_range_auto_off']
                if cmd:
                    self.device.write(cmd)
                cmd = self.config['commands']['set_voltage_range'].format(range=range)
                if cmd:
                    self.device.write(cmd)
    def set_current_range(self, range):
        ranges = {
            "10nA": 10E-9,
            "100nA": 100E-9,
            "1uA": 1E-6,
            "10uA": 10E-6,
            "100uA": 100E-6,
            "1mA": 1E-3,
            "10mA": 10E-3,
            "100mA": 100E-3,
            "1A": 1,
            "Auto": "AUTO"
        }
        range = ranges.get(range, None)
        if range is not None:
            if range == "AUTO":
                cmd = self.config['commands']['set_current_range_auto_on']
                if cmd:
                    self.device.write(cmd)
            else:
                cmd = self.config['commands']['set_current_range_auto_off']
                if cmd:
                    self.device.write(cmd)
                cmd = self.config['commands']['set_current_range'].format(range=range)
                if cmd:
                    self.device.write(cmd)

    def set_nplc(self, nplc):
        cmd = self.config['commands']['set_nplc'].format(nplc=nplc)
        if cmd:
            self.device.write(cmd)

    def set_filter(self, filter):
