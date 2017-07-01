from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui 
from Qt import QtGui, QtCore, QtWidgets
from Qt.QtCore import * 
from Qt.QtGui import * 
from shiboken2 import wrapInstance
import maya.api.OpenMaya as om
import pymel.core as pm


import math
import xsiTransformPanel
reload(xsiTransformPanel)
from xsiTransformPanel import XsiTransformPanel


class XsiTransformPanel_Maya(XsiTransformPanel):    
    def __init__(self, name, parent, *args, **kwargs):        
        super(XsiTransformPanel_Maya, self).__init__(name, parent, *args, **kwargs)

    def initHost(self):
        self.selChangeID = om.MEventMessage.addEventCallback('SelectionChanged', self.updateSelection)
        self.toolChangedID = om.MEventMessage.addEventCallback('PostToolChanged', self.getManipTool)

    def closeEvent(self, event):
        om.MMessage.removeCallback(self.selChangeID)
        for i in self.srtUpdaterID:
            om.MMessage.removeCallback(i)
        om.MMessage.removeCallback(self.toolChangedID)
        QtWidgets.QWidget.closeEvent(self, event)

    def setPlugValue(self, node, plug, value):
        return om.MFnDependencyNode(node).findPlug(plug, True).setFloat(value)

    def updateParam(self, name, value):
        for node in self.selectionList:
            if name == "translateX":
                self.setPlugValue(node, "translateX", value)
            elif name == "translateY":
                self.setPlugValue(node, "translateY", value)
            elif name == "translateZ":
                self.setPlugValue(node, "translateZ", value)
            elif name == "rotateX":
                self.setPlugValue(node, "rotateX", math.radians(value))
            elif name == "rotateY":
                self.setPlugValue(node, "rotateY", math.radians(value))
            elif name == "rotateZ":
                self.setPlugValue(node, "rotateZ", math.radians(value))
            elif name == "scaleX":
                self.setPlugValue(node, "scaleX", value)
            elif name == "scaleY":
                self.setPlugValue(node, "scaleY", value)
            elif name == "scaleZ":
                self.setPlugValue(node, "scaleZ", value)

    def updateSRT(self, msg, mplug, otherMplug, clientData):
        # print msg
        if msg == 2056:            
            nodeName, attrName = mplug.name().split('.')

            if attrName == "translate":
                self.translateWidget.X.setValue(mplug.child(0).asFloat())
                self.translateWidget.Y.setValue(mplug.child(1).asFloat())
                self.translateWidget.Z.setValue(mplug.child(2).asFloat())

            elif attrName == "rotate":
                self.rotateWidget.X.setValue(math.degrees(mplug.child(0).asFloat()), True)
                self.rotateWidget.Y.setValue(math.degrees(mplug.child(1).asFloat()), True)
                self.rotateWidget.Z.setValue(math.degrees(mplug.child(2).asFloat()), True)

            elif attrName == "scale":
                self.scaleWidget.X.setValue(mplug.child(0).asFloat())
                self.scaleWidget.Y.setValue(mplug.child(1).asFloat())
                self.scaleWidget.Z.setValue(mplug.child(2).asFloat())
            elif attrName == "translateX":
                self.translateWidget.X.setValue(mplug.asFloat())
            elif attrName == "translateY":
                self.translateWidget.Y.setValue(mplug.asFloat())
            elif attrName == "translateZ":
                self.translateWidget.Z.setValue(mplug.asFloat())
            elif attrName == "rotateX":
                self.rotateWidget.X.setValue(math.degrees(mplug.asFloat()))
            elif attrName == "rotateY":
                self.rotateWidget.Y.setValue(math.degrees(mplug.asFloat()))
            elif attrName == "rotateZ":
                self.rotateWidget.Z.setValue(math.degrees(mplug.asFloat()))
            elif attrName == "scaleX":
                self.scaleWidget.X.setValue(mplug.asFloat())
            elif attrName == "scaleY":
                self.scaleWidget.Y.setValue(mplug.asFloat())
            elif attrName == "scaleZ":
                self.scaleWidget.Z.setValue(mplug.asFloat())

    def getPlugValue(self, node, plug):
        return om.MFnDependencyNode(node).findPlug(plug, True).asFloat()

    def setSRT(self, selectionList):
        for i in selectionList:
            self.translateWidget.X.setValue(self.getPlugValue(i, "translateX"))
            self.translateWidget.Y.setValue(self.getPlugValue(i, "translateY"))
            self.translateWidget.Z.setValue(self.getPlugValue(i, "translateZ"))
            self.rotateWidget.X.setValue(math.degrees(self.getPlugValue(i, "rotateX")))
            self.rotateWidget.Y.setValue(math.degrees(self.getPlugValue(i, "rotateY")))
            self.rotateWidget.Z.setValue(math.degrees(self.getPlugValue(i, "rotateZ")))
            self.scaleWidget.X.setValue(self.getPlugValue(i, "scaleX"))
            self.scaleWidget.Y.setValue(self.getPlugValue(i, "scaleY"))
            self.scaleWidget.Z.setValue(self.getPlugValue(i, "scaleZ"))

    def updateSelection(self, *args, **kwargs):

        # TODO: handle multi selection (pass index to client data)
        selectionList = om.MGlobal.getActiveSelectionList()
        # iterator = OpenMaya.MItSelectionList( selectionList, OpenMaya.MFn.kDagNode )

        # clean previous selection callback
        if len(self.selectionList) > 0:
            for node in self.selectionList:
                ids = om.MMessage.nodeCallbacks(node)
                ids = set(self.srtUpdaterID)&set(ids)
                for index in ids:
                    om.MMessage.removeCallback(index)
                self.selectionList = []
                self.srtUpdaterID = []

        if not selectionList.isEmpty():
            for i in range(selectionList.length()):
                self.selectionList.append(selectionList.getDependNode(i))
                clientData = i
                self.srtUpdaterID.append(om.MNodeMessage.addAttributeChangedCallback(self.selectionList[i], self.updateSRT, clientData))
            self.setSRT(self.selectionList)
        else:
            self.clearSRT()
            self.SRT_stateUpdate()
            return

        self.getManipTool()


    def getManipTool(self, *args):
        if pm.currentCtx() == "moveSuperContext":
            self.updateHostState = False
            QMetaObject.invokeMethod(self.translateButton, "clicked")
        elif pm.currentCtx() == "RotateSuperContext":
            self.updateHostState = False
            QMetaObject.invokeMethod(self.rotateButton, "clicked")
        elif pm.currentCtx() == "scaleSuperContext":
            self.updateHostState = False
            QMetaObject.invokeMethod(self.scaleButton, "clicked")
        else:
            # 
            self.SRT_stateUpdate()

    def setManipTool(self, toolType):
        if toolType == "translate":
            pm.setToolTo( 'moveSuperContext' )
        elif toolType == "rotate":
            pm.setToolTo( 'RotateSuperContext' )
        elif toolType == "scale":
            pm.setToolTo( 'scaleSuperContext' )
              
#mayaMainWindowPtr = omui.MQtUtil.mainWindow()
#mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

#import xsiPanel
#from xsiPanel import xsiTransformPanel_maya
#reload(xsiTransformPanel_maya)

#view = xsiTransformPanel_maya.XsiTransformPanel_Maya("Transform", mayaMainWindow)
#view.show()