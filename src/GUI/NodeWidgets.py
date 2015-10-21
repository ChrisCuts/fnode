# -*- coding: utf-8 -*-
'''
Created on 16.09.2015

@author: derChris
'''

from pydispatch import dispatcher


from PySide import QtCore, QtGui, QtSvg

import PlugIns.NodeTemplates

import GUI.BasicItems


_NODE_RADIUS = 5
        
        

        
class NodeResizeArea(QtGui.QGraphicsWidget):
    
    _WIDTH = 20
    _HEIGHT = 8
    
    
    
    def __init__(self, parent= None):
        
        super().__init__(parent)
        
        self.setPreferredSize(self._WIDTH, self._HEIGHT)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        
        self._path = QtGui.QPainterPath()
        self._path.moveTo(0, self._HEIGHT - 0.5)
        self._path.arcTo(self._WIDTH - _NODE_RADIUS*2 - 0.5, self._HEIGHT - _NODE_RADIUS*2 - 0.5,
                         _NODE_RADIUS*2, _NODE_RADIUS*2, -90, 90)
        self._path.lineTo(self._WIDTH - 0.5, 0)
        self._path.arcTo(0, 0, _NODE_RADIUS*2, _NODE_RADIUS*2, 90, 90)
        self._path.lineTo(0, self._HEIGHT - 0.5)
        
        self._brush = QtGui.QBrush(QtGui.QColor('#707070'))
        
        
    def paint(self, painter, option, widget):
        
        painter.setRenderHint(painter.Antialiasing)
        #painter = QtGui.QPainter()
        #painter.setBrush(QtGui.QBrush(QtGui.QColor('#000000')))
        #painter.drawRoundedRect(0, 0, 15, 12, 5, 5)
        
        painter.fillPath(self._path, self._brush)
        
    def mousePressEvent(self, event):
        
        for item in self.scene().items():
            item.setSelected(False)
            
        self.parentItem().setSelected(True)
        
    def mouseMoveEvent(self, event):
        
        delta = event.pos() - event.lastPos()
        
        self.parentItem().resize(self.parentItem().width() + delta.x(), self.parentItem().height() + delta.y())
        
     

        
     
class NodeTitle(QtGui.QGraphicsWidget):
            
    _HEIGHT = 22
    _WIDTH = 150
    
    def __init__(self, text, parent):
        
        super().__init__(parent)
        
        self.setPreferredSize(200, 22)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        
        label = GUI.BasicItems.LabelWidget(text, self)
        label.set_weight(75)
        #label.setStyleSheet('font: Calibri 11pt; background-color: transparent; font-weight: 700')
        #label.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal, self)
        layout.setContentsMargins(10, 3, 5 ,0)
        layout.setSpacing(8)
        
        layout.addItem(label)
        self._label = label
        
        layout.setAlignment(label, QtCore.Qt.AlignVCenter)
        
        button = GUI.BasicItems.NodeCloseButton()
        button.triggered.connect(self.parentItem().delete)
                                 
        layout.addItem(button)
        layout.setAlignment(button, QtCore.Qt.AlignVCenter)
        
        self._path = QtGui.QPainterPath()
