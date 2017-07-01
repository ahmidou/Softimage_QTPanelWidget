from PySide import QtGui, QtCore
from PySide.QtCore import * 
from PySide.QtGui import *
import math
import re
import math
import inspect, os
from simpleEval import simple_eval

MAX_QT_VAL = 999999999.0
MAX_QT_EXP = 10

class VEBaseSpinBox(QLineEdit):
  def __init__(self, name, parent, *args, **kwargs):        
    super(VEBaseSpinBox, self).__init__(parent, *args, **kwargs)

    self.m_trackStartPos = QPoint()
    self.minimum = -MAX_QT_VAL
    self.maximum = MAX_QT_VAL
    self.decimals = 4
    self.singleStep = 1.0
    #self.m_last
    #self.m_startValue
    #bool self.m_dragging
    #bool self.m_stepping
    #bool self.m_steppingTimerConnected
    self.m_steppingTimer = QTimer()
    self.m_last = 0 
    self.m_startValue = 0
    self.m_dragging= False 
    self.m_stepping= False
    self.m_steppingTimerConnected= False
  
    self.setFocusPolicy(Qt.StrongFocus)
    self.setAlignment( Qt.AlignRight | Qt.AlignCenter )
    #self.setKeyboardTracking( False )
    self.m_steppingTimer.setSingleShot( True )
  
  def stepBy(self, step):
    print self.value()
    self.setValue(str(float(self.value()) + self.singleStep))

  def value(self):
    return self.text()

  def setValue(self, value):
    self.setText(value)

  def mousePressEvent(self, event ): #override*/
    self.m_trackStartPos = event.pos()
    self.m_startValue = self.value()
    self.m_last       = self.value()

    self.initialOverrideCursor = Qt.SizeVerCursor
    QApplication.setOverrideCursor( self.initialOverrideCursor )

    event.accept()
  

  def mouseReleaseEvent(self, event ): #override*/
  
    if self.m_dragging :
    
      self.m_dragging = False
      self.resetPrecision()
      self.emitInteractionEnd( True )

      # [FE-6014]
      self.deselect()
      self.clearFocus() # [FE-6077] using self instead of self.clearFocus() makes the TAB key work.
    
    else:
    
      self.beginStepping()

      self.mousePressEvent( event )
      super(VEBaseSpinBox, self).mouseReleaseEvent(event)
    

    QApplication.restoreOverrideCursor()

    event.accept()
  

  def mouseMoveEvent(self, event ): #override*/
  
    if ( event.buttons() == Qt.LeftButton ):
    
      if not self.m_dragging:
      
        self.m_dragging = True

        if ( self.m_stepping ):
        
          self.m_stepping = False
          self.m_steppingTimer.stop()
        
        else: 
          self.emitInteractionBegin()
      

      trackPos = event.pos()

      deltaX = trackPos.x() - self.m_trackStartPos.x()
      deltaXInInches = deltaX / self.logicalDpiX()

      logBaseChangePerStep = self.implicitLogBaseChangePerStep()
      # Slow down movement if Ctrl is pressed
      if ( QApplication.keyboardModifiers() & Qt.ControlModifier ):
        logBaseChangePerStep -= 2
      else:
        logBaseChangePerStep -= 1

      stepMult = self.updateStep( deltaXInInches, logBaseChangePerStep )

      nSteps = ( round( stepMult * ( self.m_trackStartPos.y() - trackPos.y() ) ) )

      # While dragging, we want to do an absolute value offset,
      # so reset to start value and then increment by abs step
      
        #FabricUI.Util.QTSignalBlocker block( self )
      self.setValue( self.m_startValue )
      
      self.stepBy( nSteps )
    
    event.accept()
  

  def focusInEvent(self, event ): #override*/
  
    # [FE-5997] inspired by http://stackoverflow.com/questions/5821802/qspinbox-inside-a-qscrollarea-how-to-prevent-spin-box-from-stealing-focus-when
    self.setFocusPolicy(Qt.WheelFocus)

    if ( event.reason() != Qt.PopupFocusReason ):
      self.m_last = self.value()
    super(VEBaseSpinBox, self).focusInEvent(event)
  

  def focusOutEvent(self, event ): #override*/
  
    # [FE-5997] inspired by http://stackoverflow.com/questions/5821802/qspinbox-inside-a-qscrollarea-how-to-prevent-spin-box-from-stealing-focus-when
    self.setFocusPolicy(Qt.StrongFocus)

    super(VEBaseSpinBox, self).focusOutEvent(event)
  

  def keyPressEvent(self, event ): #override*/
  
    if ( event.key() == Qt.Key_Up or event.key() == Qt.Key_Down ):
    
      beginStepping()
    
    elif ( event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter ):
    
      # [FE-6025]
      self.endStepping()
      self.deselect()
      self.clearFocus()
      event.accept()
      return
    
    elif ( event.key() == Qt.Key_Escape ):
    
      # [FE-6007]
      self.setValue(self.m_last)
      self.endStepping()
      self.deselect()
      self.clearFocus()
      event.accept()
      return
    
    else:
    
      self.endStepping()
    
    super(VEBaseSpinBox, self).keyPressEvent(event)
  

  def wheelEvent(self, event ): #override*/
  
    # [FE-5997] inspired by http://stackoverflow.com/questions/5821802/qspinbox-inside-a-qscrollarea-how-to-prevent-spin-box-from-stealing-focus-when
    if (not self.hasFocus()):
    
      event.ignore()
      return
    

    self.beginStepping()
    super(VEBaseSpinBox, self).wheelEvent(event)


  def leaveEvent(self, event ): #override*/
  
    self.endStepping()
    super(VEBaseSpinBox, self).leaveEvent(event)

  #def implicitLogBaseChangePerStep(self):
  #  return 0

  #def updateStep(self, deltaXInInches, logBaseChangePerStep):
  #  return 0

  #def resetPrecision(self    ): 
  #    pass



  def beginStepping(self):
  
    if ( not self.m_stepping ):
    
      self.m_stepping = True

      if ( not self.m_steppingTimerConnected ):
      
        self.m_steppingTimerConnected = True
        self.connectSteppingTimer( self.m_steppingTimer )
      

      self.emitInteractionBegin()

      # [pzion 20160125] Steps are bigger than dragging
      self.updateStep( 0.0, self.implicitLogBaseChangePerStep() )
    

    #assert( self.m_steppingTimerConnected )
    # This is finely tuned but also personal preference:
    # (pz's fav value: 600, em's fav value: 300)
    self.m_steppingTimer.start( 300 )
  

  def endStepping(self):
  
    if ( self.m_stepping ):
    
      self.m_stepping = False
      self.m_steppingTimer.stop()
      self.resetPrecision()
      self.emitInteractionEnd( True )
    
  

  def connectSteppingTimer(self, steppingTimer ):
    return 0

  def emitInteractionBegin(self):
    return 0

  def emitInteractionEnd(self, commit ):
    return 0

  def textFromValue(self, val ):
    return QString.number( val )

  def setSingleStep(self, val):
     self.singleStep = val

  def setDecimals(self, prec):
    self.decimals = prec

  def implicitLogBaseChangePerStep(self):
    if ( self.minimum == -MAX_QT_VAL or self.maximum == +MAX_QT_VAL ):
      return 0.0

    return max(-6.0, log10( ( self.maximum() - self.minimum() ) / 20.0 ))

  def updateStep(self, deltaXInInches, logBaseChangePerStep):

    base10Exp = 0.5 * deltaXInInches + logBaseChangePerStep
    velocity = pow( 10, base10Exp )

    # Always step by a round-number 
    roundedBase10Exp = ( round( base10Exp ) )
    changePerStep = pow( 10.0, roundedBase10Exp )

    minChangePerStep = 0.00001
    changePerStep = max( minChangePerStep, changePerStep )
    maxChangePerStep = 100000
    changePerStep = min( maxChangePerStep, changePerStep )

    self.setSingleStep( changePerStep )
    self.setDecimals( max( 0, -( math.trunc( base10Exp ) ) ) )

    return max( 0.01, 0.5 * velocity / changePerStep)


  def resetPrecision(self):
    self.setDecimals( MAX_QT_EXP )


class Toto(QtGui.QMainWindow):    
    def __init__(self, parent=None):        
        super(Toto, self).__init__()

        self.spinBox = VEBaseSpinBox('X', self)


import sys
app = QtGui.QApplication(sys.argv)
view = Toto()
view.show()
sys.exit(app.exec_())
