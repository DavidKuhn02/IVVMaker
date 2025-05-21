from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox
from PyQt5.QtWidgets import QFormLayout, QGroupBox, QScrollArea, QScrollBar



class ParameterDiaglog_K2400(QDialog):
    def __init__(self, device, id, rm, logic):
        super().__init__()
        self.setWindowTitle(f'Advanced Settings for {id}') 
        self.setGeometry(320, 180, 400, 300)
        self.setup_ui()
        self.device = device
        self.rm = rm
        self.logic = logic 
        self.load_settings(self.device.settings)
        

    def setup_ui(self):
        self.layout = QFormLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)   
        
        self.voltage_range = QComboBox(self)
        self.voltage_range.addItems(['Auto', '0.2V', '2V', '20V', '200V', '1000V'])
        self.voltage_range.setCurrentText('Auto')
        self.voltage_range.setToolTip('Select the voltage range for the measurement')
        self.voltage_range.currentTextChanged.connect(self.update_voltage_range)
        self.layout.addRow(QLabel('Source Voltage Range:'), self.voltage_range)

        self.current_range = QComboBox(self)
        self.current_range.addItems(['Auto', '10nA', '100nA', '1uA', '10uA', '100uA', '1mA', '10mA', '100mA', '1A'])
        self.current_range.setCurrentText('Auto')
        self.current_range.setToolTip('Select the current range for the measurement')
        self.current_range.currentTextChanged.connect(self.update_current_range)
        self.layout.addRow(QLabel('Measured Current Range:'), self.current_range)

        self.nlpc = QDoubleSpinBox(self)
        self.nlpc.setRange(0.01, 10)
        self.nlpc.setSingleStep(0.01)
        self.nlpc.setDecimals(2)
        self.nlpc.setValue(1)
        self.nlpc.setToolTip('Set the NPLC (Number of Power Line Cycles) for the measurement')
        self.nlpc.valueChanged.connect(self.update_nplc)
        self.layout.addRow(QLabel('NPLCs (Integration time):'), self.nlpc)

        self.high_capacitance = QCheckBox(self)
        self.high_capacitance.setToolTip('Enable or disable high capacitance mode for the measurement')
        self.high_capacitance.stateChanged.connect(self.update_high_capacitance)
        self.layout.addRow(QLabel('High Capacitance Mode:'), self.high_capacitance)
        self.layout.addRow(QLabel(''))

        self.use_filter = QCheckBox(self)
        self.use_filter.stateChanged.connect(self.update_filter)
        self.use_filter.setToolTip('Enable or disable the filter for the measurement')
        self.layout.addRow(QLabel('Use Filter:'), self.use_filter)

        self.filter_num = QSpinBox(self)
        self.filter_num.setRange(1, 100)
        self.filter_num.setSingleStep(1)
        self.filter_num.setValue(1)
        self.filter_num.setToolTip('Set the filter for the measurement')
        self.filter_num.valueChanged.connect(self.update_filter)
        self.layout.addRow(QLabel('Filter Count:'), self.filter_num)

        self.filter_type = QComboBox(self)
        self.filter_type.addItems(['Moving Average', 'Repeat Average'])
        self.filter_type.setCurrentText('Moving Average')
        self.filter_type.setToolTip('Select the filter type for the measurement')
        self.filter_type.currentTextChanged.connect(self.update_filter)
        self.layout.addRow(QLabel('Filter Type:'), self.filter_type)
        
        self.auto_zero = QCheckBox(self)
        self.auto_zero.setToolTip('Enable or disable auto-zero for the measurement')
        self.auto_zero.setChecked(True)
        self.auto_zero.stateChanged.connect(self.update_auto_zero)
        self.layout.addRow(QLabel('Auto Zero:'), self.auto_zero)


        self.finished.connect(self.save_settings)


    def update_voltage_range(self):
        self.device.set_voltage_range(self.voltage_range.currentText().strip('V'))
    
    def update_current_range(self):
        current_ranges = {
            '10nA': 1e-08,
            '100nA': 1e-07,
            '1uA': 1e-06,
            '10uA': 1e-05,
            '100uA': 1e-04,
            '1mA': 0.001,
            '10mA': 0.01,
            '100mA': 0.1,
            '1A': 1.0,
            'Auto': 'Auto'
        }
        self.device.set_current_range(current_ranges[self.current_range.currentText()])

    def update_nplc(self):
        self.device.set_nplc(self.nlpc.value())

    def update_filter(self):
        self.device.set_filter(self.use_filter.isChecked(), self.filter_type.currentText(), self.filter_num.value())

    def update_high_capacitance(self):
        self.device.enable_highC(self.high_capacitance.isChecked())

    def update_auto_zero(self):
        self.device.set_auto_zero(self.auto_zero.isChecked())
    
    def load_settings(self, settings):
        print(settings)
        if settings is None:
            return
        try:
            self.voltage_range.setCurrentText(settings['voltage_range'])
            self.current_range.setCurrentText(settings['current_range'])
            self.nlpc.setValue(settings['nplc'])
            self.high_capacitance.setChecked(settings['high_capacitance'])
            self.use_filter.setChecked(settings['use_filter'])
            self.filter_num.setValue(settings['filter_num'])
            self.filter_type.setCurrentText(settings['filter_type'])
            self.auto_zero.setChecked(settings['auto_zero'])
        except:
            return
        
    def save_settings(self):
        self.device.settings = {
            'voltage_range': self.voltage_range.currentText(),
            'current_range': self.current_range.currentText(),
            'nplc': self.nlpc.value(),
            'high_capacitance': self.high_capacitance.isChecked(),
            'use_filter': self.use_filter.isChecked(),
            'filter_num': self.filter_num.value(),
            'filter_type': self.filter_type.currentText(),
            'auto_zero': self.auto_zero.isChecked()
        }
        if self in self.logic.open_parameter_dialogs:
            self.logic.open_parameter_dialogs.remove(self)