#         self._path.moveTo(0.5, self._HEIGHT)
#         self._path.arcTo(self._label.size().width() - _NODE_RADIUS*2, self._HEIGHT - _NODE_RADIUS*2,
#                          _NODE_RADIUS*2, _NODE_RADIUS*2, -90, 90)
#         self._path.lineTo(self._label.size().width(), 0.5)
#         self._path.arcTo(0.5, 0.5, _NODE_RADIUS*2, _NODE_RADIUS*2, 90, 90)
#         self._path.lineTo(0.5, self._HEIGHT)
        
        self._brush = QtGui.QBrush(QtGui.QColor('#707070'))
        
        self.geometryChanged.connect(self._geometryChange)
        self.parentItem().selectedChange.connect(self._selectedChanged)
        
    def paint(self, painter, option, widget):
        
        painter.setRenderHint(painter.Antialiasing)
        
        painter.fillPath(self._path, self._brush)
        
    def _geometryChange(self):
        
        self._path = QtGui.QPainterPath()
        self._path.moveTo(0.5, self._HEIGHT)
        self._path.arcTo(self._label.size().width() - _NODE_RADIUS*2 + 14, self._HEIGHT - _NODE_RADIUS*2,
                         _NODE_RADIUS*2, _NODE_RADIUS*2, -90, 90)
        self._path.lineTo(self._label.size().width() + 14, 0.5)
        self._path.arcTo(0.5, 0.5, _NODE_RADIUS*2, _NODE_RADIUS*2, 90, 90)
        self._path.lineTo(0.5, self._HEIGHT)
        
    def _selectedChanged(self, value):
        
        if value:
            self._brush.setColor(QtGui.QColor('#606060'))
        else:
            self._brush.setColor(QtGui.QColor('#707070'))
        
class NodeConnectorItem(GUI.BasicItems.ConnectorWidget):
    
    def __init__(self, connector= None, parent= None):
        
        
        super().__init__(connector, parent)
        
        ### painter
        self._radius = 4
        self._pen = QtGui.QPen(QtGui.QColor('#404040'))
        self._pen.setWidth(1)
        self._brush = QtGui.QBrush(QtGui.QColor('#FFFFFF'))
        
        self.setZValue(2)
     
        self._rect = QtCore.QRectF(-self._radius, -self._radius, 2*self._radius, 2*self._radius)

        self.parentItem().parentItem().parentItem().parentItem().selectedChange.connect(self._selectedChanged)
        
    def paint(self, painter, option, widget):
          
        painter.setRenderHint(painter.Antialiasing)
        
        
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        
        painter.drawEllipse(self._rect)
          
    def boundingRect(self):
        
        return self._rect

    def itemChange(self, change, value):
        
        return super().itemChange(change, value) 
          
    def _selectedChanged(self, value):
        
        if value:
            self._pen.setColor(QtGui.QColor('#202020'))
        else:
            self._pen.setColor(QtGui.QColor('#404040'))
                           
                           
class NodeConnectorWidget(QtGui.QGraphicsWidget):
    
    def __init__(self, connector, parent):
        
        super().__init__(parent)
        
        self.setPreferredSize(0, 0)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        NodeConnectorItem(connector, self)    


    
###################
### LineEdit
###################

class ConnectorLineEditWidget(QtGui.QGraphicsProxyWidget):
    
    _VALUE_UPDATED = 'VALUE_CONNECTOR_VALUE_UPDATED'
    
    _DEFAULT_HEIGHT = 16
              
    _DEFAULT_OPACITY = 0.8
      
    def __init__(self, connector, parent):
        
        super().__init__(parent)
        
        self.setContentsMargins(0, 0, 0, 0)
        
        if isinstance(connector.value(), str):
            self._lineedit = QtGui.QLineEdit(connector.value())
            self._lineedit.setFixedHeight(self._DEFAULT_HEIGHT)
            self._lineedit.setFixedWidth(50)
            self._lineedit.setStyleSheet('QLineEdit {Background: #D0D0D0; border: 1px solid #808080}')
            self._lineedit.editingFinished.connect(lambda : connector.set_value(self._lineedit.text()))
            self._lineedit.setContentsMargins(0, 0, 0, 0)
            self.setWidget(self._lineedit)
        else:
            self._lineedit = None
        
        self.setZValue(1)
        
        self.setOpacity(self._DEFAULT_OPACITY)
        
        ### animation
        self._animation = QtCore.QPropertyAnimation(self, 'opacity')
        self._animation.setStartValue(self.opacity())
        self._animation.setDuration(150)
        
        dispatcher.connect(self.set_text, signal= self._VALUE_UPDATED, sender= connector)
        
    def set_text(self, sender, value):
        
        self._lineedit.setText(value)
    
    def setVisible(self, value):
        
        self._animation.setStartValue(self._animation.currentValue())
        self._animation.setEndValue(float(value)* self._DEFAULT_OPACITY)
        self._animation.start()
          
