import os
import datetime

class DataSaver():
    #This class is responsible for saving the data to a file
    #It creates the file and writes the data to it
    def __init__(self, filepath, filename, ui, functionality, sweep):
        self.functionality = functionality
        self.ui = ui
        self.sweep = sweep
        self.create_file(filepath, filename)
        
    def create_file(self, filepath, filename):  
        #This function creates the file and writes the header to it
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filepath = os.path.join(filepath, filename + '_' + timestamp + self.ui.filename_suffix.currentText())

        try:
            self.file = open(self.filepath, 'x', buffering=1)
            self.write_header()
        except FileExistsError:
            raise FileExistsError
            return
    
    def write_header(self):
        #The header is created based on the devices that are connected
        #It contains the names of the devices and their respective channels
        #The header is written to the file
        self.header = [] 
        self.ids = []
        if self.ui.fixed_voltage_checkBox.isChecked():
            self.constant_header(self.ui.time_between_measurements.value())
        else:
            self.sweep_header(len(self.sweep[0]))

        for i in range(len(self.ui.device_handler.smu_devices)):
            self.header.append(f'Voltage_SMU_{i}[V]')
            self.header.append(f'Current_SMU_{i}[A]')
            self.ids.append(self.ui.device_handler.smu_devices[i].return_assigned_id().replace(' ', '_').replace(',', '_') + ' ... ')
        for i in range(len(self.ui.device_handler.voltmeter_devices)):
            self.header.append(f'Voltage Voltmeter {i} [V]')
            self.ids.append(self.ui.device_handler.voltmeter_devices[i].return_assigned_id().replace(' ', '_').replace(',', '_'))
        for i in range(len(self.ui.device_handler.resistancemeter_devices)):
            self.header.append(f'Resistance_Resistancemeter_{i}[Ohm]')
            self.ids.append(self.ui.device_handler.resistancemeter_devices[i].return_assigned_id().replace(' ', '_').replace(',', '_'))
        for i in range(len(self.ui.device_handler.lowV_devices)):
            num_channels = self.ui.device_handler.resistancemeter_devices[i].return_num_channels()
            if num_channels == 3:
                self.header.append(f'Voltage_lowV_{i}_Channel_1[V] Voltage_lowV_{i}_Channel_2[V] Voltage_lowV_{i}_Channel_3[V] Current_lowV_{i}_Channel_1[A] Current_lowV_{i}_Channel_2[A] Current_lowV_{i}_Channel_3[A]')
                self.ids.append(self.ui.device_handler.lowV_devices[i].return_assigned_id().replace(' ', '_').replace(',', '_')+ ' ... '+ ' ... '+ ' ... '+ ' ... ')            
            else:
                self.header.append(f'Voltage_lowV_{i}_Channel_1[V] Voltage_lowV_{i}_Channel_2[V] Voltage_lowV_{i}_Channel_3[V] Voltage_lowV_{i}_Channel_4[V] Current_lowV_{i}_Channel_1[A] Current_lowV_{i}_Channel_2[A] Current_lowV_{i}_Channel_3[A] Current_lowV_{i}_Channel_4[A]')
                self.ids.append(self.ui.device_handler.lowV_devices[i].return_assigned_id().replace(' ', '_').replace(',', '_')+ ' ... '+ ' ... '+ ' ... '+ ' ... '+ ' ... '+ ' ... '+ ' ... ')

        self.file.write(' '.join(self.ids) + '\n')
        self.file.write(' '.join(self.header)+ '\n') 
        

    def write_data(self, data):
        #This function writes the data to the file
        data_string = ' '.join(map(str, data)) + '\n'
        try:
            self.file.write(data_string)
        except:
            print('Data could not be safed')

    def sweep_header(self, num_of_steps):
        #This function writes the header for the sweep data
        self.file.write('Steps: {}\n'.format(num_of_steps))
    
    def constant_header(self, time_between_points):
        #This function writes the header for the constant voltage data
        self.file.write('Time_between_points: {}\n'.format(time_between_points))

    def close(self):
        #This function closes the file
        self.file.close()