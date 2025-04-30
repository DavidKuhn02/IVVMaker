from PyQt5.QtWidgets import QApplication
import sys
from new_ui import Ui_MainWindow
import pyvisa as visa

ResourceManager = visa.ResourceManager('@py') # Set up the resource manager


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = Ui_MainWindow(rm=ResourceManager)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")
        ResourceManager.close()         
        sys.exit(1)
