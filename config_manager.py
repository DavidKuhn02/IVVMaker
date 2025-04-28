# This file will be handling saving and loading configs. It will also contain some hardcoded configs, that can be edited here.
# The configs will be saved as dictionaries. In this config all parameters of a measurement excluding the filename will be saved.
# If you close the program it will save the current settings to a config file and load them when you start the program again.
# The config files will be saved in the config folder. The config files will be saved as json files.

import json
import os

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
if not os.path.exists(config_path):
    os.makedirs(config_path)

class config_manager:
    def __init__(self, ui):
        # This function will load the config file from the config folder. 
        # If the file does not exist, it will create a new one with default values.
        self.ui = ui


    def assemble_config(self):
        # This function will assemble the config dictionary with all the parameters of a measurement currently set in respective the ui dicts
        config = { 
            
            'measurement_type' : self.ui.measurement_type,
            'IV' : self.ui.IV_settings,
            'CV' : self.ui.CV_settings,
            'Constant Voltage' : self.ui.constantV_settings, 
            'darkmode' : self.ui.logic.darkmode
        }

        return config

    def apply_config(self, config):
        # This function will extract the parameters from a given config and set them accordingly.
        self.ui.logic.darkmode = config['darkmode']
        self.ui.logic.update_darkmode()
        self.ui.measurement_type_comboBox.setCurrentText(config['measurement_type'])
        if config['measurement_type'] == 'IV':
            sub_config = config['IV']
            self.ui.startV_spinBox.setValue(sub_config['startV'])
            self.ui.stopV_spinBox.setValue(sub_config['stopV'])
            self.ui.stepV_spinBox.setValue(sub_config['stepV'])
            self.ui.time_between_steps_spinBox.setValue(sub_config['time_between_steps'])
            self.ui.time_between_measurements_spinBox.setValue(sub_config['time_between_measurements'])
            self.ui.measurements_per_step_spinBox.setValue(sub_config['measurements_per_step'])
            self.ui.limitI_spinBox.setValue(sub_config['limitI'])
        elif config['measurement_type'] == 'CV':
            sub_config = config['CV']
            self.ui.startV_spinBox.setValue(sub_config['startV'])
            self.ui.stopV_spinBox.setValue(sub_config['stopV'])
            self.ui.stepV_spinBox.setValue(sub_config['stepV'])
            self.ui.start_frequency_spinBox.setValue(sub_config['startFrequency'])
            self.ui.stop_frequency_spinBox.setValue(sub_config['stopFrequency'])
            self.ui.number_of_frequencies_spinBox.setValue(sub_config['number_of_frequencies'])
            self.ui.logarithmic_frequency_steps_checkBox.setChecked(sub_config['logarithmic_frequency_steps'])
            self.ui.time_between_steps_spinBox.setValue(sub_config['time_between_steps'])
            self.ui.time_between_measurements_spinBox.setValue(sub_config['time_between_measurements'])
            self.ui.measurements_per_step_spinBox.setValue(sub_config['measurements_per_step'])
            self.ui.limitI_spinBox.setValue(sub_config['limitI'])
        elif config['measurement_type'] == 'Constant Voltage':
            sub_config = config['Constant Voltage']
            self.ui.constant_voltage_spinBox.setValue(sub_config['constant_voltage'])
            self.ui.time_between_measurements_spinBox.setValue(sub_config['time_between_measurements'])
            self.ui.limitI_spinBox.setValue(sub_config['limitI'])


    def save_config(self, config, filename):
        # Save the config to a json
        with open(os.path.join(config_path, filename), 'w') as f:
            json.dump(config, f, indent=4)
        
    def load_config(self, filename):
        # Load the config from a json
        try:
            with open(os.path.join(config_path, filename), 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print('Config file not found')
            return None
        except json.JSONDecodeError:
            print('Config file is corrupted')
            return None
        except Exception as e:
            print(f'Error loading config file: {e}')
            return None



