from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui 
from PySide import QtGui, QtCore
from PySide.QtCore import * 
from PySide.QtGui import * 
from shiboken import wrapInstance
import maya.api.OpenMaya as om

import math

from xsiTransformPanel import XsiTransformPanel

class XsiTransformPanel_Maya(XsiTransformPanel):    
    def __init__(self, name, parent, *args, **kwargs):        
        super(XsiTransformPanel_Maya, self).__init__(name, parent, *args, **kwargs)

    def initHost(self):
        self.selChangeID = om.MEventMessage.addEventCallback('SelectionChanged', self.updateSelection)

    def closeEvent(self, event):
        om.MMessage.removeCallback(self.selChangeID)
        om.MMessage.removeCallback(self.srtUpdaterID)
        QtGui.QWidget.closeEvent(self, event)

    def updateSRT(self, msg, mplug, otherMplug, clientData):
        # print msg
        if msg == 2056:            
            nodeName, attrName = mplug.name().split('.')

            if attrName == "translate":
                self.translateWidget.X.set(mplug.child(0).asFloat())
                self.translateWidget.Y.set(mplug.child(1).asFloat())
                self.translateWidget.Z.set(mplug.child(2).asFloat())

            elif attrName == "rotate":
                self.rotateWidget.X.set(mplug.child(0).asFloat(), True)
                self.rotateWidget.Y.set(mplug.child(1).asFloat(), True)
                self.rotateWidget.Z.set(mplug.child(2).asFloat(), True)

            elif attrName == "scale":
                self.scaleWidget.X.set(mplug.child(0).asFloat())
                self.scaleWidget.Y.set(mplug.child(1).asFloat())
                self.scaleWidget.Z.set(mplug.child(2).asFloat())
            elif attrName == "translateX":
                self.translateWidget.X.set(mplug.asFloat())
            elif attrName == "translateY":
                self.translateWidget.Y.set(mplug.asFloat())
            elif attrName == "translateZ":
                self.translateWidget.Z.set(mplug.asFloat())
            elif attrName == "rotateX":
                self.rotateWidget.X.set(math.degrees(mplug.asFloat()))
            elif attrName == "rotateY":
                self.rotateWidget.Y.set(math.degrees(mplug.asFloat()))
            elif attrName == "rotateZ":
                self.rotateWidget.Z.set(math.degrees(mplug.asFloat()))
            elif attrName == "scaleX":
                self.scaleWidget.X.set(mplug.asFloat())
            elif attrName == "scaleY":
                self.scaleWidget.Y.set(mplug.asFloat())
            elif attrName == "scaleZ":
                self.scaleWidget.Z.set(mplug.asFloat())

    def setSRT(self):
        self.translateWidget.X.setText("")
        self.translateWidget.Y.setText("")
        self.translateWidget.Z.setText("")
        self.rotateWidget.X.setText("")
        self.rotateWidget.Y.setText("")
        self.rotateWidget.Z.setText("")
        self.scaleWidget.X.setText("")
        self.scaleWidget.Y.setText("")
        self.scaleWidget.Z.setText("")

    def updateSelection(self, *args, **kwargs):
        # TODO: handle multi selection (pass index to client data)
        selectionList = om.MGlobal.getActiveSelectionList()
        # iterator = OpenMaya.MItSelectionList( selectionList, OpenMaya.MFn.kDagNode )

        # clean previous selection callback
        if self.selectionList:
            ids = om.MMessage.nodeCallbacks(self.selectionList)
            if self.srtUpdaterID is not None and self.srtUpdaterID in ids:
                om.MMessage.removeCallback(self.srtUpdaterID)

        if not selectionList.isEmpty():
            self.selectionList = selectionList.getDependNode(0)
            clientData = None
            self.srtUpdaterID = om.MNodeMessage.addAttributeChangedCallback(self.selectionList, self.updateSRT, clientData)
            self.setSRT()
        else:
            self.clearSRT()

    
                           
#mayaMainWindowPtr = omui.MQtUtil.mainWindow()
#mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

#import xsiPanel
#from xsiPanel import xsiTransformPanel_maya
#reload(xsiTransformPanel_maya)

#view = xsiTransformPanel_maya.XsiTransformPanel_Maya("Transform", mayaMainWindow)
#view.show()