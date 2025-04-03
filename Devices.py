# This file contains the classes for the supported devices. If any device needs to be added, a new class should be created here.
# The class should contain the following methods:
# - __init__(self, port, rm): Constructor that initializes the device
# - reset(self): Resets the device
# - return_id(self): Returns the identification string of the device
# - close(self): Closes the connection to the device
# - Other methods that are specific to the device like measuring voltage, current, etc.
# Currently supported devices: Keithley 2000 Voltmeter, Keithley 2200 SMU, Keithley 2600 SMU, Rhode&Schwarz NGE100 Power Supply and HAMEG HMP4040 Power Supply 

class Dummy_Device: # Dummy Device for testing purposes
    def __init__(self, port, rm): 
        self.port = port
        self.reset()

    def reset(self):
        print('Resetting Dummy')
        

    def clear_buffer(self):
        print('Clearing Dummy Buffer')
        
    def return_port(self):
        return self.port

    def return_id(self):
        return 'Dummy Device'
    
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
    def __init__(self, port, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.device.write('RST*')

    def reset(self):
        self.device.write('RST*')

    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?')
    
    def close(self):
        self.device.close()

    def measure_voltage(self):
        self.device.write('SENS:FUNC "VOLT:DC"')
        voltage = self.device.query('READ?')
        return voltage
    
    def measure_resistance(self):
        self.device.write('SENS:FUNC "RES"')
        resistance = self.device.query('READ?')
        return resistance
    
class K2200:
    def __init__(self, port, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.reset()
        self.clear_buffer()

    def reset(self):
        self.device.write('RST*')

    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?')
    
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
    def __init__(self, port, rm):
        self.device = rm.open_resource(port)
        self.port = port
        self.device.reset()
        self.device.clear_buffer()
        self.device.write(':SOUR:FUNC VOLT') # Sets Source to voltage mode (needed for IV Curves)
        self.device.write(':SOUR:VOLT 0') #Sets the output voltage to 0

    def reset(self):
        self.device.write('RST*')

    def clear_buffer(self):
        self.device.write('*CLS')

    def return_port(self):
        return self.port

    def return_id(self):
        return self.device.query('*IDN?')
    
    def close(self):
        self.device.close()

    def enable_output(self, enable):
        if enable:
            self.device.write(':OUTP ON')
        else:
            self.device.write(':OUTP OFF')

    def set_limit(self, limitI):
        self.device.write(f':SENS:CURR:PROT {str(limitI)}')

    def set_voltage(self, voltage):
        self.device.write(f':SOUR:VOLT {str(voltage)}')

    def measure_current(self):
        current = float(self.device.query(':MEAS:CURR?').strip('\n'))
        return current

    def measure_voltage(self):
        voltage = float(self.device.query(':MEAS:VOLT?').strip('\n'))
        return voltage

class K2600: #K2600 SMU (up to 200V bias Voltage)
    def __init__(self, port, rm):
        self.device = rm.open_resource(port)
        self.port = port
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

class LowVoltagePowerSupplies: #Rhode&Schwarz NGE 100 and HAMEG HMP4040 
    def __init__(self,  port, rm):
        self.device = rm.open_resource(port)
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