# This file contains the classes for the supported devices. If any device needs to be added, a new class should be created here.
# The class should contain the following methods:
# - __init__(self, port, rm): Constructor that initializes the device
# - reset(self): Resets the device
# - return_id(self): Returns the identification string of the device
# - return_assigned_id(self): Returns the port of the device
# - close(self): Closes the connection to the device
# - clear_buffer(self): Clears the buffer of the device
# - return_port(self): Returns the port of the device
# - enable_output(self, enable): Enables or disables the output of the device
# - set_voltage(self, voltage): Sets the voltage of the device
# - set_limit(self, limitI): Sets the current limit of the device
# - measure_current(self): Measures the current output of the device
# - measure_voltage(self): Measures the voltage at the device
# - measure_resistance(self): Measures the resistance at the device
# - read_output(self): Reads the output low voltage power devices
# - enable_highC(self, highC): Enables or disables the high current mode of the device (Currently only for K2600)
# - return_num_channels(self): Returns the number of channels of the device (Currently only for Rhode&Schwarz NGE100 and HAMEG HMP4040)
# Currently supported devices: Keithley 2000 Voltmeter, Keithley 2200 SMU, Keithley 2600 SMU, Rhode&Schwarz NGE100 Power Supply and HAMEG HMP4040 Power Supply 

class Dummy_Device: # Dummy Device for testing purposes
    def __init__(self, port, id, rm): 
        self.port = port
        self.assigned_id = id
        self.reset()

    def reset(self):
        print('Resetting Dummy')
        
    def clear_buffer(self):
        print('Clearing Dummy Buffer')
        
    def return_port(self):
        return self.port

    def return_id(self):
        return 'Dummy Device'
    
    def return_assigned_id(self):
        return self.assigned_id

    def close(self):
        print('Closing Dummy')
        
    def measure_voltage(self):
        return 1
    
    def measure_resistance(self):
        return 1
    
    def enable_output(self, enable):
        print('Output on Dummy Enabled')
        
    def set_limit(self, limitI):
        print('Limit set on Dummy ', limitI)
        

    def set_voltage(self, voltage):
        print('Voltage set on Dummy ', voltage)
        
    def measure_current(self):
        return 1

