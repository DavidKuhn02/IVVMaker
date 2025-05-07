import os
import datetime

class DataSaver:
    #This class is responsible for saving the data to a file
    #It creates the file and writes the data to it
    def __init__(self, filepath, filename, ui, functionality):
        self.functionality = functionality
        self.ui = ui
        self.create_file(filepath=filepath, filename=filename)
        
    def create_file(self, filepath, filename):  
        #This function creates the file and writes the header to it
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filepath = os.path.join(filepath, filename + '_' + timestamp + self.ui.filename_suffix.currentText())
        try:
            self.file = open(self.filepath, 'x', buffering=1)
            self.write_header()
        except FileExistsError:
            raise FileExistsError
        except Exception as e:
            return  
    
    def write_header(self):
        #The header is created based on the devices that are connected
        #It provides information on the different channels which are measured
        self.header = [] 
        self.header.append(f'Target[V]')
        for i in range(len(self.ui.device_handler.smu_devices)):
            self.header.append(f'Voltage_SMU_{i}[V]')
            self.header.append(f'Current_SMU_{i}[A]')
        for i in range(len(self.ui.device_handler.voltmeter_devices)):
            self.header.append(f'Voltage_Voltmeter_{i} [V]')
        for i in range(len(self.ui.device_handler.resistancemeter_devices)):
            self.header.append(f'Resistance_Resistancemeter_{i}[Ohm]')
        for i in range(len(self.ui.device_handler.lowV_devices)):
            num_channels = self.ui.device_handler.resistancemeter_devices[i].return_num_channels()
            if num_channels == 3:
                self.header.append(f'Voltage_lowV_{i}_Channel_1[V] Voltage_lowV_{i}_Channel_2[V] Voltage_lowV_{i}_Channel_3[V] Current_lowV_{i}_Channel_1[A] Current_lowV_{i}_Channel_2[A] Current_lowV_{i}_Channel_3[A]')
            else:
                self.header.append(f'Voltage_lowV_{i}_Channel_1[V] Voltage_lowV_{i}_Channel_2[V] Voltage_lowV_{i}_Channel_3[V] Voltage_lowV_{i}_Channel_4[V] Current_lowV_{i}_Channel_1[A] Current_lowV_{i}_Channel_2[A] Current_lowV_{i}_Channel_3[A] Current_lowV_{i}_Channel_4[A]')
        for i in range(len(self.ui.device_handler.capacitancemeter_devices)):
            self.header.append(f'Impedance_capacitancemeter_device{i}')
            self.header.append(f'Phase_capacitancemeter_device{i}')
            self.header.append(f'Frequency_capacitancemeter_device{i}')
        self.file.write(' '.join(self.header)+ '\n') 
        

    def write_data(self, data):
        #This function writes the data to the file
        data_string = ' '.join(map(str, data)) + '\n'
        try:
            self.file.write(data_string)
        except:
            print('Data could not be safed')

    def close(self):
        #This function closes the file
        self.file.close()