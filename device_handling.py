import pyvisa as visa
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

        # Lists of supported devices, these are used to check if a device is supported
        # If you want to add a new device, you need to add it here in its respective category

        self.smu_supported_devices = ['Keithley K2200 SMU', 'Keithley K2400 SMU', 'Keithley K2600 SMU', 'Keithley K6487 SMU'] # List of supported SMU devices
        self.voltmeter_supported_devices = ['Keithley K2000 Voltmeter'] # List of supported voltmeter devices
        self.lowV_supported_devices = ['HAMEG HMP4040', 'Rhode&Schwarz NGE103B'] # List of supported low voltage power supply devices
        self.capacitancemeter_supported_devices = ['HAMEG HM8118 LCR'] # List of supported capacitance meter devices

    def find_devices(self):
        self.ports = self.rm.list_resources() # search devices and clear all canidates for that, to prevent double entries
        self.clear()
#        self.device_candidates.append(['Dummy Port', 'Dummy Device', 'Dummy']) # Add a dummy device for testing purposes
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
            if id in self.used_ids: # Check if the device is already in use
                print(id, ' already in use')
                continue
            if 'Keithley' in id and '2200' in id:
                self.device_candidates.append([port, id, 'Keithley K2200 SMU'])
            elif 'KEITHLEY' in id and ('2470' in id or '2450' in id):
                self.device_candidates.append([port, id, 'Keithley K2400 SMU'])
            elif 'Keithley' in id and '2611' in id:
                self.device_candidates.append([port, id, 'Keithley K2600 SMU'])
            elif 'KEITHLEY' in id and 'MODEL 6487' in id:
                self.device_candidates.append([port, id, 'Keithley K6487 SMU'])
            elif 'KEITHLEY' in id and '2000'in id:
                self.device_candidates.append([port, id, 'Keithley K2000 Voltmeter'])
            elif 'NGE103B' in id:
                self.device_candidates.append([port, id, 'Rhode&Schwarz NGE103B'])
            elif 'HMP4040' in id: 
                self.device_candidates.append([port, id, 'HAMEG HMP4040'])
            elif 'HM8118' in id:
                self.device_candidates.append([port, id, 'HAMEG HM8118 LCR'])
            else:
                self.device_candidates.append([port, id, 'Uncharacterized'])
            device.close()
        print('Found devices:', self.device_candidates)
        return np.array(self.device_candidates)


    def add_decvice(candidate_id, self):
        #This function adds a device to the list of used devices
        candidate = self.device_candidates[candidate_id]
        if candidate[2] in self.smu_supported_devices:
            self.smu_devices.append(candidate)
            self.used_ids.append(candidate[1])
        elif candidate[2] in self.voltmeter_supported_devices:
            self.voltmeter_devices.append(candidate)
            self.used_ids.append(candidate[1])
        elif candidate[2] in self.lowV_supported_devices:
            self.lowV_devices.append(candidate)
            self.used_ids.append(candidate[1])
        elif candidate[2] in self.capacitancemeter_supported_devices:
            self.capacitancemeter_devices.append(candidate)
            self.used_ids.append(candidate[1])
            



    def clear(self):
        self.device_candidates = []
