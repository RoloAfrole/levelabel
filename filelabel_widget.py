# -*- coding: utf-8 -*-

import sys
import os

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QScrollArea
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, QSizePolicy
from PySide2.QtUiTools import QUiLoader


class FileLabelWidget(QPushButton):
    def __init__(self, path, id):
        super(FileLabelWidget, self).__init__(path)
        self.path = path
        self.id = id
        self.setFlat(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = FileLabelWidget()
    mainWindow.show()
    sys.exit(app.exec_())
