# -*- coding: utf-8 -*-

import sys
import os
import json

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QMessageBox
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy, QCheckBox
from PySide2.QtUiTools import QUiLoader
from numpy.lib.shape_base import apply_along_axis

from image_widget import ImageWidget
from label_widget import LabelWidget
from filelist_widget import FilelistWidget

class ControlWidget(QWidget):
    def __init__(self, parent=None):
        super(ControlWidget, self).__init__(parent)
        self.set_init_settings()
        self.setup_ui()
        self.setup_labeling_func()
        self.setup_file_func()
        self.set_check()
        self.set_check_func()
        self.set_size()

    def set_size(self):
        self.l_layout.setAlignment(QtCore.Qt.AlignTop)

        self.select_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.save_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.delete_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.image_w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filelist_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.f_widget.setFixedHeight(40)
        self.file_name.setFixedHeight(40)

        self.l_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.r_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def set_init_settings(self):
        self.auto_load_next_data = True
        self.auto_save = False

    def setup_ui(self):
        """Initialize widgets.
        """
        self.file_name = QLabel()
        self.f_widget = self.setup_func_widget()
        self.label_w = LabelWidget()
        self.image_w = ImageWidget(self.label_w)
        self.filelist_w = FilelistWidget()

        self.l_layout = QVBoxLayout()
        self.l_layout.addWidget(self.file_name)
        self.l_layout.addWidget(self.image_w)
        self.l_layout.addWidget(self.f_widget)
        self.l_widget = QWidget()
        self.l_widget.setLayout(self.l_layout)

        self.r_layout = QVBoxLayout()
        self.r_layout.addWidget(self.label_w)
        self.r_layout.addWidget(self.filelist_w)
        self.r_widget = QWidget()
        self.r_widget.setLayout(self.r_layout)
        
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.l_widget)
        self.h_layout.addWidget(self.r_widget)

        self.setLayout(self.h_layout)

    def setup_func_widget(self):
        f_widget = QWidget()
        f_layout = QHBoxLayout()
        self.select_button = QPushButton("Open Dir")
        self.select_button.clicked.connect(self.select_dir)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_data)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_data)
        self.auto_load_next_data_box = QCheckBox("Auto Load Next")
        self.auto_save_box = QCheckBox("Auto Save")
        self.auto_take_over_last_data_box = QCheckBox("Auto Use Last label")

        f_layout.addWidget(self.select_button)
        f_layout.addWidget(self.save_button)
        f_layout.addWidget(self.delete_button)
        f_layout.addWidget(self.auto_load_next_data_box)
        f_layout.addWidget(self.auto_save_box)
        f_layout.addWidget(self.auto_take_over_last_data_box)
        f_widget.setLayout(f_layout)
        return f_widget

    def set_check(self):
        self.auto_load_next_data_box.setChecked(self.auto_load_next_data)
        self.auto_save_box.setChecked(self.auto_save)
        self.auto_take_over_last_data_box.setChecked(self.image_w.auto_take_over_last_data)

    def set_check_func(self):
        self.auto_load_next_data_box.stateChanged.connect(self.change_check)
        self.auto_save_box.stateChanged.connect(self.change_check)
        self.auto_take_over_last_data_box.stateChanged.connect(self.change_check)

    def change_check(self):
        self.auto_load_next_data = self.auto_load_next_data_box.isChecked()
        self.auto_save = self.auto_save_box.isChecked()
        self.image_w.auto_take_over_last_data = self.auto_take_over_last_data_box.isChecked()

    def setup_labeling_func(self):
        for w in self.label_w.level_buttons:
            w.clicked.connect(self.labeling)

    def setup_file_func(self):
        for w in self.filelist_w.filelabel_list:
            w.clicked.connect(self.clicked_file)

    def labeling(self):
        lbutton = self.sender()
        self.image_w.update_labeling_data(int(lbutton.text())-1)
        if self.auto_load_next_data:
            if self.image_w.is_last_idx():
                self.save_data()
                self.open_data(self.filelist_w.select_filepath())
                return
        self.image_w.update_selected_idx()
        img, level = self.image_w.get_selected_area_image()
        self.label_w.update_limage(img, level)

    def save_data(self):
        self.image_w.save_labeling_data(self.auto_save)

    def delete_data(self):
        self.image_w.delete_labeling_data()

    def select_dir(self):
        self.filelist_w.select_dir()
        self.setup_file_func()
        self.open_data(self.filelist_w.get_selected_path())

    def open_data(self, file_path):
        if file_path:
            self.file_name.setText(file_path)
            self.image_w.load_image(file_path, self.filelist_w.selected_idx)
            img, level = self.image_w.get_selected_area_image()
            self.label_w.update_limage(img, level)

    def clicked_file(self):
        filelabel = self.sender()
        id = filelabel.id
        self.save_data()
        self.open_data(self.filelist_w.select_filepath(id))

    def closeEvent(self, event):
        self.save_data()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ControlWidget()
    mainWindow.show()
    sys.exit(app.exec_())
