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
        # This function will assemble the config dictionary with all the parameters of a measurement. 
        config = {
            'sweep': not self.ui.fixed_voltage_checkBox.isChecked(),
            'start_voltage': self.ui.startV.value(),
            'stop_voltage': self.ui.stopV.value(),
            'step_voltage': self.ui.stepV.value(),
            'time_between_steps': self.ui.time_between_steps.value(),
            'time_between_measurements': self.ui.time_between_measurements.value(),
            'measurements_per_step': self.ui.measurements_per_step.value(),
            'limit_current': self.ui.limitI.value(),
            'constant_voltage' : self.ui.fixed_voltage.value(),
            'custom_sweep': self.ui.use_custom_sweep_checkBox.isChecked(),
            'custom_sweep_filepath': self.ui.custom_sweep_file.text(),
            'filename_suffix': self.ui.filename_suffix.currentIndex(),
            'darkmode': self.ui.logic.darkmode
        }
        return config

    def apply_config(self, config):
        # This function will extract the parameters from a given config and set them accordingly.
        try:
            self.ui.fixed_voltage_checkBox.setChecked(not config['sweep'])
            self.ui.startV.setValue(config['start_voltage'])
            self.ui.stopV.setValue(config['stop_voltage'])
            self.ui.stepV.setValue(config['step_voltage'])
            self.ui.time_between_steps.setValue(config['time_between_steps'])
            self.ui.time_between_measurements.setValue(config['time_between_measurements'])
            self.ui.measurements_per_step.setValue(config['measurements_per_step'])
            self.ui.limitI.setValue(config['limit_current'])
            self.ui.fixed_voltage.setValue(config['constant_voltage'])
            self.ui.use_custom_sweep_checkBox.setChecked(config['custom_sweep'])
            self.ui.custom_sweep_file.setText(config['custom_sweep_filepath'])
            self.ui.filename_suffix.setCurrentIndex(config['filename_suffix'])
            self.ui.logic.darkmode = config['darkmode']
            self.ui.logic.update_darkmode()
            self.ui.logic.enable_fixed_voltage()
            self.ui.logic.enable_custom_sweep
        except Exception as e:
            print('Settin config failed', e)
        return

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



