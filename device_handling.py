import json
import pyvisa as visa
import numpy as np
import os
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
        self.config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'devices')
        with open(os.path.join(self.config_dir, 'supported_devices.json'), 'r') as f:
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
            found = False         # Flag to check if device is found in supported devices
            for entry in self.supported_devices: #Check all supported devices 
                if all(match_id in id for match_id in entry['match_id']): 
                    self.device_candidates.append([port, id, entry['type'], entry['config']])  # Add the device candidate
                    found = True
            if not found:
                print('Device not supported', id, port)  # Debug message for unsupported devices
            device.close() #Close Devices again, only reopen them once actually selected for a measurement

        print('Device search complete', self.device_candidates)  # Debug message for the found devices
    def add_device(self, candidate_id):
        #This function adds a device to the list of used devices
        return
            



    def clear(self):
        #Clear the list of device candidates
        self.device_candidates = []

class Device:
    '''
    Class for a device connected to the measurement system. It contains all the functionality to communicate with the device.
    The commands for each individual device needs to be implemented in the device's configuration file. If you want to add a new device to the system, you need to figure out all the commands and assemble a configuration file for it.
    Maybe secondary UI for that in a future version.
    '''
    def __init__(self, port, id, rm, dev_type, cfg_path, device_handler):
        '''
        Initialize the device with the given parameters.
        '''
        self.port = port  # Port at which the device is connected 
        self.assigned_id = id #ID the device returned at the initial search (should be constant for every device)
        self.rm = rm # Reference to the resource manager
        self.type = dev_type # Type of the device
        self.device_handler = device_handler  # Reference to the Device_Handler instance
        self.device = self.rm.open_resource(port)  # Open the port
        self.config_path = cfg_path  # Path to the device configuration file
        with open(cfg_path, 'r') as f:
            self.config = json.load(f)  # Load the device configuration from the JSON file
        self.settings_path = os.path.join(self.device_handler.config_dir, "device_settings" , f"{self.assigned_id}.json")
        
        self.init_device() 
        self.load_settings()
        self.add_to_device_list()

    def save_settings(self):
        # Save the current settings to a settings file
        with open(self.settings_path, 'w') as f:
            json.dump(self.settings, f, indent = 2)

    def load_settings(self):
        # Load the last settings from the settings file
        try: 
            with open(self.settings_path, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}

    def add_to_device_list(self):
        #Add the device to the list of opened devices 
        if self.type =='SMU':
            self.device_handler.smu_devices.append(self)
        elif self.type == 'Voltmeter':
            self.device_handler.voltmeter_devices.append(self)
        elif self.type == 'Powersupply':
            self.device_handler.lowV_devices.append(self)
        elif self.type == 'LCR':
            self.device_handler.capacitancemeter_devices.append(self)
    
    def remove_from_device_list(self):
        # Remove the device from the list of opened devices
        self.save_settings()
        self.device_handler.used_ids.remove(self.assigned_id)
        self.device_handler.smu_devices = [dev for dev in self.device_handler.smu_devices if dev != self]
        self.device_handler.voltmeter_devices = [dev for dev in self.device_handler.voltmeter_devices if dev != self]
        self.device_handler.lowV_devices = [dev for dev in self.device_handler.lowV_devices if dev != self]
        self.device_handler.capacitancemeter_devices = [dev for dev in self.device_handler.capacitancemeter_devices if dev != self]
        self.device.close()  # Close the device connection

    def init_device(self):
        # Sends the commands specified in the configuration file "init_commands" to initialize the device
        for cmd in self.config['init_commands']:
            self.device.write(cmd)

    def reset(self):
        # Sends the command specified in the configuration file "reset" to reset the device
        cmd = self.config['commands']['reset']
        if cmd:
            self.device.write(cmd)

    def clear_buffer(self):
        # Sends the commands specified in the configuration file "clear_buffer" to clear the device buffer
        cmds = self.config['commands']['clear_buffer']
        if cmds:
            if isinstance(cmds, str):
                self.device.write(cmds)
            elif isinstance(cmds, list):
                for cmd in cmds:
                    self.device.write(cmd)

    def return_id(self):
        # Queries the device ID with the "return_id" command specified in the configuration file
        cmd = self.config['commands']['return_id']
        if cmd:
            id = self.device.query(cmd)
            return id

    def return_assigned_id(self):
        # Returns the assigned ID of the device
        return self.assigned_id

    def return_port(self):
        # Queries the device port with the "return_port" command specified in the configuration file
        cmd = self.config['commands']['return_port']
        if cmd:
            port = self.device.query(cmd)
            return port
        
    def close(self): 
        #Closes the device
        self.device.close()

    def set_limit(self, limitI):
        '''
        Sets the current limit for the SMU.
        param limitI: The current limit in uA
        '''
        cmd = self.config['commands']['set_limit']
        if cmd:
            self.device.write(cmd.format(limitI=limitI*1e-6))

    def enable_output(self, state):
        # Enables or disables the output of the device by utilizing the appropriate command "enable_output" or "disable_output" specified in the configuration file
        if state:
            cmd = self.config['commands']['enable_output']
        else:
            cmd = self.config['commands']['disable_output']
        if cmd:
            self.device.write(cmd)

    def set_voltage(self, voltage):   #Available only for SMUs
        # Sets the voltage at the device with the "set_voltage" command specified in the configuration file
        cmd = self.config['commands']['set_voltage']
        if cmd:
            self.device.write(cmd.format(voltage=str(voltage)))

    def set_frequency(self, frequency):  # Available only for LCRs
        # Sets the frequency at the device with the "set_frequency" command specified in the configuration file
        cmd = self.config['commands']['set_frequency']
        if cmd:
            self.device.write(cmd.format(frequency=str(frequency)))

    def measure_voltage(self):  #Available only for SMUs
        # Queries the device voltage with the "measure_voltage" command specified in the configuration file
        cmd = self.config['commands']['measure_voltage']
        if cmd:
            voltage = float(self.device.query(cmd))
            return voltage
    
    def measure_current(self):  #Available only for SMUs
        # Queries the device current with the "measure_current" command specified in the configuration file
        cmd = self.config['commands']['measure_current']
        if cmd:
            current = float(self.device.query(cmd))
            return current

    def measure(self):  #Available only for Multimeters
        # Queries the device measurement with the "measure" command specified in the configuration file
        cmd = self.config['commands']['measure']
        if cmd:
            measurement = float(self.device.query(cmd))
            return measurement

    def read_output(self):   #Only for LowV PS
        # Queries the output voltage and current of the device using the "read_voltage"/"read_current" commands specified in the configuration file, iterates through all channels.
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
        # Queries the device frequency with the "measure_frequency" command specified in the configuration file
        cmd = self.config['commands']['measure_frequency']
        if cmd:
            measurement = float(self.device.query(cmd))
            return measurement

    def measure_impedance_phase(self): #Only for LCR
        # Queries the device impedance phase with the "measure_impedance_phase" command specified in the configuration file
        cmd = self.config['commands']['measure_impedance_phase']
        if cmd:
            measurement = float(self.device.query(cmd))
            return measurement

    def set_voltage_range(self, range):
        # Sets the voltage range at the device with the "set_voltage_range" command specified in the configuration file (auto requires special commands unfortunately)
        ranges = { #Available ranges on all the devices. If your new decvice has different options, you should add them here
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
            if range == "Auto":
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
        # Sets the current range at the device with the "set_current_range" command specified in the configuration file (auto requires special commands unfortunately)
        ranges = { #Available ranges on all the devices. If your new device has different options, you should add them here
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
            if range == "Auto":
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

    def set_resistance_range(self, range):
        # Sets the resistance range at the device with the "set_resistance_range" command specified in the configuration file (auto requires special commands unfortunately)
        range_dic = { #Available ranges on all the devices. If your new device has different options, you should add them here
            '100 Ohm': 100,
            '1k Ohm': 1000,
            '10k Ohm': 10000,
            '100k Ohm': 100000,
            '1M Ohm': 1000000,
            '10M Ohm': 10000000,
            'Auto': 'AUTO'
        }
        if range is not None:
            if range == "Auto":
                cmd = self.config['commands']['set_resistance_range_auto_on']
                if cmd:
                    self.device.write(cmd)
            else:
                cmd = self.config['commands']['set_resistance_range_auto_off']
                if cmd:
                    self.device.write(cmd)
                cmd = self.config['commands']['set_resistance_range'].format(range=range_dic[range])
                if cmd:
                    self.device.write(cmd)

    def set_nplc(self, nplc):
        # Sets the NPLC (Number of Power Line Cycles) at the device with the "set_nplc" command specified in the configuration file
        cmd = self.config['commands']['set_nplc'].format(nplc=nplc)
        if cmd:
            self.device.write(cmd)

    def set_filter(self, filter, filter_num, filter_type):
        # Sets the filter at the device with commands (enable/disable_filter, set_filter_num, set_filter_type) specified in the configuration file
        filter_type_dic = {
            "Moving Average": "MOV",
            "Repeat Average": "REP"
        }
        if filter:
            cmd = self.config['commands']['enable_filter']
            if cmd:
                self.device.write(cmd)
        else:
            cmd = self.config['commands']['disable_filter']
            if cmd:
                self.device.write(cmd)
        cmd = self.config['commands']['set_filter_num'].format(filter_num=filter_num)
        if cmd:
            self.device.write(cmd)
        cmd = self.config['commands']['set_filter_type'].format(filter_type=filter_type_dic[filter_type])
        if cmd:
            self.device.write(cmd)

    def set_auto_zero(self, state):
        if state:
            cmd = self.config['commands']['enable_auto_zero']
            if cmd:
                self.device.write(cmd)
        else:
            cmd = self.config['commands']['disable_auto_zero']
            if cmd:
                self.device.write(cmd)

    def set_highC(self, state):
        # Sets the High C state at the device with the "set_highC" command specified in the configuration file
        if state:
            print(self.assigned_id, "Enabled High C")
            cmd = self.config['commands']['enable_highC']
            if cmd:
                self.device.write(cmd)
        else:
            print(self.assigned_id, "Disabled High C")
            cmd = self.config['commands']['disable_highC']
            if cmd:
                self.device.write(cmd)

    def set_measurement_type(self, quantity):
        # Sets the measurement type at the device with the "set_measurement_type" command specified in the configuration file (Multimeter only)
        quantity_dic = {
            'Voltage DC': 'VOLT:DC',
            'Current DC': 'CURR:DC',
            'Resistance (2 Wire)': 'RES',
            'Voltage AC': 'VOLT:AC',
            'Current AC': 'CURR:AC',
            'Resistance (4 Wire)': 'FRES',
            'Frequency': 'FREQ',
            'Period': 'PER'
        }
        cmd = self.config['commands']['set_measurement_type'].format(quantity=quantity_dic[quantity])
        if cmd:
            self.device.write(cmd)