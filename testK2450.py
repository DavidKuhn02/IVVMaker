import pyvisa as visa

rm = visa.ResourceManager('@py')

ports = rm.list_resources()
for port in ports:
    print(port)
    try:
        device = rm.open_resource(port)
        print(device.query('*IDN?'), )
        
    except Exception as e:
        print(f"Error: {e}")

device.write('*RST')
device.write('*CLS')
device.write("*LANG SCPI")
device.write(':SOUR:FUNC VOLTage') # Sets Source to voltage mode (needed for IV Curves)
#device.write(':SOUR:VOLT 0') #Sets the output voltage to 0     

device.close()