class K2000: # K2000 Voltmeter (able to measure Voltage/Resistance)
    def __init__(self, port, id, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.assigned_id = id
        self.settings = {  #Standard settings for the Keithley 2000 (loaded when the device is connected)
            'measurement_type': 'VOLD:DC',
            'voltage_range': 'Auto',
            'current_range': 'Auto',
            'resistance_range': 'Auto',
            'use_filter': False,
            'filter_num': 10,
            'filter_type': 'Moving Average',
            }
        self.type = 'VOLT:DC'   # Sets the default measurement type to DC Voltage
        self.set_measurement_type(self.type)
        self.reset()
        self.clear_buffer()

    def reset(self):
        self.device.write('*RST')

    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?').strip('').strip('')
    
    def return_assigned_id(self):
        return self.assigned_id
    
    def close(self):
        self.device.close()

    def measure(self):
        return self.device.query('READ?').strip('').strip('').strip('\n').strip()
    
    def set_measurement_type(self, type):
        self.type = type
        self.device.write('SENS:FUNC "{}"'.format(type))

    def update_voltage_range(self, range):
        if range == 'AUTO':
            self.device.write('SENS:VOLT:DC:RANG:AUTO ON')
        else:
            self.device.write('SENS:VOLT:DC:RANG:AUTO OFF')
            self.device.write(f'SENS:VOLT:DC:RANG {range}')

    def update_current_range(self, range):
        if range == 'AUTO':
            self.device.write('SENS:CURR:DC:RANG:AUTO ON')
        else:
            self.device.write('SENS:CURR:DC:RANG:AUTO OFF')
            self.device.write(f'SENS:CURR:DC:RANG {range}')

    def update_resistance_range(self, range):
        if range == 'AUTO':
            self.device.write('SENS:RES:RANG:AUTO ON')
        else:
            self.device.write('SENS:RES:RANG:AUTO OFF')
            self.device.write(f'SENS:RES:RANG {range}')
 
    def update_filter(self, filter, filter_type, filter_num):
        
        if filter:
            self.device.write(f'SENS:{self.type}:AVER:STAT ON')
        else:
            self.device.write(f'SENS:{self.type}:AVER:STAT OFF')
        self.device.write(f'SENS:{self.type}:AVER:COUNT {str(filter_num)}')
        if filter_type == 'Moving Average':
            self.device.write(f'SENS:{self.type}:AVER:TCON MOV')
        elif filter_type == 'Repeat Average':
            self.device.write(f'SENS:{self.type}:AVER:TCON REP')
        

class K2200:
    def __init__(self, port, id, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.assigned_id = id
        self.reset()
        self.clear_buffer()

    def reset(self):
        self.device.write('*RST')

    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?')
    
    def return_assigned_id(self):
        return self.assigned_id
    
    def close(self):
        self.device.close()

    def enable_output(self, enable):
        if enable:
            self.device.write('OUTPUT ON')
        else:
            self.device.write('OUTPUT OFF')
    
    def set_limit(self, limitI):
        self.device.write('CURR {:.4f}'.format(limitI))

    def set_voltage(self, voltage):
            self.device.write('VOLT {:.4f}'.format(abs(voltage)))
    
    def measure_current(self):
        current = float(self.device.query('MEAS:CURR?').strip('\n'))
        return current

    def measure_voltage(self):
        voltage = float(self.device.query('MEAS:VOLT?').strip('\n'))
        return voltage

class K2400:
    def __init__(self, port, id, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.assigned_id = id
        self.settings = { #Standard settings for the Keithley 2400 (loaded when the device is connected)
            'voltage_range': 'Auto',
            'current_range': 'Auto',
            'nplc': 1,
            'high_capacitance': False,
            'use_filter': False,
            'filter_num': 10,
            'filter_type': 'Moving Average',
            'auto_zero': True,
        }
        self.reset()
        self.clear_buffer()
        self.device.write(':SOUR:FUNC VOLT') # Sets Source to voltage mode (needed for IV Curves)
        self.device.write(':SOUR:VOLT 0') #Sets the output voltage to 0

    def reset(self):
        self.device.write('*RST')

    def clear_buffer(self):
        self.device.write('*CLS')
        self.device.write('TRAC:CLE "defbuffer1"')
        self.device.write('TRAC:CLE "defbuffer2"')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?')
    
    def return_assigned_id(self):
        return self.assigned_id
    
    def close(self):
        self.device.close()

    def enable_highC(self, highC):
        if highC:
            self.device.write(':SOUR:VOLT:HIGH:CAP ON')
        else:
            self.device.write(':SOUR:VOLT:HIGH:CAP OFF')
    
    def set_voltage_range(self, range):
        if range == 'Auto':
            self.device.write(':SOUR:VOLT:RANG:AUTO ON')
        else:
            self.device.write(':SOUR:VOLT:RANG:AUTO OFF')
            self.device.write(f':SOUR:VOLT:RANG {range}')
    
    def set_current_range(self, range):
        if range == 'Auto':
            self.device.write(':SENS:CURR:RANG:AUTO ON')
        else:
            self.device.write(':SENS:CURR:RANG:AUTO OFF')
            self.device.write(f':SENS:CURR:RANG {range}')

    def set_filter(self, filter, filter_type, filter_num):
        self.device.write(f':SENS:CURR:AVER:COUN {str(filter_num)}')
        if filter_type == 'Moving Average':
            self.device.write(f':SENS:CURR:AVER:TCON MOV')
        elif filter_type == 'Repeat Average':
            self.device.write(f':SENS:CURR:AVER:TCON REP')
        if filter:
            self.device.write(':SENS:CURR:AVER ON')
        else:
            self.device.write(':SENS:CURR:AVER OFF')

    def set_nplc(self, nplc):
        self.device.write(f':SENS:CURR:NPLC {str(nplc)}')

    def set_auto_zero(self, auto_zero):
        if auto_zero:
            self.device.write(':SENS:CURR:AZER ON')
        else:
            self.device.write(':SENS:CURR:AZER OFF')

    def enable_output(self, enable):
        if enable:
            self.device.write(':OUTP ON')
        else:
            self.device.write(':OUTP OFF')

    def set_limit(self, limitI):
        self.device.write(f':SOUR:VOLT:ILIM {str(limitI)}')

    def set_voltage(self, voltage):
        self.device.write(f':SOUR:VOLT {str(voltage)}')

    def measure_current(self):
        current = float(self.device.query(':MEAS:CURR?').strip('\n'))
        return current

    def measure_voltage(self):
        voltage = float(self.device.query(':MEAS:VOLT?').strip('\n'))
        return voltage

class K2600: #K2600 SMU (up to 200V bias Voltage)
    def __init__(self, port, id, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.assigned_id = id
        self.reset()

    def reset(self):
        self.set_voltage(0)
        self.enable_output(False)

    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?')
    
    def return_assigned_id(self):
        return self.assigned_id
    
    def close(self):
        self.device.close()

    def enable_output(self, enable):
        if enable:
            self.device.write('smua.source.output = smua.OUTPUT_ON')
        else:
            self.device.write('smua.source.output = smua.OUTPUT_OFF')

    def set_limit(self, limitI):
        self.device.write(f'smua.source.limiti= {str(limitI)}')   

    def enable_highC(self, highC):
        if highC:
            self.device.write('smua.source.highc = smua.ENABLE')
        else:
            self.device.write('smua.source.highc = smua.DISABLE')

    def set_voltage(self, voltage):
        self.device.write('smua.source.levelv={:.1f}'.format(voltage))

    def measure_current(self):
        current = self.device.query('print(smua.measure.i())').strip('\n')
        return current
    
    def measure_voltage(self):
        voltage = self.device.query('print(smua.measure.v())').strip('\n')
        return voltage
    

class K6487: #K6487 Voltage source/piccoammeter 
    def __init__(self, port, id, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.assigned_id = id
        self.reset()
        self.voltage = 0 #As the device can only measure current, the voltage that is returned is the same as the set voltage.
    
    def reset(self):
        self.device.write('*RST')
        self.device.write('SOUR:FUNC VOLT')
        self.device.write('SOUR:VOLT 0')
        self.device.write('SOUR:VOLT:STAT OFF')
    
    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port
    
    def return_id(self):
        return self.device.query('*IDN?')
    
    def return_assigned_id(self):
        return self.assigned_id
    
    def close(self):
        self.device.close()

    def enable_output(self, enable):
        if enable:
            self.device.write('SOUR:VOLT:STAT ON')
        else:
            self.device.write('SOUR:VOLT:STAT OFF')

    def set_limit(self, limitI):
        return
    
    def set_voltage(self, voltage):
        self.device.write(f'SOUR:VOLT {voltage}')
        self.voltage = voltage

    def measure_current(self):
        data = self.device.query('READ?')
        data = data.split(',')  
        current = float(data[0].strip('A'))
        return current

    def measure_voltage(self):
        return self.voltage

class LowVoltagePowerSupplies: #Rhode&Schwarz NGE 100 and HAMEG HMP4040 
    def __init__(self,  port, id, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.return_assigned_id = id
        self.device.write('*RST')
        #Test if the device is a Rhode&Schwarz NGE 100 or a HAMEG HMP4040 by testing if channel 4 exists (only i  HAMEG). Should maybe be changed in seperate classes, if more functionallity is needed.
        self.device.write('INST:NSEL 4')
        if int(self.device.query('INST:NSEL?')) == 4:
            self.number_of_channels = 4
        else:
            self.number_of_channels = 3
        self.port = port

    def reset(self):
        self.device.write('RST*')

    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?')
    
    def return_assigned_id(self):
        return self.return_assigned_id
    
    def return_num_channels(self):
        return self.number_of_channels
    
    def close(self):
        self.device.close()

    def read_output(self):
        U = []
        I = []
        for i in range(self.number_of_channels):
            self.device.write(f'INST:NSEL {i}')
            I.append(float(self.device.query('MEAS:CURR?')))
            U.append(float(self.device.query('MEAS:VOLT?')))
        
        return U, I

class Hameg8118:
    def __init__(self, port, id, rm):
        self.device = rm.open_resource(port, read_termination='\r', write_termination='\r')
        self.port = port
        self.assigned_id = id
        self.clear_buffer()
        self.device.write('FUNC ZTD')
        self.device.write('DISP:FORM ZTD')

    def reset(self):
        pass #Does not work on Hameg8118 (breaks the communication)
        
    def clear_buffer(self):
        self.device.write('*CLS')
    
    def return_port(self):
        return self.port
    
    def return_id(self):
        print("read_termination:", repr(self.device.read_termination))
        print("write_termination:", repr(self.device.write_termination))
        self.device.write('*IDN?')
        return self.device.read()
    
    def return_assigned_id(self):
        return self.assigned_id
    
    def close(self):
        self.device.close()
    
    def set_frequency(self, frequency):
        self.device.write(f'FREQ {frequency}')

    def set_voltage(self, voltage):
        pass 
    
    def measure_frequency(self):
        return self.device.query('FREQ?')

    def measure_impedance(self):
        return 
    
    def measure_phase(self):
        return
        
    
        