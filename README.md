# IVVMaker
This piece of software is intended to be used to measure various electrical parameters of devices under test (DUTs) using a variety of devices. The software is designed to be modular and easy to use, allowing users to add support for new devices and customize the measurement process. The software is written in Python and uses the PyQt5 library for the GUI. It also uses the PyVISA library for communication with the devices.
## Feautures
- Modular design: The software is designed to be modular, allowing users to add support for new devices and customize the measurement process.
- Easy to use GUI: The software has a user-friendly GUI that allows users to easily configure the measurement process and view the results.
- Support for a range of devices. It currently includes support for:
    - Keithley 2200 series SMUs
    - Keithley 2400 series SMUs
    - Keithley 2600 series SMUs
    - Keithley 2000 series DMMs
    - Hameg HMP 4000 series power supply
    - Rhode&Schwarz NGE100 series power supply
    - Keithley 6487 piccoammeter
    - Hameg 8118 LCR Bridge
- The following measurements are supported:
    - Current-Voltage characteristics (I-V curves) 
    - Constant voltage measurement (I-t curves)
    - Capacitance-voltage characteristics (C-V curves)
    - Tracking of additional parameters (e.g. resistances, voltages, power use, etc.) for all three measurement types
## File structure
- `main.py` : Main file to start the application
- `devices.py`: File containing the classes for the devices. This is where you can add support for additional devices.
- `measurement_thread.py`: File containing the class for the measurement thread. This is where the actual measurement is done.
- `ui.py`: File containing the class for the GUI. This is where the GUI is created. The logic behind the GUI is not handled in this file.
- `logic.py`: File containing the class for the functionality of the application. This is where the logic behind the GUI is handled.#
- `data_handler.py`: File containing the class for the data handling. This is where the data saving is handled.
- `plotting.py`: File containing the class for the plotting. This is where the plotting of the live data is handled.
- `config_manager.py`: File containing the class to save and load configs for your measurement.
- `parameter_dialog.py`: File containing the classes for the parameter dialogs. This handles the advanced settings for the devices.
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
ResourceManager = pyvisa.ResourceManager('@py') # for the pure python backend

ResourceManager = pyvisa.ResourceManager('@ni') # for the NI-VISA backend
```
  If you use the python backend, be sure you install `pyusb` and `pyserial` to be able to communiate with the devices over USB and serial.
  
For more information on how to install the backends, please refer to the [pyvisa documentation](https://pyvisa.readthedocs.io/en/).

## Usage
### Performing measurements 
1. Start the application
```bash
python main.py
```
2. Search for connected devices using the "Search Devices" button in the GUI. The devices should be listed in the "Select Device" menu. If you want to use a device, select it and click on the "Add selected Device" button. The device should now be connected and ready to use. 

    If you know what you're doing you can use the "Search and add all connected Devices". This is only recommended if you are sure that you want to use all the devices connected to your computer.
    
    The device should now be listed in the "Connected Devices" menu. There you have the option to remove the device from this list if you dont want to use it in your measurement. Additional you can reset the device and clear its buffer. For some devices advanced settings are available. These can be used to further configure the device (usage of fixed ranges, filters, etc.). Feel free to add additional settings for your device in the `parameter_dialog.py` file. Currently only available for the Keithley K2600 series and K2000 series.

    To support additional devices, you can add them to the `devices.py` file. Additionally you need to add them to the logic in the `logic.py` to properly include them. Only do this if really needed.   

3. Choose which kind of measurement you want to perform. The options are:
    - I-V curve measurement
    - Constant voltage measurement
    - C-V curve measurement
    
    After choosing your measurement type, you can set the parameters for the measurement. All of the parameters are more or less self-explanatory. If you are unsure what a parameter does, test it. Entering invalid parameters will result in an error message. Be aware that to start a measurement at least one SMU device has to be connected. For the C-V measurement at least one LCR bridge has to be connected as well. The IV and CV measurement will auomatically stop after the sweep has concluded. The constant voltage measurement can only be stopped by manually aborting the measurement.
4. During the measurement, the recorded data will be shown in the plot.
    The plot will be updated in real time. The toolbar can be used to visually edit the plot directly in the GUI. You also have the option to include older mesaurements in the plot by using the "Load Data" button. Please be sure that the measurement you are loading is of the same type as the one you are currently performing. Otherwise this could lead to problems. Be also aware that for a CV measurement not the capacitance but rather the current from the SMU is plotted. This is due to the fact that the capacitance must be calculated using the data from the LCR bridge. As this calculation is dependent on the model you are using, this is not done live. If you perform a CV measurement you probably also know how to calculate the capacitance from the data. If not refer to the manual of the LCR bridge (eg. [Hameg 8118](https://www.rohde-schwarz.com/de/handbuch/hm8118-lcr-messbruecke-bedienhandbuch-handbuecher_78701-156992.html)) for more information.

5. During the measurement all accumulated data is saved to a file. The file will be saved in the folder specified in the GUI. The default is `cwd/data`. You can choose which format is used for the data, but `.csv` is recommended. Along with the data, a log file will be created. This file contains all the settings and devices with their settings used for the measurement. 

6. After the measurement is finished, you can save the data to a file. The file will be saved in the folder specified in the GUI. The default is `cwd/data`. You can choose which format is used for the data, but `.csv` is recommended. Along with the data, a log file will be created. This file contains all the settings and devices with their settings used for the measurement.
    
    The first column of the data file contains the target voltage for every measurement. After that follows the data from the SMUs with Voltage | Current. The next columns depend on the devices you are using. Each row is one measurement done at the target voltage.   

### Saving and loading configs
If you close te program the current settings are saved to the at `latest.json` config file and loaded again if you start the application the next time. Additional you have the option to save customized configs using the respective button. These manually saved configs can also be loaded again. 

## Contributing
If you want to contribute to the project, feel free to fork the repository and create a pull request. If you have any questions or suggestions, please open an issue on GitHub or contact me directly via [E-Mail](mailto:kuhn@physi.uni-heidelberg.de)