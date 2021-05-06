# -*- coding: utf-8 -*-

import sys
import os
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import cv2

import json
import numpy as np

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QMessageBox
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog
from PySide2.QtUiTools import QUiLoader


class ImageWidget(QLabel):
    def __init__(self, label_widget, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.label_widget = label_widget
        self.setup_settings()
        self.setFixedWidth(self.base_size)
        self.setFixedHeight(self.base_size)

    def setup_settings(self):
        """Initialize widgets params.
        """
        self.auto_take_over_last_data = True
        self.max_level = 3
        self.selected_idx = 0
        self.level_base_color = [(255,0,0), (0,255,0), (0,0,255)]
        self.r_outline_width = 2
        self.t_outline_width = 2
        self.image_path = None
        self.image_base_path = None
        self.json_path = None
        self.image_id = None
        self.law_image_data = None
        # self.draw_image = None
        self.image_data = None
        self.labeling_data = None
        self.old_data = None
        self.rank = None
        self.rpoints = None
        self.hs = 4
        self.vs = 4
        self.zero_rank = [0 for i in range(self.hs*self.vs)]
        self.json_templete = {
            'hs': self.hs,
            'vs': self.vs,
            'rank':self.zero_rank,
            'imagePath':self.image_base_path
        }
        self.base_size = 600

    def update_image(self):
        # qim = ImageQt(self.image_data)
        qim = QImage(
            self.image_data,
            self.image_data.shape[1],
            self.image_data.shape[0],
            self.image_data.strides[0],
            QImage.Format_RGB888,
        )
        self.setPixmap(QPixmap.fromImage(qim))

    def load_image(self, path, id):
        self.selected_idx = 0
        self.image_path = path
        self.image_base_path = os.path.basename(self.image_path)
        self.image_id = id
        # self.law_image_data = Image.open(self.image_path)
        img = cv2.imread(self.image_path)
        img = scale_box(img, self.base_size, self.base_size)
        self.law_image_data = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.set_widget_size_from_img()
        self.load_labeling_data()
        self.update_image()

    def load_labeling_data(self):
        basename = os.path.splitext(self.image_base_path)[0]
        self.json_path = os.path.join(os.path.dirname(self.image_path), '{}.lebeljson'.format(basename))
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                self.labeling_data = json.load(f)
                self.old_data = self.labeling_data['rank'].copy()
                self.rank = self.labeling_data['rank']
        else:
            if self.auto_take_over_last_data and self.rank is not None:
                self.old_data = None
                self.labeling_data = None
            else:
                self.old_data = None
                self.labeling_data = None
                self.rank = self.zero_rank.copy()
        self.image_data = self.law_image_data.copy()
        # self.draw_image = ImageDraw.Draw(self.law_image_data)
        self.rpoints = rectangle_points(self.hs, self.vs, self.law_image_data)
        self.draw_from_rank()
        
    def update_image_data(self):
        self.draw_from_rank()

    def draw_from_rank(self):
        clist = color_list(self.level_base_color, self.rank, self.selected_idx)
        wlist = [self.r_outline_width if self.selected_idx != i else self.t_outline_width for i, r in enumerate(self.rank)]
        for points, ccode, w in zip(self.rpoints, clist, wlist):
            # self.draw_image.rectangle(xy = points,
            #                           fill = None,
            #                           outline = ccode,
            #                           width = w)
            cv2.rectangle(self.image_data, (points[0], points[1]), (points[2], points[3]), ccode, thickness=w)
        cv2.rectangle(self.image_data, (self.rpoints[self.selected_idx][0], self.rpoints[self.selected_idx][1]), (self.rpoints[self.selected_idx][2], self.rpoints[self.selected_idx][3]), clist[self.selected_idx], thickness=wlist[self.selected_idx])
        return self.image_data

    def update_labeling_data(self, selected_level):
        if self.rank is not None:
            self.rank[self.selected_idx] = selected_level
            self.update_image_data()
            self.update_image()

    def is_last_idx(self):
        return self.selected_idx + 1 == self.hs * self.vs

    def save_labeling_data(self, auto_save=True):
        if self.json_path is not None:
            if self.old_data is None or self.old_data != self.rank:
                if not auto_save:
                    result = QMessageBox.question(None, "確認", "セーブしますか？", QMessageBox.Ok, QMessageBox.Cancel)
                    if result == QMessageBox.Cancel:
                        return
                if self.labeling_data is None:
                    self.labeling_data = {}
                self.labeling_data['hs'] = self.hs
                self.labeling_data['vs'] = self.vs
                self.labeling_data['rank'] = self.rank
                self.labeling_data['imagePath'] = self.image_base_path
                with open(self.json_path, 'w') as f:
                    json.dump(self.labeling_data, f, indent=2, ensure_ascii=False)

    def update_selected_idx(self, new_idx=None):
        if new_idx is None:
            self.selected_idx += 1
        else:
            self.selected_idx = new_idx
        self.selected_idx = self.selected_idx % (self.hs * self.vs)
        self.update_image_data()
        self.update_image()

    def get_selected_area_image(self):
        if self.image_path is not None:
            # w, h = self.law_image_data.size
            h, w, c = self.law_image_data.shape
            img = Image.new(mode='RGB',size=(int(w/self.hs)*3, int(h/self.vs)*3))
            x1, y1, x2, y2 = self.rpoints[self.selected_idx]
            new_pos = [-(x1-(x2-x1)), -(y1-(y2-y1))]
            # img.paste(self.image_data, tuple(new_pos))
            img.paste(Image.fromarray(self.image_data), tuple(new_pos))
            return np.array(img, dtype=np.uint8), self.rank[self.selected_idx]

    def selected_clicked_area(self, pos):
        if self.image_path is not None:
            clicked_idx = self.pos_to_idx(pos)
            if 0 <= clicked_idx and  clicked_idx < self.hs * self.vs:
                self.selected_idx = clicked_idx
                self.update_image_data()
                self.update_image()

    def pos_to_idx(self, pos):
        for i, r in enumerate(self.rpoints):
            x1, y1, x2, y2 = r
            x = pos.x()
            y = pos.y()
            if x1 <= x and x < x2 and y1 <= y and y < y2:
                return i

    def mousePressEvent(self, event):
        clicked_pos = event.pos()
        self.selected_clicked_area(clicked_pos)
        img, level = self.get_selected_area_image()
        self.label_widget.update_limage(img, level)

    def delete_labeling_data(self, auto=False):
        if not auto:
            result = QMessageBox.question(None, "確認", "削除しますか？", QMessageBox.Ok, QMessageBox.Cancel)
            if result == QMessageBox.Cancel:
                return
        os.remove(self.json_path)

    def set_widget_size_from_img(self):
        h, w, c = self.law_image_data.shape
        self.setFixedWidth(w)
        self.setFixedHeight(h)


def rectangle_points(hs, vs, image_data):
    # w, h = image_data.size
    h, w, c = image_data.shape
    w_list = np.linspace(0, w, hs+1, dtype=int)
    h_list = np.linspace(0, h, vs+1, dtype=int)
    points = []
    for yi in range(vs):
        for xi in range(hs):
            point = [w_list[xi], h_list[yi], w_list[xi+1]-1, h_list[yi+1]-1]
            points.append(point)

    return points

def color_list(c_base, rank, selected_idx=None):
    color_list = []
    for i, r in enumerate(rank):
        c = c_base[r]
        if selected_idx is not None and i == selected_idx:
            c = tuple([int(v/2) for v in c])
        color_list.append(c)
    return color_list


def scale_box(img, width, height):
    """指定した大きさに収まるように、アスペクト比を固定して、リサイズする。
    """
    h, w = img.shape[:2]
    aspect = w / h
    if width / height >= aspect:
        nh = height
        nw = round(nh * aspect)
    else:
        nw = width
        nh = round(nw / aspect)

    dst = cv2.resize(img, dsize=(nw, nh))

    return dst


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ImageWidget()
    mainWindow.show()
    sys.exit(app.exec_())