class InteratorControlWidget(QtGui.QGraphicsWidget):
    
    _DEFAULT_WIDTH = 13
    _DEFAULT_HEIGHT = 13
    
    _ITERATE_PIC = QtSvg.QSvgRenderer(':/node/iterate.svg')
    _SQUARE_PIC = QtSvg.QSvgRenderer(':/node/square.svg')
    
    _ITERATOR_UPDATED = 'ITERATOR_UPDATED'
    
    def __init__(self, connector, parent):
        
        super().__init__(parent)
        
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        layout.setContentsMargins(0, 0, 0, 0)
        self._button = GUI.BasicItems.NodeIterateButton()
        self._button.triggered.connect(connector.increase_iteration_dimension)
        self._button.setPreferredSize(15, 15)
        layout.addItem(self._button)
        layout.setAlignment(self._button, QtCore.Qt.AlignVCenter)
        
        self._label = GUI.BasicItems.LabelWidget('hey')
        layout.addItem(self._label)
        layout.setAlignment(self._label, QtCore.Qt.AlignVCenter)
        
        self.setLayout(layout)
        
        self._text = ''
        
        self._connector = connector
        
        dispatcher.connect(self._update, self._ITERATOR_UPDATED, sender= connector)
        
#     def paint(self, painter, option, widget):
#     
#         self._pic.render(painter, self._pic_rect)
        
    def _update(self):
    
        iterate_via, size = self._connector.display()
        
        if size:
            self._label.set_text(str(size))
        else:
            self._label.set_text('')
        if iterate_via:
            self._button.set_pic(self._ITERATE_PIC)
        else:
            self._button.set_pic(self._SQUARE_PIC)
    
        self.update()
        
class ConnectorGroupWidget(QtGui.QGraphicsWidget):
    
    _DEFAULT_WIDTH = 200
    _DEFAULT_HEIGHT = 18
    
    _PIPE_CONNECTION_STATUS = 'PIPE_CONNECTION_STATUS'
    
    def __init__(self, connector, parent= None):
        
        super().__init__(parent)
        
        self._connector = connector
        
        self.setPreferredSize(self._DEFAULT_WIDTH, self._DEFAULT_HEIGHT)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self._edit_widget = None
                
        
        if isinstance(connector, PlugIns.NodeTemplates.Connector):
            
            nodeconnectorwidget = NodeConnectorWidget(connector, self)
            layout.addItem(nodeconnectorwidget)
            layout.setAlignment(nodeconnectorwidget, QtCore.Qt.AlignVCenter)
            
            layout.addItem(GUI.BasicItems.Spacer())
            layout.addItem(GUI.BasicItems.LabelWidget(connector.name(), self))
            
            layout.addStretch(1)    
            
            
            if isinstance(connector, PlugIns.NodeTemplates.ValueConnector):
                self._edit_widget = ConnectorLineEditWidget(connector, self)
                layout.addItem(self._edit_widget)
                layout.setAlignment(self._edit_widget, QtCore.Qt.AlignVCenter)
                layout.addItem(GUI.BasicItems.Spacer())
            
            elif isinstance(connector, PlugIns.NodeTemplates.DataConnector):
                iterator_widget = InteratorControlWidget(connector, self)
                layout.addItem(iterator_widget)
                layout.setAlignment(self._edit_widget, QtCore.Qt.AlignVCenter)
                layout.addItem(GUI.BasicItems.Spacer())
            
            
            
            self.setLayout(layout)
            
            if connector.style() == 'output':
                self.setLayoutDirection(QtCore.Qt.RightToLeft)
            
        
        dispatcher.connect(self.set_edit_widget_visible, signal= self._PIPE_CONNECTION_STATUS, sender= connector)
        
    def connector(self):
    
        return self._connector
        
    def set_edit_widget_visible(self, status):
        
        if self._edit_widget:
            self._edit_widget.setVisible(not status)
    
