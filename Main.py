from PyQt5.QtWidgets import QApplication
import sys
from UI import Ui_MainWindow
ResourceManager = visa.ResourceManager('@py') # Set up the resource manager


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ui_MainWindow(rm=ResourceManager)
    window.show()
    sys.exit(app.exec_())