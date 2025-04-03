from PyQt5.QtWidgets import QApplication
import qdarkstyle
import sys
from UI import Ui_MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())