from Qt import QtGui, QtCore, QtWidgets
from Qt.QtCore import * 
from Qt.QtGui import *

import inspect, os

from xsiMenuButton import TooglableMenuButton

class XsiPanelHost(QtWidgets.QWidget):    
    def __init__(self, name, parent, *args, **kwargs):        
        super(XsiPanelHost, self).__init__(*args, **kwargs)

        #Parent widget under Maya main window        
        self.setParent(parent)        
        self.setWindowFlags(Qt.Window)   
        
        #Set the object name     
        self.name = name
        self.setObjectName(name+'_uniqueId')        
        self.setWindowTitle(name)        
        self.iconPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        self.selChangeID = None
        self.selectionList = []
        self.srtUpdaterID = []
        
        self.Menuactions = {}
        self.initUI()
        self.initHost()
        self.updateSelection()

    def closeEvent(self, event):
        QtGui.QWidget.closeEvent(self, event)

    def initHost(self):
        pass

    def updateSelection(self, *args, **kwargs):
        pass     
        
    def initUI(self):
        #Create 'Main Menu' button
        self.mainMenu = QMenu(self.name+'Menu')
        self.mainMenu.setObjectName(self.name+'Menu')
        self.mainMenu.setTearOffEnabled(True)
        self.mainMenu.addAction((QtGui.QAction('test0', self)))
        self.mainMenu.setStyleSheet("QMenu::tearoff {height: 8px;} QMenu::tearoff:selected{ background-color: dimgray}")

        self.populateMenu()
        for action in self.Menuactions:
            self.mainMenu.addAction(self.Menuactions[action])

        self.mainButton = TooglableMenuButton(os.path.join(self.iconPath,"leftBottomArrow.png"), self.refMenu, str(self.name))
        self.mainButton.setObjectName(self.name+'Main')
        #self.mainButton.setStyleSheet("QPushButton#main::menu-indicator {subcontrol-position: left bottom; bottom: -4px;}")

        mainGrid = QtGui.QGridLayout()
        mainGrid.setSpacing(0)
        mainGrid.setContentsMargins(0,0,0,0)
        mainGrid.addWidget(self.mainButton, 0, 0)
        #mainGrid.addLayout(SRTgrid,1,0)

        self.setLayout(mainGrid) 

    def populateMenu(self):       
        action = QAction("&Reset All Transforms", self)
        action.setShortcut(self.tr("Ctrl+Sift+R"))
        action.triggered = self.resetAllTransforms
        self.Menuactions["resetAllTransforms"] = action

    def resetAllTransforms(self):
        print "&Reset All Transforms"