class NodeWidget(QtGui.QGraphicsWidget):
    """Node of the Node Editor"""
            
    _CONNECTOR_TOP = 34
    _CONNECTOR_DISTANCE = 15
    _DEFAULT_HEIGHT = 300
    _DEFAULT_WIDTH = 220
    
    _MIN_WIDTH = 50
    _MAX_WIDTH = 500
    
    _MIN_HEIGHT = 0
    _MAX_HEIGHT = 1000
    
    _NODE_DELETED = 'NODE_DELETED'
    
    selectedChange = QtCore.Signal(bool)
    
    def __init__(self, node):
        """Initialize NodeWidget"""
        
        super().__init__()
        
        self._gui_data = GUI.BasicItems.SharedGUIDataQTProxy(node.gui_data())
        
        
        self.setPos(self._gui_data.pos())
        
        self._node = node
        
        ### painter        
        self._pen = QtGui.QPen(QtGui.QColor('#404040'))
        self._pen.setWidth(1)
        self._pen_selected = QtGui.QPen(QtGui.QColor('#202020'))
        self._pen_selected.setWidth(1)
        
        self.setFlags(self.ItemIsMovable \
                      | self.ItemSendsGeometryChanges \
                      | self.ItemIsSelectable)
        
        
        ### layout
        # header
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        layout.setMaximumWidth(400)
        layout.setMinimumWidth(150)
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addItem(NodeTitle(node.name(), self))
        layout.addItem(GUI.BasicItems.Spacer(5, QtCore.Qt.Vertical, parent= self))
        
        # connectors
        self._connector_field = QtGui.QGraphicsWidget(self)
        
        connectors_layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        connectors_layout.setContentsMargins(0, 0, 0, 0)
        connectors_layout.setSpacing(0)
        
        for connector in node.connectors():
            connectors_layout.addItem(ConnectorGroupWidget(connector, self._connector_field))

        self._connector_field.setLayout(connectors_layout)
        layout.addItem(self._connector_field)
        
        # footer
        layout.addItem(GUI.BasicItems.Spacer(5, QtCore.Qt.Vertical, parent= self))
        resizearea = NodeResizeArea(self)
        layout.addItem(resizearea)
        layout.setAlignment(resizearea, QtCore.Qt.AlignRight)
        self.setLayout(layout)
        
        
        self.resize(self._gui_data.size().width(), self._gui_data.size().height())
        
        
        dispatcher.connect(self.remove_from_scene, self._NODE_DELETED, node)
        
        
    def resize(self, width, height):
        """Initialize or actualize paths and gradients"""
        
        super().resize(width, height)
        
        width = self.size().width()
        height = self.size().height()
        
        radius = 5
        
        gradient = QtGui.QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.2, QtGui.QColor('#B0B0B0'))
        gradient.setColorAt(0.8, QtGui.QColor('#909090'))
        self._brush = QtGui.QBrush(gradient)
        gradient.setColorAt(0.2, QtGui.QColor('#A0A0A0'))
        gradient.setColorAt(0.8, QtGui.QColor('#797979'))
        self._brush_title = QtGui.QBrush(gradient)
        gradient.setColorAt(0.2, QtGui.QColor('#808080'))
        gradient.setColorAt(0.8, QtGui.QColor('#505050'))
        self._brush_title_selected = QtGui.QBrush(gradient)
        
        
        self._title_path = QtGui.QPainterPath()
        self._title_path.moveTo(0, 22)
        self._title_path.arcTo(0, 0, radius*2, radius*2, 180, -90)
        self._title_path.arcTo(  width - radius*2, 0, radius*2, radius*2, 90, -90)
        self._title_path.lineTo( width, 22)
        self._title_path.closeSubpath()
        
        self._rounded_rect = QtGui.QPainterPath()
        self._rounded_rect.addRoundedRect(0, 0, width, height, radius, radius)
        
        self._gui_data.set_size(self.size())
        
        
    def paint(self, painter, option, widget):
        
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        ### background
        painter.fillPath(self._rounded_rect, self._brush)
        
