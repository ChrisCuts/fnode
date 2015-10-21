# -*- coding: utf-8 -*-
'''
Created on 16.09.2015

@author: derChris
'''

from PySide import QtCore, QtGui, QtSvg
from pydispatch import dispatcher


from PlugIns.NodeTemplates import SharedGUIData
import GUI.PipeWidgets


class SharedGUIDataQTProxy():
    
    def __init__(self, SharedGUIDataObject= None):
        
        if isinstance(SharedGUIDataObject, SharedGUIData):
            self._SharedGUIDataObject = SharedGUIDataObject
        else:
            raise TypeError('Must be initialized with a SharedGUIData Object')
        
        
        
    def pos(self):
        
        pos = self._SharedGUIDataObject.pos()
        
        if isinstance(pos, (list, tuple)):
            return QtCore.QPointF(pos[0], pos[1])
        else:
            return QtCore.QPointF(0, 0)
    
    def size(self):
        
        size = self._SharedGUIDataObject.size()
        
        if isinstance(size, (list, tuple)):
            return QtCore.QSizeF(size[0], size[1])
        else:
            return QtCore.QSizeF(0, 0)
     
    def set_pos(self, pos):
        
        self._SharedGUIDataObject.set_pos((pos.x(), pos.y()))
        
    def set_size(self, size):
        
        self._SharedGUIDataObject.set_size((size.width(), size.height()))
        
class Spacer(QtGui.QGraphicsWidget):
    
    def __init__(self, size= 5, orientation= QtCore.Qt.Horizontal, parent= None):
        
        super().__init__(parent)
        
        if orientation == QtCore.Qt.Horizontal:
            self.setPreferredSize(size, 0)
            
        elif orientation == QtCore.Qt.Vertical:
            self.setPreferredSize(0, size)
            
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
         
         
         
class NodeButton(QtGui.QGraphicsWidget):
    """Button in the upper-right edge closing the node."""
    
    _DEFAULT_WIDTH = 16
    _DEFAULT_HEIGHT = 16
    
    triggered = QtCore.Signal()
    
    def __init__(self, parent = None):
        
        super().__init__(parent)
        
        self.setPreferredSize(self._DEFAULT_WIDTH, self._DEFAULT_HEIGHT)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        
        self._pic_rect = QtCore.QRectF(0, 0, self._DEFAULT_HEIGHT, self._DEFAULT_HEIGHT)

    def paint(self, painter, option, widget):
    
        self._pic.render(painter, self._pic_rect)
    
        
    def setPreferredSize(self, width, height):
        
        self._pic_rect = QtCore.QRectF(0, 0, min(width, height), min(width, height))
        
        super().setPreferredSize(width, height)
        
    def mousePressEvent(self, event):
        
        pass
    
    def mouseReleaseEvent(self, event):
        """Is the mouse still on the button -> close node"""
        if self.boundingRect().contains(event.pos()):
            
            self.triggered.emit()
    
    def set_pic(self, pic):
        
        self._pic = pic
            
class NodeCloseButton(NodeButton):
    """Button in the upper-right edge closing the node."""
    
    _pic = QtSvg.QSvgRenderer(':/node/close.svg')

            
class NodeMinimizeButton(NodeButton):
    """Button in the upper-right edge minimizes the node."""
    
    _pic = QtSvg.QSvgRenderer(':/node/minimize.svg')
    
            
class NodeMaximizeButton(NodeButton):
    """Button in the upper-right edge maximizes the node."""
    
    _pic = QtSvg.QSvgRenderer(':/node/maximize.svg')

class NodeIterateButton(NodeButton):
    """Button for the IterationNode."""
    
    _pic = QtSvg.QSvgRenderer(':/node/square.svg')

    
            
