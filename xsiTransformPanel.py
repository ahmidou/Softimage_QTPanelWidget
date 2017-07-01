from Qt import QtGui, QtCore, QtWidgets
from Qt.QtCore import * 
from Qt.QtGui import *

from xsiMenuButton import TooglableMenuButton
import xsiPanelHost
reload(xsiPanelHost)
from xsiPanelHost import XsiPanelHost

import re
import sys
import math
import traceback
import inspect, os
from simpleEval import simple_eval


class XYZLineEdit(QtWidgets.QLineEdit):
    def __init__(self, contents='', parent=None, name=''):
        super(XYZLineEdit, self).__init__(contents, parent)
        self.returnPressed.connect(self.validate)
        self._before = contents
        self.name = name
        self.value = 0.0
        regexp = QtCore.QRegExp('^[\d\(\)\+\-\*\/\.]*$')
        self.validator = QRegExpValidator(regexp)
        self.asDegree = False
        self.initFocus = False

    def focusInEvent(self, event):
        self.initFocus = True
        if event.reason() != QtCore.Qt.PopupFocusReason:
            self._before = self.text()
        super(XYZLineEdit, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.validate()
        super(XYZLineEdit, self).focusOutEvent(event)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.setText(str(self._before))
            self.clearFocus()
        else:
            super(XYZLineEdit, self).keyPressEvent(e)

    def mousePressEvent(self, e, Parent=None):
        super(XYZLineEdit, self).mousePressEvent(e)
        # 1st click
        if self.initFocus == True:
            self.selectAll()
            self.initFocus = False

    def validate(self):
    	print self.parent().name+self.name
        state = self.validator.validate(self.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            try:
                exp = simple_eval(self.text())
                self.setValue(exp)
                self._before = exp
                self.clearFocus()
                self.parent().parent().updateClientValues(self.parent().name+self.name, exp)
                
            except Exception, e:
                print e
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                if(self._before != self.text()):
                    self.setValue(self._before)
                self.clearFocus()
        elif state == QtGui.QValidator.Invalid:
            try:
                self.setValue(self._before)
            except:
                self.setText("")

    def setValue(self, val, isRadian=False):
        if self.asDegree:
            self.value = math.degrees(val)
        else:
            self.value = val

        if type(self.value) != unicode:
            self.setText(str(round(self.value, 3)))
        else:
            self.setText(str(round(float(self.value), 3)))



class TransformElement(QtWidgets.QWidget):    
    def __init__(self, name, parent, *args, **kwargs):        
        super(TransformElement, self).__init__(*args, **kwargs)

        #Set the object name 
        self.name = name    
        self.setObjectName('Transform_' + name)

        self.xIsChecked = True
        self.yIsChecked = True
        self.zIsChecked = True

        regexp = QtCore.QRegExp('^[\d\(\)\+\-\*\/\.]*$')
        self.validator = QRegExpValidator(regexp)
        self.X = XYZLineEdit(None, self, 'X')
        self.Y = XYZLineEdit(None, self, 'Y')
        self.Z = XYZLineEdit(None, self, 'Z')  

        self.XButton = QtWidgets.QPushButton('X', self)
        self.XButton.setObjectName('X')
        self.XButton.setCheckable(True)
        self.XButton.setChecked(False)
        self.XButton.setStyleSheet("QPushButton#X {background-color: dimgray; min-width: 1.5em; min-height: 1.5em; border-radius: 4px;} QPushButton#X:checked {background-color: Crimson;}");
        self.XButton.clicked.connect(self.button_onClicked) 
     
        self.YButton = QtWidgets.QPushButton('Y', self)
        self.YButton.setObjectName('Y')
        self.YButton.setCheckable(True)
        self.YButton.setChecked(False)
        self.YButton.setStyleSheet("QPushButton#Y {background-color: dimgray; min-width: 1.5em; min-height: 1.5em; border-radius: 4px;} QPushButton#Y:checked {background-color: SpringGreen ;}");
        self.YButton.clicked.connect(self.button_onClicked) 

        self.ZButton = QtWidgets.QPushButton('Z', self)
        self.ZButton.setObjectName('Z')
        self.ZButton.setCheckable(True)
        self.ZButton.setChecked(False)
        self.ZButton.setStyleSheet("QPushButton#Z {background-color: dimgray; min-width: 1.5em; min-height: 1.5em; border-radius: 4px;} QPushButton#Z:checked {background-color: DodgerBlue ;}");
        self.ZButton.clicked.connect(self.button_onClicked) 

        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(1)
        self.grid.setContentsMargins(2,2,2,2)
        self.grid.addWidget(self.X, 1, 0)
        self.grid.addWidget(self.Y, 2, 0)
        self.grid.addWidget(self.Z, 3, 0)
        self.grid.addWidget(self.XButton, 1, 2)
        self.grid.addWidget(self.YButton, 2, 2)
        self.grid.addWidget(self.ZButton, 3, 2)
        self.setLayout(self.grid)


    def button_onClicked(self):
        parent = self.parent()
        self.xIsChecked = self.XButton.isChecked()
        self.yIsChecked = self.YButton.isChecked()
        self.zIsChecked = self.ZButton.isChecked()

        if self.name == 'scale':
            parent.updateXYZstate(parent.scaleWidget)
            QMetaObject.invokeMethod(parent.scaleButton, "clicked")
        elif self.name == 'rotate':
            parent.updateXYZstate(parent.rotateWidget)
            QMetaObject.invokeMethod(parent.rotateButton, "clicked")
        elif self.name == 'translate':
            parent.updateXYZstate(parent.translateWidget)
            QMetaObject.invokeMethod(parent.translateButton, "clicked")

        #modifiers = QtGui.QApplication.keyboardModifiers()



        """if modifiers == QtCore.Qt.ShiftModifier:

            print('Shift+Click')
        elif modifiers == QtCore.Qt.ControlModifier:
            print('Control+Click')
        else:
            for b in buttons:
                b.setChecked(False)"""


class XsiTransformPanel(XsiPanelHost):    
    def __init__(self, name, parent, *args, **kwargs):        
        super(XsiTransformPanel, self).__init__(name, parent, *args, **kwargs)

        #Parent widget under Maya main window        
        self.setParent(parent)        
        self.setWindowFlags(Qt.Window)   
        
        self.updateHostState = True
        self.srtUpdaterID = []
        self.currentTool = None

        self.setAttribute(Qt.WA_ShowWithoutActivating)

    def mousePressEvent(self, event):
        focused_widget = QtWidgets.QApplication.focusWidget()
        if isinstance(focused_widget, XYZLineEdit):
            focused_widget.clearFocus()
        super(XsiTransformPanel, self).mousePressEvent(event)

    def closeEvent(self, event):
        QtWidgets.QWidget.closeEvent(self, event)

    def initHost(self):
        pass

    def updateHostValues(self, msg, mplug, otherMplug, clientData):
        pass

    def setHostValues(self, selectionList, getFunct):
        srt = [ "translateX","translateY","translateZ",
                "rotateX","rotateY","rotateZ",
                "scaleX","scaleY","scaleZ"]

        widgets = [ self.translateWidget.X,
                    self.translateWidget.Y,
                    self.translateWidget.Z,
                    self.rotateWidget.X,
                    self.rotateWidget.Y,
                    self.rotateWidget.Z,
                    self.scaleWidget.X,
                    self.scaleWidget.Y,
                    self.scaleWidget.Z]

        srtvals = {}
        for item in srt:
            srtvals[item] = set()
            for node in selectionList:
                srtvals[item].add(getFunct(node, item))

        for i,j in zip(widgets,srt):
            if len(srtvals[j]) == 1:
                i.setValue(srtvals[j].pop())
            else:
                i.setText("")

    def updateSelection(self, *args, **kwargs):
        pass

    def updateClientValues(self, name, value):
    	print "updateClientValues"

    def clearHostValues(self):
        self.translateWidget.X.setText("")
        self.translateWidget.Y.setText("")
        self.translateWidget.Z.setText("")
        self.rotateWidget.X.setText("")
        self.rotateWidget.Y.setText("")
        self.rotateWidget.Z.setText("")
        self.scaleWidget.X.setText("")
        self.scaleWidget.Y.setText("")
        self.scaleWidget.Z.setText("")

    def createMenus(self):
        self.mainMenu = QtWidgets.QMenu('TransformMenu')
        self.mainMenu.setObjectName('TransformMenu')
        self.mainMenu.setTearOffEnabled(True)
        self.mainMenu.addAction((QtWidgets.QAction('test0', self)))
        self.mainMenu.setStyleSheet("QMenu::tearoff {height: 8px;} QMenu::tearoff:selected{ background-color: dimgray}")
        for action in self.Menuactions:
            self.mainMenu.addAction(self.Menuactions[action])
        self.mainMenu.setLayoutDirection(Qt.LeftToRight)
        self.mainButton.setMenu (self.mainMenu)     
        
        self.refMenu = QtWidgets.QMenu('RefMenu')
        self.refMenu.addAction((QtWidgets.QAction('Use Current Reference', self)))
        self.refMenu.addAction((QtWidgets.QAction('Pick New Reference', self)))
        self.refMenu.addSeparator()

        self.refMenu.addAction((QtWidgets.QAction('Pick Object Reference', self)))
        self.refMenu.addAction((QtWidgets.QAction('Pick Point Reference', self)))
        self.refMenu.addAction((QtWidgets.QAction('Pick Edge Reference', self)))
        self.refMenu.addAction((QtWidgets.QAction('Pick Face Reference', self)))
        self.refMenu.addSeparator()

        ag = QtWidgets.QActionGroup(self, exclusive=True)
        a = ag.addAction((QtWidgets.QAction('View', self, checkable=True)))
        self.refMenu.addAction(a)
        a = ag.addAction((QtWidgets.QAction('XY', self, checkable=True)))
        self.refMenu.addAction(a)
        a = ag.addAction((QtWidgets.QAction('XZ', self, checkable=True)))
        self.refMenu.addAction(a)
        a = ag.addAction((QtWidgets.QAction('YZ', self, checkable=True)))
        self.refMenu.addAction(a)
        self.refMenu.addSeparator()

        self.refMenu.addAction((QtWidgets.QAction('Reference Properties..', self)))

        self.symMenu = QtWidgets.QMenu('SymMenu')
        ag = QtWidgets.QActionGroup(self, exclusive=True)
        a = ag.addAction((QtWidgets.QAction('YZ', self, checkable=True)))
        self.symMenu.addAction(a)
        a = ag.addAction((QtWidgets.QAction('XZ', self, checkable=True)))
        self.symMenu.addAction(a)
        a = ag.addAction((QtWidgets.QAction('XY', self, checkable=True)))
        self.symMenu.addAction(a)
        self.symMenu.addSeparator()

        self.symMenu.addAction((QtWidgets.QAction('Symmetry Properties..', self)))

        
    def initUI(self):

        #Create 'Main Menu' button
        self.mainButton = QtWidgets.QPushButton(str(self.name), self)
        self.mainButton.setObjectName('main')
        self.mainButton.setStyleSheet("QPushButton#main::menu-indicator {subcontrol-position: left bottom; bottom: -4px;}")

        self.createMenus()
 
        self.scaleButton = QtWidgets.QPushButton('S')
        self.scaleButton.setObjectName('S')
        self.scaleButton.setCheckable( True );
        self.scaleButton.setAutoExclusive(False)
        self.scaleButton.setStyleSheet("QPushButton#S {background-color: dimgray; min-width: 0.5em; min-height: 1.5em; border-radius: 12px; font-weight: bold; font-size: 10pt;} QPushButton#S:checked {background-color: darkgray;}");
        self.scaleWidget = TransformElement('scale', self)
        self.scaleButton.clicked.connect(self.SRT_stateUpdate) 

        self.rotateButton = QtWidgets.QPushButton('R')
        self.rotateButton.setObjectName('R')
        self.rotateButton.setStyleSheet("QPushButton#R {background-color: dimgray; min-width: 1.2em; min-height: 1.5em; border-radius: 12px; font-weight: bold; font-size: 10pt;} QPushButton#R:checked {background-color: darkgray;}");
        self.rotateButton.setCheckable( True );
        self.rotateButton.setAutoExclusive(False)
        self.rotateWidget = TransformElement('rotate', self)
        self.rotateWidget.X.asDegree = True
        self.rotateWidget.Y.asDegree = True
        self.rotateWidget.Z.asDegree = True
        self.rotateButton.clicked.connect(self.SRT_stateUpdate) 

        self.translateButton = QtWidgets.QPushButton('T')
        self.translateButton.setObjectName('T')
        self.translateButton.setStyleSheet("QPushButton#T {background-color: dimgray; min-width: 1.2em; min-height: 1.5em; border-radius: 12px; font-weight: bold; font-size: 10pt;} QPushButton#T:checked {background-color: darkgray;}");
        self.translateButton.setCheckable( True );
        self.translateButton.setAutoExclusive(False)
        self.translateWidget = TransformElement('translate', self)
        self.translateButton.clicked.connect(self.SRT_stateUpdate) 

        self.SRTgroup = QtWidgets.QButtonGroup()
        self.SRTgroup.setExclusive(True)
        self.SRTgroup.addButton(self.scaleButton)
        self.SRTgroup.addButton(self.rotateButton)
        self.SRTgroup.addButton(self.translateButton)


        self.globalButton = QtWidgets.QPushButton('Global')
        self.globalButton.setCheckable( True );
        self.localButton = QtWidgets.QPushButton('Local')
        self.localButton.setCheckable( True );
        self.viewButton = QtWidgets.QPushButton('View')
        self.viewButton.setCheckable( True );
        self.parentButton = QtWidgets.QPushButton('Parent')
        self.parentButton.setCheckable( True );
        self.addButton = QtWidgets.QPushButton('Add')
        self.addButton.setCheckable( True );
        self.refButton = TooglableMenuButton(os.path.join(self.iconPath,"leftTopArrow.png"), self.refMenu, 'Ref')
        self.refButton.setObjectName('Ref')
        self.refButton.setCheckable( True )

        self.planeButton = TooglableMenuButton(os.path.join(self.iconPath,"leftTopArrow.png"), self.refMenu, 'Plane')
        self.planeButton.setObjectName('Plane')
        self.planeButton.setCheckable( True );

        self.volumeButton = QtWidgets.QPushButton('Vol')
        self.volumeButton.setCheckable( True );

        self.SRTModegroup = QtWidgets.QButtonGroup()
        self.SRTModegroup.setExclusive(True)
        self.SRTModegroup.addButton(self.globalButton)
        self.SRTModegroup.addButton(self.localButton)
        self.SRTModegroup.addButton(self.viewButton)
        self.SRTModegroup.addButton(self.parentButton)
        self.SRTModegroup.addButton(self.addButton)
        self.SRTModegroup.addButton(self.refButton)
        self.SRTModegroup.addButton(self.planeButton)
        self.SRTModegroup.addButton(self.volumeButton)

        self.cogButton = QtWidgets.QPushButton('COG')
        self.cogButton.setCheckable( True );
        self.proportionalButton = QtWidgets.QPushButton('Prop')
        self.proportionalButton.setCheckable( True );
        self.symmetryButton = TooglableMenuButton(os.path.join(self.iconPath,"leftTopArrow.png"), self.symMenu, 'Sym')
        self.symmetryButton.setCheckable( True );

        SRTgrid = QtWidgets.QGridLayout()
        SRTgrid.setSpacing(0)
        SRTgrid.setContentsMargins(2,2,2,2)
        SRTgrid.addWidget(self.scaleButton, 0, 2)
        SRTgrid.addWidget(self.scaleWidget, 0, 0, 1, 2)        
        SRTgrid.addWidget(self.rotateButton, 1, 2)
        SRTgrid.addWidget(self.rotateWidget, 1, 0, 1, 2) 
        SRTgrid.addWidget(self.translateButton, 2, 2)
        SRTgrid.addWidget(self.translateWidget, 2, 0, 1, 2)
        
        SRToptionsGrid = QtWidgets.QGridLayout()
        SRToptionsGrid.setSpacing(0)
        SRToptionsGrid.addWidget(self.globalButton, 0, 0)
        SRToptionsGrid.addWidget(self.localButton, 0, 1)
        SRToptionsGrid.addWidget(self.viewButton, 0, 2)
        SRToptionsGrid.addWidget(self.parentButton, 1, 0)
        SRToptionsGrid.addWidget(self.addButton, 1, 0)
        SRToptionsGrid.addWidget(self.refButton, 1, 1)
        SRToptionsGrid.addWidget(self.planeButton, 1, 2)
        SRToptionsGrid.addWidget(self.volumeButton, 1, 2)
        SRToptionsGrid.setRowMinimumHeight(2,2)
        SRToptionsGrid.addWidget(self.cogButton, 3, 0)
        SRToptionsGrid.addWidget(self.proportionalButton, 3, 1)
        SRToptionsGrid.addWidget(self.symmetryButton, 3, 2)

        mainGrid = QtWidgets.QGridLayout()
        mainGrid.setSpacing(0)
        mainGrid.setContentsMargins(0,0,0,0)
        mainGrid.addWidget(self.mainButton, 0, 0)
        mainGrid.addLayout(SRTgrid,1,0)
        mainGrid.addLayout(SRToptionsGrid,2,0)

        self.setLayout(mainGrid)


    def updateXYZstate(self, widget):
        widgets = [self.scaleWidget, self.rotateWidget, self.translateWidget]
        for w in widgets:
            if w ==  widget:
                widget.XButton.setChecked(widget.xIsChecked)
                widget.YButton.setChecked(widget.yIsChecked)
                widget.ZButton.setChecked(widget.zIsChecked)
            else:
                w.XButton.setChecked(False)
                w.YButton.setChecked(False)
                w.ZButton.setChecked(False)

    def setManipTool(self, type):
    	pass


    def SRT_stateUpdate(self):        
        button = self.sender()

        if button:
            if button.text() == 'S':
                self.currentTool = self.scaleWidget
                self.volumeButton.show()
                self.planeButton.hide()
                self.globalButton.setEnabled(False)
                self.parentButton.setEnabled(False)
                self.addButton.setEnabled(False)
                self.refButton.setEnabled(False)
                if self.updateHostState:
                	self.setManipTool("scale")
            elif button.text() == 'R':
                self.currentTool = self.rotateWidget
                self.volumeButton.hide()
                self.planeButton.show()
                self.addButton.show()
                self.parentButton.hide()
                self.globalButton.setEnabled(True)
                self.addButton.setEnabled(True)
                self.parentButton.setEnabled(True)
                self.refButton.setEnabled(True)
                if self.updateHostState:
                	self.setManipTool("rotate")
            elif button.text() == 'T':
                self.currentTool = self.translateWidget
                self.volumeButton.hide()
                self.planeButton.show()
                self.addButton.hide()
                self.parentButton.show()
                self.globalButton.setEnabled(True)
                self.addButton.setEnabled(True)
                self.parentButton.setEnabled(True)
                self.refButton.setEnabled(True)
                if self.updateHostState:
                	self.setManipTool("translate")
            button.setChecked(True)
        else:
            self.SRTgroup.setExclusive(False)
            self.scaleButton.setChecked(False)
            self.translateButton.setChecked(False)
            self.rotateButton.setChecked(False)
            self.SRTgroup.setExclusive(True)
            self.currentTool = None
        self.updateXYZstate(self.currentTool)
        self.updateHostState = True

    def setCurrentTool(*args):
    	pass

    def populateMenu(self):       
        action = QAction("&Reset All Transforms", self)
        action.setShortcut(self.tr("Ctrl+Sift+R"))
        action.triggered = self.resetAllTransforms
        self.Menuactions["resetAllTransforms"] = action

    def resetAllTransforms(self):
        print "&Reset All Transforms"

