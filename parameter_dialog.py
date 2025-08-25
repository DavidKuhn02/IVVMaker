from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox
from PyQt5.QtWidgets import QFormLayout, QGroupBox, QScrollArea, QScrollBar


class ParameterDialog(QDialog):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.setWindowTitle(f'Settings for {self.device.return_assigned_id()}')
        self.setGeometry(320, 180, 400, 300)    
        layout = QVBoxLayout()
        self.widgets = {}
        for field in device.config["ui_settings"]:
            label = QLabel(field['label'])
            layout.addWidget(label)
            if field['type'] == 'select':
                widget = QComboBox()
                widget.addItems(field['options'])
                widget.setCurrentText(field.get('default'))
            elif field['type'] == 'checkbox':
                widget = QCheckBox()
                widget.setChecked(field.get('default'))
            elif field['type'] == 'int':
                widget = QSpinBox()
                widget.setMinimum(field.get('min', 0))
                widget.setMaximum(field.get('max', 100))
                widget.setSingleStep(field.get('step', 1))
                widget.setValue(field.get('default', 0))
            elif field['type'] == 'float':
                widget = QDoubleSpinBox()
                widget.setMinimum(field.get('min', 0))
                widget.setMaximum(field.get('max', 100))
                widget.setSingleStep(field.get('step', 1))
                widget.setValue(field.get('default', 0))
            else:
                continue

            widget.setProperty("function", field.get("function"))
            widget.setProperty("values", field.get("values"))
            layout.addWidget(widget)
            self.widgets[field['name']] = widget


        self.assign_widget_signals()
        self.setLayout(layout)
        self.load_config()

    def load_config(self):
        for name, widget in self.widgets.items():
            value = self.device.settings.get(name)
            if value is not None:
                if isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(value)
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(value)
            self.on_widget_changed(widget)
            # Trigger the change event to ensure the device is updated

    def save_config(self):
        for name, widget in self.widgets.items():
            value = self.get_widget_value(widget)
            if value is not None:
                self.device.settings[name] = value
        self.device.save_config()

    def closeEvent(self, event):
        self.save_config()
        event.accept()

    def assign_widget_signals(self):
        for name, widget in self.widgets.items():
            if isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda value, w=widget: self.on_widget_changed(w))
            if isinstance(widget, QCheckBox):
                widget.stateChanged.connect(lambda state, w=widget: self.on_widget_changed(w))
            if isinstance(widget, QSpinBox):
                widget.valueChanged.connect(lambda value, w=widget: self.on_widget_changed(w))
            if isinstance(widget, QDoubleSpinBox):
                widget.valueChanged.connect(lambda value, w=widget: self.on_widget_changed(w))

    def on_widget_changed(self, widget):
        function_name = widget.property("function")
        if function_name:
            widget_names = widget.property("values")
            widgets = [self.widgets[name] for name in widget_names]
            value = [self.get_widget_value(w) for w in widgets]
            func = getattr(self.device, function_name, None)
        if func and callable(func) and value is not None:
            if len(value) == 1:
                func(value[0])
            else:
                func(*value)

    def get_widget_value(self, widget):
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QCheckBox):
            return bool(widget.isChecked())
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QDoubleSpinBox):
            return widget.value()
        else:
            return None