class ParameterDialog_K2000(QDialog):
    def __init__(self, device, id, rm, logic):
        super().__init__()
        self.setWindowTitle(f'Advanced Settings for {id}') 
        self.setGeometry(320, 180, 400, 300)
        self.setup_ui()
        self.device = device
        self.rm = rm
        self.logic = logic
        self.load_settings(self.device.settings)
        
    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(layout)

        self.measurement_type = QComboBox(self)
        self.measurement_type.addItems(['Voltage DC', 'Current DC', 'Resistance (2 Wire)', 'Voltage AC', 'Current AC', 'Resistance (4 Wire)', 'Frequency', 'Period'])
        self.measurement_type.setCurrentText('Voltage DC')
        self.measurement_type.currentTextChanged.connect(self.update_measurement_type)
        layout.addRow(QLabel('Measurement Type:'), self.measurement_type)

        self.voltage_range = QComboBox(self)
        self.voltage_range.addItems(['Auto', '0.1V', '1V', '10V', '100V', '1000V'])
        self.voltage_range.setCurrentText('Auto')
        self.voltage_range.setToolTip('Select the voltage range for the measurement')
        self.voltage_range.currentTextChanged.connect(self.update_voltage_range)
        layout.addRow(QLabel('Voltage Range (only DC):'), self.voltage_range)

        self.current_range = QComboBox(self)
        self.current_range.addItems(['Auto', '10mA', '100mA', '1A', '3A'])
        self.current_range.setCurrentText('Auto')
        self.current_range.setToolTip('Select the current range for the measurement')
        self.current_range.currentTextChanged.connect(self.update_current_range)
        layout.addRow(QLabel('Current Range (only DC):'), self.current_range)

        self.resistance_range = QComboBox(self)
        self.resistance_range.addItems(['Auto', '100 Ohm', '1k Ohm', '10k Ohm', '100k Ohm', '1M Ohm', '10M Ohm'])
        self.resistance_range.setCurrentText('Auto')
        self.resistance_range.setToolTip('Select the resistance range for the measurement')
        self.resistance_range.currentTextChanged.connect(self.update_resistance_range)
        layout.addRow(QLabel('Resistance Range (2 Wire):'), self.resistance_range)

        self.use_filter = QCheckBox(self)
        self.use_filter.setToolTip('Enable or disable the filter for the measurement')
        self.use_filter.stateChanged.connect(self.update_filter)
        layout.addRow(QLabel('Use Filter:'), self.use_filter)

        self.filter_num = QSpinBox(self)
        self.filter_num.setRange(1, 100)
        self.filter_num.setSingleStep(1)
        self.filter_num.setValue(1)
        self.filter_num.setToolTip('Set the filter for the measurement')
        self.filter_num.valueChanged.connect(self.update_filter)
        layout.addRow(QLabel('Filter Count:'), self.filter_num)

        self.filter_type = QComboBox(self)
        self.filter_type.addItems(['Moving Average', 'Repeat Average'])
        self.filter_type.setCurrentText('Moving Average')
        self.filter_type.setToolTip('Select the filter type for the measurement')
        self.filter_type.currentTextChanged.connect(self.update_filter)
        layout.addRow(QLabel('Filter Type:'), self.filter_type)

        self.finished.connect(self.save_settings)

    def update_measurement_type(self):
        types = {
            'Voltage DC': 'VOLT:DC',
            'Current DC': 'CURR:DC',
            'Resistance (2 Wire)': 'RES',
            'Voltage AC': 'VOLT:AC',
            'Current AC': 'CURR:AC',
            'Resistance (4 Wire)': 'FRES',
            'Frequency': 'FREQ',
            'Period': 'PER'
        }
        self.device.set_measurement_type(types[self.measurement_type.currentText()])

    def update_filter(self):
        self.device.update_filter(self.use_filter.isChecked(), self.filter_type.currentText(), self.filter_num.value())

    def update_voltage_range(self):
        voltage_ranges = {
            '0.1V': 0.1,
            '1V': 1,
            '10V': 10,
            '100V': 100,
            '1000V' : 1000,
            'Auto': 'AUTO'
        }
        self.device.update_voltage_range(voltage_ranges[self.voltage_range.currentText()])

    def update_current_range(self):
        current_ranges = {
            '10mA': 0.01,
            '100mA': 0.1,
            '1A': 1,
            '3A': 3,
            'Auto': 'AUTO'
        }
        self.device.update_current_range(current_ranges[self.current_range.currentText()])
    
    def update_resistance_range(self):
        resistance_ranges = {
            '100 Ohm': 100,
            '1k Ohm': 1000,
            '10k Ohm': 10000,
            '100k Ohm': 100000,
            '1M Ohm': 1000000,
            '10M Ohm': 10000000,
            'Auto': 'AUTO'
        }
        self.device.update_resistance_range(resistance_ranges[self.resistance_range.currentText()])

    def load_settings(self, settings):
        if settings is None:
            return
        try:
            self.measurement_type.setCurrentText(settings['measurement_type'])
            self.voltage_range.setCurrentText(settings['voltage_range'])
            self.current_range.setCurrentText(settings['current_range'])
            self.resistance_range.setCurrentText(settings['resistance_range'])
            self.use_filter.setChecked(settings['use_filter'])
            self.filter_num.setValue(settings['filter_num'])
            self.filter_type.setCurrentText(settings['filter_type'])
        except:
            return
    
    def save_settings(self):
        self.device.settings = {
            'measurement_type': self.measurement_type.currentText(),
            'voltage_range': self.voltage_range.currentText(),
            'current_range': self.current_range.currentText(),
            'resistance_range': self.resistance_range.currentText(),
            'use_filter': self.use_filter.isChecked(),
            'filter_num': self.filter_num.value(),
            'filter_type': self.filter_type.currentText()
        }
        if self in self.logic.open_parameter_dialogs:
            self.logic.open_parameter_dialogs.remove(self)

