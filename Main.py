from PyQt5.QtWidgets import QApplication
import sys
from UI import Ui_MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())