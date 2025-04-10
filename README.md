# IVVMaker
This piece of software is intended to be used to measure IV characteristics of electronic devices using a SMU. It features a user friendly GUI to control your measurement.

## Feautures
- GUI to set the parameters for the measurement and control the devices for the measurement
- Real time plotting of the data during the measurement
- Currently implemented devices:
    - SMU (__Keithley 2200__ series, __Keithley 2400__ series, __Keithley 2600__ series)
    - Voltage Meter (__Keithley 2000__ series)
    - Resistance Meter (__Keithley 2000__ series)
    - Low Voltage Power Supply (__HAMEG HMP4040__ series, __Rhode & Schwarz NGE100__ series) 

## File structure
- main.py: Main file to start the application
- Devices.py: File containing the classes for the devices. This is where you can add support for additional devices.
- MeasurementThread.py: File containing the class for the measurement thread. This is where the actual measurement is done.
- UI.py: File containing the class for the GUI. This is where the GUI is created. The logic behind the GUI is not handled in this file.
- Functionallity.py: File containing the class for the functionality of the application. This is where the logic behind the GUI is handled. Also the data save class and the devices are handled here.
- Plotting.py: File containing the class for the plotting. This is where the plotting of the live data is handled.
## Installation
1. Clone the repository
```bash 
git clone https://github.com/DavidKuhn02/IVVMaker.git
```
2. Install the required packages
```bash
pip install -r requirements.txt
```
3. Decide which backend for visa you want to use. The default is pyvisa-py, which is a pure python implementation of the NI-VISA standard. If you want to use the native backend, you need to install pyvisa and the appropriate backend for your operating system. You will also have to change the definition of the `ResourceManager` in the `Main.py` file:
```python 
self.rm = pyvisa.ResourceManager('@py') # for the pure python backend

self.rm = pyvisa.ResourceManager('@ni') # for the NI-VISA backend
```
  If you use the python backend, be sure you install `pyusb` and `pyserial` to be able to communiate with the devices over USB and serial.


For more information on how to install the backends, please refer to the [pyvisa documentation](https://pyvisa.readthedocs.io/en/).

## Usage
1. Start the application
```bash
python main.py
```
2. Search for connected devices using the "Search Devices" button in the GUI. The devices should be listed in the "Select Device" menu. If you want to use a device, select it and click on the "Add selected Device" button. The device should now be connected and ready to use. If you know what you're doing you can use the "Search and add all connected Devices". This is only recommended if you are sure that you want to use all the devices connected to your computer.
The device should now be listed in the "Connected Devices" menu. There you the option to remove the device from this list if you dont want to use it in your measurement. Additional you can reset the device and clear its buffer. For some devices additional options are available. For example you can choose if the device should measure a voltage or current.
If you want to add support for additional devices, you can do this by creating a new class in the device file.

3. Enter the parameters for the measurement. You can choose between a voltage sweep or a measurement with a constant applied voltage.
The parameters are:
    - __Start Voltage__: The starting voltage for the measurement. This is only used for a voltage sweep.
    - __Stop Voltage__: The stopping voltage for the measurement. This is only used for a voltage sweep.
    - __Step Voltage__: The step voltage for the measurement. This is only used for a voltage sweep.
    - __Time between steps__: The time between each step in the measurement to enable built up charges to decay. This is only used for a voltage sweep.
    - __Time between measurements__: The time between each measurement.
    - __Measurements per step__: The number of measurements to take at each step. This is only used for a voltage sweep. 
    - __Current Limit__: The current limit for the measurement. This is important to set appropiate for the DUT to avoid damage.
    - __Constant Voltage__: The constant voltage to apply to the DUT. This is only used for a constant voltage measurement.
    - __Custom Sweep__: Select custom sweep file for your measurement. This file should be a csv file with the following format:
        - Column 1: Voltages for your sweep
        - Column 2: Number of measurements for each voltage 
    - __File Name__: The name of the file to save the measurement to. You can select the path for your data individually, the default path is IVVMaker/data/
    - __File Format__: The format of the file to save the measurement to. The default format is csv, with ' ' as delimiter. 

4. During the measurement, the recorded data will be shown in the plot. The plot will be updated in real time. If you do a voltage sweep, the plot will show the current as a function of the voltage. If you do a constant voltage measurement, the plot will show the current as a function of time. You can set custom limits for the plot to be able to zoom in on the data. You are also able to load the data from a previous measurement. Please note that only the data of the first connected SMU is plotted in the live view for now. The data of the other devices is saved in the file, but not plotted in the live view. This could be added in a future version. If you load a constant voltage measurement, note that the time between measurements is not saved in the file. This means that the time axis could be wrong, as it uses the current value of the time between measurements. This can also be fixed in the furture. 

5. After the measurement is finished, the data will be saved to the file you specified. The data will be saved in the format you specified. The default format is csv, with ' ' as delimiter. The data will be saved in the following format:
- Column 1: Voltage of SMU0
- Column 2: Current of SMU0
If more decvices are connected, the next columns will be the data of additional SMUs, after that possible voltage meters and resistance meters will be saved. At the end the voltage and currents of the low voltage power supplies will be saved. 

    The data will have two lines of header, the first one being either the number of steps taken in the sweep (for sweep measurements) or the time between measurements (for constant voltage measurements). This is done to simplify the analysis and not strictly needed. Be aware that while loading data in the plot, the first two lines of the data fil will always be skipped, as the header is expected there.