#         if self.isSelected():
#             painter.fillPath(self._title_path, self._brush_title_selected)
#         else:
#             painter.fillPath(self._title_path, self._brush_title)
        
        ### border
        painter.setPen(self._pen)
            
        painter.drawPath(self._rounded_rect)

            
    def boundingRect(self):
        
        return QtCore.QRectF(- 10, 0, self.width() + 10, self.height())
        #return QtCore.QRectF(0, 0, self._width, self._height)
    
    
    def remove_from_scene(self):
        
        self.scene().removeItem(self)

    def width(self):
         
        return self.geometry().width()

    def height(self):
        
        return self.geometry().height()
    
    def itemChange(self, change, value):
        """Catch item moving or deleted."""
        
        if change == self.ItemPositionChange:
            self._gui_data.set_pos(value)
        elif change == self.ItemSelectedChange:
            
            if value:
                self._pen.setColor(QtGui.QColor('#202020'))
            else:
                self._pen.setColor(QtGui.QColor('#404040'))
            self.selectedChange.emit(value)
            
        return super().itemChange(change, value) 
    
    def node(self):
        return self._node
    
    def delete(self):
        
        self._node.remove_node()
        
        
    def _update_connectors(self):
        
        self.prepareGeometryChange()
        
        existing_connectors = set()
        
        for child in self._connector_field.childItems():
            
            if child.connector() not in self._node.connectors():
                child.setParent(None)
        
            existing_connectors.add(child.connector())
            
        for connector in self._node.connectors():
            
            if connector not in existing_connectors:
                self._connector_field.layout().addItem(ConnectorGroupWidget(connector, self._connector_field))

        self._connector_field.updateGeometry()
            
        self.resize(self.size().width(), self.size().height())
        
class FunctionWidget(NodeWidget):
    
    _MATLAB_ENGINE_STARTET = 'MATLAB_ENGINE_STARTET'
    
    def contextMenuEvent(self, event):
    
        if self not in self.scene().selectedItems():
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.setSelected(True)
            
        if self._context_menu:
            self._context_menu.exec_(event.screenPos(), None)
            
        
    def itemChange(self, change, value):
        
        if change == self.ItemSceneChange:
            
            if value:
                context_menu   = QtGui.QMenu()
            
                cm_edit_code  = context_menu.addAction('Edit code')
                
                cm_edit_code.triggered.connect(lambda : value.system().plugin_manager()['MATLAB'].edit_code(self._node.path() + self._node.name()))
                #cm_edit_code.setEnabled(False)
                self._cm_edit_code_enable = lambda : cm_edit_code.setEnabled(True)
                dispatcher.connect(self._cm_edit_code_enable, signal= self._MATLAB_ENGINE_STARTET)
                
                context_menu.addSeparator()
                cm_cut        = context_menu.addAction('Cut')
                cm_cut.triggered.connect(lambda : value.system().cut(value.selectedNodes()))
                cm_copy       = context_menu.addAction('Copy')
                cm_copy.triggered.connect(lambda : value.system().copy(value.selectedNodes()))
                cm_paste      = context_menu.addAction('Paste')
                cm_paste.triggered.connect(value.system().paste)
                context_menu.addSeparator()
                #cm_properties = 
                context_menu.addAction('Properties')
                
                self._context_menu = context_menu
            else:
                self._context_menu = None
            
        
        return super().itemChange(change, value)
    
    
class MatFileWidget(NodeWidget):
    
    
    pass