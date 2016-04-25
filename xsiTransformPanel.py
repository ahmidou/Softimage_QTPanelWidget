import re
from simpleEval import simple_eval

class XYZLineEdit(QtGui.QLineEdit):
    def __init__(self, contents='', parent=None):
        super(XYZLineEdit, self).__init__(contents, parent)
        self.returnPressed.connect(self.validate)
        self._before = contents
        regexp = QtCore.QRegExp('^[\d\(\)\+\-\*\/\.]*$')
        self.validator = QRegExpValidator(regexp)

    def focusInEvent(self, event):
        #self.selectAll()
        if event.reason() != QtCore.Qt.PopupFocusReason:
            self._before = self.text()
        super(XYZLineEdit, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.validate()
        super(XYZLineEdit, self).focusOutEvent(event)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.setText(self._before)
            self.clearFocus()
        else:
            super(XYZLineEdit, self).keyPressEvent(e)

    def mousePressEvent(self, e, Parent=None):
        super(XYZLineEdit, self).mousePressEvent(e) #required to deselect on 2e click
        self.selectAll()

    def validate(self):
        state = self.validator.validate(self.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            try:
                exp=simple_eval(self.text())
                self.setText( str(exp))
                self._before = str(exp)
                self.clearFocus()
            except:
                self.setText(self._before)
                self.clearFocus()
        elif state == QtGui.QValidator.Invalid:
            self.setText(self._before)

class TooglableMenuButton (QtGui.QPushButton):
    def __init__ (self, path, menu, parent = None):
        QtGui.QPushButton.__init__(self, parent)
        self.pixmap = QPixmap(path)
        self.menu = menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuButton_onClicked)

    def paintEvent (self, event):
        QtGui.QPushButton.paintEvent(self, event)

        style = self.style()
        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        p = QtGui.QPainter(self)

        if not self.pixmap.isNull():
            style.drawItemPixmap(p, self.rect(), Qt.AlignLeft|Qt.AlignTop, self.pixmap);

    def menuButton_onClicked(self, point):
        sender = self.sender()
        geo = self.geometry()
        print point
        pos = sender.mapToGlobal(point)
        print geo, pos
        self.menu.exec_(QPoint(pos.x()-geo.width()-self.menu.geometry().width(), pos.y()))

    def setMenu(self, menu):
        QtGui.QPushButton.setMenu(self, menu)
        menu.installEventFilter(self)




class TransformElement(QWidget):    
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
        self.X = XYZLineEdit(self)
        self.Y = XYZLineEdit(self)
        self.Z = XYZLineEdit(self)  

        self.XButton = QPushButton('X', self)
        self.XButton.setObjectName('X')
        self.XButton.setCheckable(True)
        self.XButton.setChecked(False)
        self.XButton.setStyleSheet("QPushButton#X {background-color: dimgray; min-width: 1.5em; min-height: 1.5em; border-radius: 4px;} QPushButton#X:checked {background-color: Crimson;}");
        self.XButton.clicked.connect(self.button_onClicked) 
     
        self.YButton = QPushButton('Y', self)
        self.YButton.setObjectName('Y')
        self.YButton.setCheckable(True)
        self.YButton.setChecked(False)
        self.YButton.setStyleSheet("QPushButton#Y {background-color: dimgray; min-width: 1.5em; min-height: 1.5em; border-radius: 4px;} QPushButton#Y:checked {background-color: SpringGreen ;}");
        self.YButton.clicked.connect(self.button_onClicked) 

        self.ZButton = QPushButton('Z', self)
        self.ZButton.setObjectName('Z')
        self.ZButton.setCheckable(True)
        self.ZButton.setChecked(False)
        self.ZButton.setStyleSheet("QPushButton#Z {background-color: dimgray; min-width: 1.5em; min-height: 1.5em; border-radius: 4px;} QPushButton#Z:checked {background-color: DodgerBlue ;}");
        self.ZButton.clicked.connect(self.button_onClicked) 

        self.grid = QtGui.QGridLayout()
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
        #srt = [parent.scaleButton, ]
        #print self.parent()
        self.xIsChecked = self.XButton.isChecked()
        self.yIsChecked = self.YButton.isChecked()
        self.zIsChecked = self.ZButton.isChecked()
        #buttons = set([self.XButton, self.YButton, self.ZButton])
        #button = self.sender()
       # buttons.remove(button)
        #axis = button.text()
        #print button == self.XButton
        #button.setChecked(!button.is)

        if self.name == 'Scale':
            parent.updateXYZstate(parent.scaleWidget)
            parent.scaleButton.setChecked(True)
        elif self.name == 'Rotate':
            parent.updateXYZstate(parent.rotateWidget)
            parent.rotateButton.setChecked(True)
        elif self.name == 'Translate':
            parent.updateXYZstate(parent.translateWidget)
            parent.translateButton.setChecked(True)

        #modifiers = QtGui.QApplication.keyboardModifiers()



        """if modifiers == QtCore.Qt.ShiftModifier:

            print('Shift+Click')
        elif modifiers == QtCore.Qt.ControlModifier:
            print('Control+Click')
        else:
            for b in buttons:
                b.setChecked(False)"""


class XsiTransformPanel(QWidget):    
    def __init__(self, name, parent, *args, **kwargs):        
        super(XsiTransformPanel, self).__init__(*args, **kwargs)

        #Parent widget under Maya main window        
        self.setParent(parent)        
        self.setWindowFlags(Qt.Window)   
        
        #Set the object name     
        self.name = name
        self.setObjectName('XsiTransformPanel_uniqueId')        
        self.setWindowTitle('XsiTransformPanel')        

        self.selChangeID = None
        self.srtUpdaterID = None
        self.selectionList = None
        
        self.Menuactions = {}
        self.initHost()
        self.populateMenu()   
        self.initUI()
        self.updateSelection()

    def closeEvent(self, event):
        QtGui.QWidget.closeEvent(self, event)

    def initHost(self):
        pass

    def updateSRT(self, msg, mplug, otherMplug, clientData):
        pass

    def setSRT(self):
        pass

    def updateSelection(self, *args, **kwargs):
        pass

    def clearSRT(self):
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
        self.mainMenu = QMenu('TransformMenu')
        self.mainMenu.setTearOffEnabled(True)
        self.mainMenu.addAction((QtGui.QAction('test0', self)))
        for action in self.Menuactions:
            self.mainMenu.addAction(self.Menuactions[action])
        self.mainMenu.setLayoutDirection(Qt.LeftToRight)
        self.mainButton.setMenu (self.mainMenu)     
        
        self.refMenu = QMenu('RefMenu')
        self.refMenu.setTearOffEnabled(True)

        self.refMenu.addAction((QtGui.QAction('test0', self)))
        self.refMenu.addAction((QtGui.QAction('test1', self)))
        self.refMenu.addAction((QtGui.QAction('test2', self)))
        self.refMenu.addAction((QtGui.QAction('test3', self)))


        
    def initUI(self):
        #Create 'Main Menu' button
        self.mainButton = QPushButton(str(self.name), self)
        self.mainButton.setObjectName('main')
        self.mainButton.setStyleSheet("QPushButton#main::menu-indicator {subcontrol-position: left bottom; bottom: -4px;}")

        self.createMenus()
 
        self.scaleButton = QtGui.QPushButton('S')
        self.scaleButton.setObjectName('S')
        self.scaleButton.setCheckable( True );
        self.scaleButton.setStyleSheet("QPushButton#S {background-color: dimgray; min-width: 0.5em; min-height: 1.5em; border-radius: 12px; font-weight: bold; font-size: 10pt;} QPushButton#S:checked {background-color: darkgray;}");
        self.scaleWidget = TransformElement('Scale', self)
        self.scaleButton.clicked.connect(self.SRT_onClicked) 

        self.rotateButton = QtGui.QPushButton('R')
        self.rotateButton.setObjectName('R')
        self.rotateButton.setStyleSheet("QPushButton#R {background-color: dimgray; min-width: 1.2em; min-height: 1.5em; border-radius: 12px; font-weight: bold; font-size: 10pt;} QPushButton#R:checked {background-color: darkgray;}");
        self.rotateButton.setCheckable( True );
        self.rotateWidget = TransformElement('Rotate', self)
        self.rotateButton.clicked.connect(self.SRT_onClicked) 

        self.translateButton = QtGui.QPushButton('T')
        self.translateButton.setObjectName('T')
        self.translateButton.setStyleSheet("QPushButton#T {background-color: dimgray; min-width: 1.2em; min-height: 1.5em; border-radius: 12px; font-weight: bold; font-size: 10pt;} QPushButton#T:checked {background-color: darkgray;}");
        self.translateButton.setCheckable( True );
        self.translateWidget = TransformElement('Translate', self)
        self.translateButton.clicked.connect(self.SRT_onClicked) 

        self.SRTgroup = QtGui.QButtonGroup()
        self.SRTgroup.setExclusive(True)
        self.SRTgroup.addButton(self.scaleButton)
        self.SRTgroup.addButton(self.rotateButton)
        self.SRTgroup.addButton(self.translateButton)


        self.globalButton = QtGui.QPushButton('Global')
        self.globalButton.setCheckable( True );
        self.localButton = QtGui.QPushButton('Local')
        self.localButton.setCheckable( True );
        self.viewButton = QtGui.QPushButton('View')
        self.viewButton.setCheckable( True );
        self.parentButton = QtGui.QPushButton('Parent')
        self.parentButton.setCheckable( True );
        self.addButton = QtGui.QPushButton('Add')
        self.addButton.setCheckable( True );
        self.refButton = TooglableMenuButton("E:/XSI_DEV/MAYA/python/xsiPanel/leftTopArrow.png", self.refMenu, 'Ref')
        self.refButton.setObjectName('Ref')
        self.refButton.setCheckable( True )

        self.planeButton = TooglableMenuButton("E:/XSI_DEV/MAYA/python/xsiPanel/leftTopArrow.png", 'Plane')
        self.planeButton.setObjectName('Plane')
        self.planeButton.setCheckable( True );

        self.volumeButton = QtGui.QPushButton('Vol')
        self.volumeButton.setCheckable( True );

        self.SRTModegroup = QtGui.QButtonGroup()
        self.SRTModegroup.setExclusive(True)
        self.SRTModegroup.addButton(self.globalButton)
        self.SRTModegroup.addButton(self.localButton)
        self.SRTModegroup.addButton(self.viewButton)
        self.SRTModegroup.addButton(self.parentButton)
        self.SRTModegroup.addButton(self.addButton)
        self.SRTModegroup.addButton(self.refButton)
        self.SRTModegroup.addButton(self.planeButton)
        self.SRTModegroup.addButton(self.volumeButton)

        self.cogButton = QtGui.QPushButton('COG')
        self.cogButton.setCheckable( True );
        self.proportionalButton = QtGui.QPushButton('Prop')
        self.proportionalButton.setCheckable( True );
        self.symmetryButton = TooglableMenuButton("E:/XSI_DEV/MAYA/python/xsiPanel/leftTopArrow.png", self.refMenu, 'Sym')
        self.symmetryButton.setCheckable( True );

        self.symmetryButton.setStyleSheet("QPushButton::menu-indicator {subcontrol-position: left bottom}")

        SRTgrid = QtGui.QGridLayout()
        SRTgrid.setSpacing(0)
        SRTgrid.setContentsMargins(2,2,2,2)
        SRTgrid.addWidget(self.scaleButton, 0, 2)
        SRTgrid.addWidget(self.scaleWidget, 0, 0, 1, 2)        
        SRTgrid.addWidget(self.rotateButton, 1, 2)
        SRTgrid.addWidget(self.rotateWidget, 1, 0, 1, 2) 
        SRTgrid.addWidget(self.translateButton, 2, 2)
        SRTgrid.addWidget(self.translateWidget, 2, 0, 1, 2)
        
        SRToptionsGrid = QtGui.QGridLayout()
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

        mainGrid = QtGui.QGridLayout()
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

    def SRT_onClicked(self):        
        button = self.sender()
        widget = None
        if button.text() == 'S':
            widget = self.scaleWidget
            self.volumeButton.show()
            self.planeButton.hide()
            self.globalButton.setEnabled(False)
            self.parentButton.setEnabled(False)
            self.addButton.setEnabled(False)
            self.refButton.setEnabled(False)
        elif button.text() == 'R':
            widget = self.rotateWidget
            self.volumeButton.hide()
            self.planeButton.show()
            self.addButton.show()
            self.parentButton.hide()
            self.globalButton.setEnabled(True)
            self.addButton.setEnabled(True)
            self.parentButton.setEnabled(True)
            self.refButton.setEnabled(True)
        elif button.text() == 'T':
            self.volumeButton.hide()
            self.planeButton.show()
            self.addButton.hide()
            self.parentButton.show()
            widget = self.translateWidget
            self.globalButton.setEnabled(True)
            self.addButton.setEnabled(True)
            self.parentButton.setEnabled(True)
            self.refButton.setEnabled(True)

        self.updateXYZstate(widget)

    def populateMenu(self):       
        action = QAction("&Reset All Transforms", self)
        action.setShortcut(self.tr("Ctrl+Sift+R"))
        action.triggered = self.resetAllTransforms
        self.Menuactions["resetAllTransforms"] = action

    def resetAllTransforms(self):
        print "&Reset All Transforms"