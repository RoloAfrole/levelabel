# -*- coding: utf-8 -*-

import sys
import os


from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader

from control_widget import ControlWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mainWidget = ControlWidget()
        self.setCentralWidget(self.mainWidget)
        # self.setWindowTitle("tool")
        # self.setGeometry(350, 150, 600, 400)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())