class LabelWidget(QtGui.QGraphicsWidget):
    
    _DEFAULT_HEIGHT = 16
    
    _MIN_WIDTH = 20
    
    def __init__(self, text, parent= None):
      
        super().__init__(parent)
          
        self._text = text
          
        ### painter
        self._text_pen = QtGui.QPen(QtGui.QColor('#000000'))
        self._font = QtGui.QFont('Calibri', pointSize = 11, weight = 50)
        
          
        self._metrics = QtGui.QFontMetricsF(self._font)
        
        
        self.setPreferredSize(self._metrics.width(text), self._DEFAULT_HEIGHT)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        
        self.setMinimumWidth(self._MIN_WIDTH)
        
          
          
    def paint(self, painter, option, widget):
        """Draw text labels"""
           
        painter.setPen(self._text_pen)
        painter.setFont(self._font)
         
        rect = QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        painter.drawText(rect, QtCore.Qt.AlignVCenter, self._text, boundingRect = self.geometry()) #-self._metrics.height()/2 
           
    def text(self):
        return self._text
    
    def set_text(self, text):
        
        self._text = text
        self.setPreferredSize(self._metrics.width(text), self._DEFAULT_HEIGHT)
        
        self.update()
        
    def set_font(self, font):
        
        self._font = font
        self.update()
        
    def set_weight(self, weight):
    
        self._font.setWeight(weight)
        self.update()
        
    def font(self):
        
        return self._font
    
class ConnectorWidget(QtGui.QGraphicsItem):
    
    _CONNECTOR_DELETED = 'CONNECTOR_DELETED'
    
    def __init__(self, connector, parent = None):
        
        super().__init__(parent)
        
        self._connector = connector
        self._connected_pipe_widget = None
        
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.setFlags(self.ItemSendsScenePositionChanges)
        
        
        
        dispatcher.connect(self.delete, self._CONNECTOR_DELETED, sender= self._connector)

    def paint(self, painter, option, widget):
        
        pass
    
    def boundingRect(self):
    
        return QtCore.QRectF()
    
    
    def mousePressEvent(self, event):
        
        if event.modifiers() != QtCore.Qt.NoModifier and event.modifiers() != QtCore.Qt.ControlModifier:
            super().mousePressEvent(event)
        
        
        ### start drag
        if not self._connected_pipe_widget:
            self.scene().system().undo_save_state()
            # create provisional pipe widget
            pipe_widget = GUI.PipeWidgets.PipeWidget()
             
            pipe_widget.fix_to(self)
             
            self.scene().addItem(pipe_widget)
            self.scene().current_pipe = pipe_widget
             
            self._connected_pipe_widget = pipe_widget
        else:
            # loose existing pipe widget
            self.scene().current_pipe = self._connected_pipe_widget
            self._connected_pipe_widget.loosen_connection(self)
            
            self._connected_pipe_widget = None
            
        
        
    def mouseMoveEvent(self, event):
        
        if self.scene() and self.scene().current_pipe:
            
            if not event.pos().isNull() and (event.modifiers() == QtCore.Qt.NoModifier or event.modifiers() == QtCore.Qt.ControlModifier):
                self.scene().current_pipe.move_to(event.scenePos())
                
            elif event.modifiers() == QtCore.Qt.NoModifier or event.modifiers() == QtCore.Qt.ControlModifier:

                if self.scene().current_pipe.loose_end() == self.style():
                    self.scene().current_pipe.snap_to_connector_widget(self)
                    event.accept()

      
    def mouseReleaseEvent(self, event):
        
        if self.scene() and self.scene().current_pipe:
            
            self.scene().current_pipe.register()
            self.scene().current_pipe = None
            
            
        super().mouseReleaseEvent(event)
        
    def register(self, pipe_widget):
        
        self._connected_pipe_widget = pipe_widget
        
    def unregister(self, pipe_widget):
        
        if self._connected_pipe_widget and self._connected_pipe_widget != pipe_widget:
            raise Exception('PipeWidget not connected to this ConnectorWidget.')
        self._connected_pipe_widget = None
        
    def itemChange(self, change, value):
        """Catch item moving or deleted."""
          
        
        if change == self.ItemScenePositionHasChanged:
            
            if self._connected_pipe_widget:
                
                # actualize pipe tail position
                self._connected_pipe_widget.snap_to_connector_widget(self)
                  
        elif change == self.ItemSceneChange:
            if self._connector:
                if value:
                    # connector added to scene <- value is the scene
  
                    value.mapto({self._connector: self})
                else:
                    # connector removed from scene: scene() is the old one
                    if self._connector in self.scene().map():
                        self.scene().unmap(self._connector)
                          
          
         
        return super().itemChange(change, value)
     
     
     
     
    def style(self):
          
        return self._connector.style()
     
    def connector(self):
         
        return self._connector
     
    def delete(self):
         
        if self._connected_pipe_widget:
            self._connected_pipe_widget.unregister(self)
             
        if self.scene():
            self.scene().removeItem(self)
         
        if isinstance(self.parentItem(), GUI.PipeWidgets.BranchWidget):
            self.parentItem().update_connectors()
            
            
            