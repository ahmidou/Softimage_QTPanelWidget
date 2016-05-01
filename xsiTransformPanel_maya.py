from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui 
from PySide import QtGui, QtCore
from PySide.QtCore import * 
from PySide.QtGui import * 
from shiboken import wrapInstance
import maya.api.OpenMaya as om

import math
import xsiTransformPanel
reload(xsiTransformPanel)
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

    def updateParam(self, name, value):
        if name == "translateX":
            om.MFnDependencyNode(self.selectionList).findPlug("translateX", True).setFloat(value)
        elif name == "translateY":
            om.MFnDependencyNode(self.selectionList).findPlug("translateY", True).setFloat(value)
        elif name == "translateZ":
            om.MFnDependencyNode(self.selectionList).findPlug("translateZ", True).setFloat(value)
        elif name == "rotateX":
            om.MFnDependencyNode(self.selectionList).findPlug("rotateX", True).setFloat(math.radians(value))
        elif name == "rotateY":
            om.MFnDependencyNode(self.selectionList).findPlug("rotateY", True).setFloat(math.radians(value))
        elif name == "rotateZ":
            om.MFnDependencyNode(self.selectionList).findPlug("rotateZ", True).setFloat(math.radians(value))
        elif name == "scaleX":
            om.MFnDependencyNode(self.selectionList).findPlug("scaleX", True).setFloat(value)
        elif name == "scaleY":
            om.MFnDependencyNode(self.selectionList).findPlug("scaleY", True).setFloat(value)
        elif name == "scaleZ":
            om.MFnDependencyNode(self.selectionList).findPlug("scaleZ", True).setFloat(value)

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

    def setSRT(self, selectionList):
        self.translateWidget.X.setText(str(om.MFnDependencyNode(selectionList).findPlug("translateX", True).asFloat()))
        self.translateWidget.Y.setText(str(om.MFnDependencyNode(selectionList).findPlug("translateY", True).asFloat()))
        self.translateWidget.Z.setText(str(om.MFnDependencyNode(selectionList).findPlug("translateZ", True).asFloat()))
        self.rotateWidget.X.setText(str(om.MFnDependencyNode(selectionList).findPlug("rotateX", True).asFloat()))
        self.rotateWidget.Y.setText(str(om.MFnDependencyNode(selectionList).findPlug("rotateY", True).asFloat()))
        self.rotateWidget.Z.setText(str(om.MFnDependencyNode(selectionList).findPlug("rotateZ", True).asFloat()))
        self.scaleWidget.X.setText(str(om.MFnDependencyNode(selectionList).findPlug("scaleX", True).asFloat()))
        self.scaleWidget.Y.setText(str(om.MFnDependencyNode(selectionList).findPlug("scaleY", True).asFloat()))
        self.scaleWidget.Z.setText(str(om.MFnDependencyNode(selectionList).findPlug("scaleZ", True).asFloat()))

    def updateSelection(self, *args, **kwargs):
        #print "BEUUUUUP"
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
            self.setSRT(self.selectionList)
        else:
            self.clearSRT()

    
                           
#mayaMainWindowPtr = omui.MQtUtil.mainWindow()
#mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

#import xsiPanel
#from xsiPanel import xsiTransformPanel_maya
#reload(xsiTransformPanel_maya)

#view = xsiTransformPanel_maya.XsiTransformPanel_Maya("Transform", mayaMainWindow)
#view.show()