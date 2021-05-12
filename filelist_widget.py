# -*- coding: utf-8 -*-

import sys
import os

import cv2

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QScrollArea
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog
from PySide2.QtUiTools import QUiLoader

from util_file import path_list

from filelabel_widget import FileLabelWidget

class FilelistWidget(QWidget):
    def __init__(self, parent=None):
        super(FilelistWidget, self).__init__(parent)
        self.setup_settings()
        self.setup_ui()

    def setup_settings(self):
        """Initialize widgets params.
        """
        self.target_dir = './'
        self.re_pattern = '/*\.(jpg|jpeg|png|gif|bmp)'
        self.target_files_path = []
        self.selected_idx = 0

    def setup_ui(self):
        """Initialize widgets.
        """
        # self.select_button = QPushButton("Open dir")
        # self.select_button.clicked.connect(self.select_dir)

        self.list_w = self.setup_list_ui()
        self.filelabel_list = []
        self.filelist_layout = QVBoxLayout()
        # self.filelist_layout.addWidget(self.select_button)
        self.filelist_layout.addWidget(self.list_w)

        self.setLayout(self.filelist_layout)

    def setup_list_ui(self):
        self.filelabel_list = []
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        list_w = QWidget()
        vbox = QVBoxLayout()
        if self.target_files_path:
            for i, p in enumerate(self.target_files_path):
                label = FileLabelWidget(p, i)
                vbox.addWidget(label)
                self.filelabel_list.append(label)
        else:
            label = QLabel('Please select Directory!')
            vbox.addWidget(label)
        vbox.setAlignment(QtCore.Qt.AlignTop)
        list_w.setLayout(vbox)
        scroll.setWidget(list_w)
        return scroll

    def select_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Directory', os.path.expanduser(self.target_dir) )
        if dir_path:
            self.target_dir = dir_path
            self.load_files()
            self.init_selected_idx()

    def load_files(self):
        self.target_files_path = path_list(self.target_dir, path_key='f', use_re=True, re_pattern=self.re_pattern)
        self.filelist_layout.removeWidget(self.list_w)
        self.list_w.deleteLater()
        self.list_w = self.setup_list_ui()
        self.filelist_layout.addWidget(self.list_w)

    def get_filepath(self, id):
        if self.target_files_path:
            return self.target_files_path[id]
        else:
            return None

    def get_selected_path(self):
        return self.get_filepath(self.selected_idx)

    def init_selected_idx(self):
        self.selected_idx = 0

    def select_filepath(self, idx=None):
        if idx is None:
            if self.selected_idx != len(self.target_files_path)-1:
                self.selected_idx += 1
                return self.get_selected_path()
            else:
                return self.get_selected_path()
        else:
            self.selected_idx = idx
            return self.get_selected_path()

    def select_filepath_back(self, idx=None):
        if idx is None:
            if self.selected_idx != 0:
                self.selected_idx -= 1
                return self.get_selected_path()
            else:
                return self.get_selected_path()
        else:
            self.selected_idx = idx
            return self.get_selected_path()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = FilelistWidget()
    mainWindow.show()
    sys.exit(app.exec_())