class ParameterDialog_K2600(QDialog):
    def __init__(self, device, id, rm, logic):
        super().__init__()
        self.setWindowTitle(f'Advanced Settings for {id}') 
        self.setGeometry(320, 180, 400, 300)
        self.setup_ui()
        self.device = device
        self.rm = rm
        self.load_settings(self.device.settings)
        self.logic = logic
        self.finished.connect(self.save_settings)

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(layout)

        self.voltage_range = QComboBox(self)
        self.voltage_range.addItems(['Auto', '0.2V', '2V', '20V', '200V'])
        self.voltage_range.setCurrentText('Auto')
        self.voltage_range.setToolTip('Select the voltage range for the measurement')
        self.voltage_range.currentTextChanged.connect(self.update_voltage_range)
        layout.addRow(QLabel('Source Voltage Range:'), self.voltage_range)

        self.current_range = QComboBox(self)
        self.current_range.addItems(['Auto', '100nA', '1uA', '10uA', '100uA', '1mA', '10mA', '100mA', '1A', '1.5A'])
        self.current_range.setCurrentText('Auto')
        self.current_range.setToolTip('Select the current range for the measurement')
        self.current_range.currentTextChanged.connect(self.update_current_range)
        layout.addRow(QLabel('Measured Current Range:'), self.current_range)
        
        self.use_filter = QCheckBox(self)
        self.use_filter.setToolTip('Enable or disable the filter for the measurement')
        self.use_filter.stateChanged.connect(self.update_filter)
        layout.addRow(QLabel('Use Filter:'), self.use_filter)

        self.filter_num = QSpinBox(self)
        self.filter_num.setRange(1, 100)
        self.filter_num.setSingleStep(1)
        self.filter_num.setValue(1)
        self.filter_num.setToolTip('Set the filter for the measurement')
        self.filter_num.valueChanged.connect(self.update_filter)
        layout.addRow(QLabel('Filter Count:'), self.filter_num)

        self.filter_type = QComboBox(self)
        self.filter_type.addItems(['Moving Average', 'Repeat Average', 'Median'])
        self.filter_type.setCurrentText('Moving Average')
        self.filter_type.setToolTip('Select the filter type for the measurement')
        self.filter_type.currentTextChanged.connect(self.update_filter)
        layout.addRow(QLabel('Filter Type:'), self.filter_type)

        self.high_capacitance = QCheckBox(self)
        self.high_capacitance.setToolTip('Enable or disable high capacitance mode for the measurement')
        self.high_capacitance.stateChanged.connect(self.update_high_capacitance)
        layout.addRow(QLabel('High Capacitance Mode:'), self.high_capacitance)
        

    def update_voltage_range(self):
        voltage_ranges = {
            '0.2V': 0.2,
            '2V': 2,
            '20V': 20,
            '200V': 200,
            'Auto': 'AUTO'
        }
        self.device.set_voltage_range(voltage_ranges[self.voltage_range.currentText()])

    def update_current_range(self):
        current_ranges = {
            '100nA': 1e-07,
            '1uA': 1e-06,
            '10uA': 1e-05,
            '100uA': 1e-04,
            '1mA': 0.001,
            '10mA': 0.01,
            '100mA': 0.1,
            '1A': 1.0,
            '1.5A': 1.5,
            'Auto': 'AUTO'
        }
        self.device.set_current_range(current_ranges[self.current_range.currentText()])

    def update_filter(self):
        self.device.set_filter(self.use_filter.isChecked(), self.filter_type.currentText(), self.filter_num.value())

    def update_high_capacitance(self):
        self.device.enable_highC(self.high_capacitance.isChecked())

    def load_settings(self, settings):
        if settings is None:
            return
        try:
            self.voltage_range.setCurrentText(settings['voltage_range'])
            self.current_range.setCurrentText(settings['current_range'])
            self.use_filter.setChecked(settings['use_filter'])
            self.filter_num.setValue(settings['filter_num'])
            self.filter_type.setCurrentText(settings['filter_type'])
            self.high_capacitance.setChecked(settings['high_capacitance'])
        except:
            return
        
    def save_settings(self):
        self.device.settings = {
            'voltage_range': self.voltage_range.currentText(),
            'current_range': self.current_range.currentText(),
            'use_filter': self.use_filter.isChecked(),
            'filter_num': self.filter_num.value(),
            'filter_type': self.filter_type.currentText(),
            'high_capacitance': self.high_capacitance.isChecked()
        }
        if self in self.logic.open_parameter_dialogs:
            self.logic.open_parameter_dialogs.remove(self)



        