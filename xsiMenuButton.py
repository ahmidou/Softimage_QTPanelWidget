from Qt import QtGui, QtCore, QtWidgets
from Qt.QtCore import * 
from Qt.QtGui import *


class TooglableMenuButton (QtWidgets.QPushButton):
    def __init__ (self, path, menu, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        self.pixmap = QPixmap(path)
        self.menu = menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuButton_onClicked)

    def paintEvent (self, event):
        #Draw the corner arrow
        #
        QtWidgets.QPushButton.paintEvent(self, event)

        style = self.style()
        opt = QtWidgets.QStyleOptionButton()
        self.initStyleOption(opt)

        p = QtGui.QPainter(self)

        if not self.pixmap.isNull():
            style.drawItemPixmap(p, self.rect(), Qt.AlignLeft|Qt.AlignTop, self.pixmap)

    def menuButton_onClicked(self, point):
        # set the menu position on the button's left side
        sender = self.sender()
        globalPos = sender.mapToGlobal(QPoint(0 , 0))
        pos = QPoint(globalPos.x() - self.menu.sizeHint().width(), globalPos.y())
        self.menu.exec_(pos)

    def setMenu(self, menu):
        QtWidgets.QPushButton.setMenu(self, menu)
        menu.installEventFilter(self)