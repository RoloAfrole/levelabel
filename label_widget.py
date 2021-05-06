# -*- coding: utf-8 -*-

import sys
import os
from PIL import Image
import cv2
from PIL.ImageQt import ImageQt

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog
from PySide2.QtUiTools import QUiLoader


class LabelWidget(QWidget):
    def __init__(self, parent=None, level=3):
        super(LabelWidget, self).__init__(parent)
        self.setup_settings(level)
        self.setup_ui()

    def setup_settings(self, level):
        """Initialize widgets params.
        """
        self.level = level
        self.base_size = 450

    def setup_ui(self):
        """Initialize widgets.
        """
        self.level_label = QLabel('Level: ?')
        self.limage_label = QLabel()
        self.level_buttons = [QPushButton('{}'.format(l)) for l in range(1, self.level+1)]

        self.limage_label.setFixedWidth(self.base_size)
        self.limage_label.setFixedHeight(self.base_size)

        self.b_layout = QHBoxLayout()
        for b in self.level_buttons:
            self.b_layout.addWidget(b)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.level_label)
        self.main_layout.addWidget(self.limage_label)
        self.main_layout.addLayout(self.b_layout)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

    def update_limage(self, image, level):
        # qim = ImageQt(image)
        qim = QImage(
            image,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            QImage.Format_RGB888,
        )
        self.set_widget_size_from_img(image)
        self.limage_label.setPixmap(QPixmap.fromImage(qim))
        self.level_label.setText('Level: {}'.format(level+1))

    def set_widget_size_from_img(self, img):
        h, w, c = img.shape
        self.limage_label.setFixedWidth(w)
        self.limage_label.setFixedHeight(h)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = LabelWidget()
    mainWindow.show()
    sys.exit(app.exec_())
