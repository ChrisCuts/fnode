# -*- coding: utf-8 -*-
'''
Created on 16.09.2015

@author: derChris
'''

from PySide import QtCore, QtGui
from pydispatch import dispatcher

import GUI.NodeWidgets
import GUI.BasicItems

import PlugIns.NodeTemplates

class OptionsGroupWidget(QtGui.QGraphicsWidget):
    
    _DEFAULT_WIDTH = 200
    _DEFAULT_HEIGHT = 18
    
    def __init__(self, connector, parent= None):
        
        super().__init__(parent)
        
        self.setPreferredSize(self._DEFAULT_WIDTH, self._DEFAULT_HEIGHT)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
            
        if isinstance(connector, PlugIns.NodeTemplates.ValueConnector):
            layout.addItem(GUI.BasicItems.LabelWidget(connector.name(), self))
            layout.addStretch(1)    
        
            edit_widget = GUI.NodeWidgets.ConnectorLineEditWidget(connector, self)
            layout.addItem(edit_widget)
            layout.setAlignment(edit_widget, QtCore.Qt.AlignVCenter)
            
            
        self.setLayout(layout)
        
            
class FunctionWidget(QtGui.QGraphicsWidget):
    
    _WIDTH = 150
    _HEIGHT = 45
    
    _BUTTON_SIZE = 12
    
    def __init__(self, node, parent= None):
        
        super().__init__(parent)
        
        self._node = node
        
        self._options_widgets = []
        
        self._active = True
        
        
        
        ### title
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self._label = GUI.BasicItems.LabelWidget(node.name(), self)
        layout.addItem(self._label)
        layout.setAlignment(self._label, QtCore.Qt.AlignVCenter)
        
        if node.options():
            button = GUI.BasicItems.NodeMinimizeButton()
            button.setPreferredSize(self._BUTTON_SIZE, self._BUTTON_SIZE)
            button.triggered.connect(self.minimize)
            layout.addItem(button)
            layout.setAlignment(button, QtCore.Qt.AlignVCenter)
            
            button = GUI.BasicItems.NodeMaximizeButton()
            button.setPreferredSize(self._BUTTON_SIZE, self._BUTTON_SIZE)
            button.triggered.connect(self.maximize)
            layout.addItem(button)
            layout.setAlignment(button, QtCore.Qt.AlignVCenter)
        
        button = GUI.BasicItems.NodeCloseButton()
        button.setPreferredSize(self._BUTTON_SIZE, self._BUTTON_SIZE)
        button.triggered.connect(self.delete)
        layout.addItem(button)
        layout.setAlignment(button, QtCore.Qt.AlignVCenter)
        
        title = QtGui.QGraphicsWidget(self)
        title.setLayout(layout)
        
        self._minimized_layout = layout
        
        ### title + options
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        layout.setContentsMargins(5, 1, 5, 3)
        layout.setSpacing(0)
        
        layout.addItem(title)
        
        for connector in node.option_connectors():
            self._options_widgets.append(OptionsGroupWidget(connector, self))
            layout.addItem(self._options_widgets[-1])
        
        self.setLayout(layout)
        self._maximized_layout = layout 
        
        ### painter
        self._pen = QtGui.QPen(QtGui.QColor('#202020'))
        self._pen.setWidth(1)
        
        self.update()
        #self.resize(self._WIDTH, self._HEIGHT)
        
        
        ### painter
        self._path = QtGui.QPainterPath()
        
        self._path.moveTo(1, 3)
        self._path.arcTo(80, 3, 8, 8, 90, -90)
        self._path.arcTo(80, 9, 8, 8, 0, -90)
        
        self._path.lineTo(0.5, 17)
        
        self.geometryChanged.connect(self._geometryChanged)
        
        
    def _geometryChanged(self):
        
        width = self.size().width()
        height = self.size().height()
        
        gradient = QtGui.QLinearGradient(width/2, 0, width/2, height)
        gradient.setColorAt(0.4, QtGui.QColor('#909090'))
        gradient.setColorAt(0.8, QtGui.QColor('#808080'))
        self._brush = QtGui.QBrush(gradient)
        
        
    def paint(self, painter, option, widget):
        
        painter.setRenderHint(painter.Antialiasing)
        
        painter.setBrush(self._brush)
        painter.drawRoundedRect(0, 0, self.size().width(), self.size().height(), 4, 4)
     
        painter.fillPath(self._path, QtGui.QBrush(QtGui.QColor('#808080')))
        
    def delete(self):
    
        self.parentItem().parentItem().remove(self._node)
        
    def minimize(self):
        
        for item in self._options_widgets:
            item.setVisible(False)
            self.layout().removeItem(item)
        
    def maximize(self):
        
        for item in self._options_widgets:
            item.setVisible(True)
            self.layout().addItem(item)
            
        #self.parentItem().parentItem()._geometryChanged()
        
    def mousePressEvent(self, event):
        
        self._active ^= 1
        
        self._selectedchanged()
        self.update()
        
        
    def _selectedchanged(self):
        
        gradient = QtGui.QLinearGradient(self.size().width()/2, 0, self.size().width()/2, self.size().height())
        
        if self._active:
            gradient.setColorAt(0.4, QtGui.QColor('#909090'))
            gradient.setColorAt(0.8, QtGui.QColor('#808080'))
        
        else:
            gradient.setColorAt(0.2, QtGui.QColor('#B0B0B0'))
            gradient.setColorAt(0.8, QtGui.QColor('#A0A0A0'))
        
        self._brush = QtGui.QBrush(gradient)
        
    
    def itemChange(self, change, value):
        
        
        return super().itemChange(change, value)
    
    
class FunctionListSlider(QtGui.QGraphicsWidget):   
    
    _WIDTH = 10
    _HEIGHT = 10
    
    class Slider(QtGui.QGraphicsWidget):
        
        _SIZE = 10
        
        def __init__(self, parent= None):
            
            super().__init__(parent)
            
            #self.setMinimumWidth(self._SIZE+10)
            
        def paint(self, painter, option, widget):
    
            painter.setRenderHint(painter.Antialiasing)
            
            painter.setPen(QtGui.QPen(QtGui.QColor('#404040')))
            painter.pen().setWidth(1)
            
            painter.setBrush(QtGui.QBrush(QtGui.QColor('#787878')))
            
            painter.drawRoundedRect(- self._SIZE/2, - self._SIZE/2, self._SIZE, self._SIZE, 3, 3)
            
        def boundingRect(self):
            
            return QtCore.QRectF(- self._SIZE/2, - self._SIZE/2, self._SIZE, self._SIZE)
        
        def mousePressEvent(self, event):
            
            pass
        
        def mouseMoveEvent(self, event):
            
            delta = event.pos().y() - event.buttonDownPos(QtCore.Qt.LeftButton).y()
        
            new_y = self.pos().y() + delta
            
            slider_length = self.parentItem().parentItem().size().height() - self._SIZE
            
            if  new_y <= self._SIZE/2:
                self.setPos(self._SIZE/2, self._SIZE/2)
                self.parentItem().set_t(0)
            elif new_y >= slider_length + self._SIZE/2:
                self.setPos(self._SIZE/2, slider_length + self._SIZE/2)
                self.parentItem().set_t(1)
            else:
                self.setPos(self._SIZE/2, new_y)
                self.parentItem().set_t((new_y - self._SIZE/2) / slider_length)
        
    slider_changed = QtCore.Signal()
    
    def __init__(self, parent= None):
        
        super().__init__(parent)
        
        self.setPreferredSize(self._WIDTH+2, self._HEIGHT)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
    
        self._slider = FunctionListSlider.Slider(self)
        self._slider.setPos(5, 5)
        
        self._t = 0
        
    def update_slider_pos(self):

        slider_length = self.parentItem().size().height() - self.Slider._SIZE

        self._slider.setPos(self.Slider._SIZE/2, self._t * slider_length + self.Slider._SIZE/2)

    def set_t(self, t):

        if t < 0:
            self._t = 0
        elif t > 1:
            self._t = 1
        else:
            self._t = t
        
        self.update_slider_pos()
        self.slider_changed.emit()
        
    def t(self):
        
        return self._t
        
class FunctionListBox(QtGui.QGraphicsWidget):
    
    _WIDTH = 400
    _HEIGHT = 120
    
    _UPDATE_FUNCTION_SELECTION_WIDGET = 'UPDATE_FUNCTION_SELECTION_WIDGET'
    
    
    def __init__(self, node, parent= None):
        
        super().__init__(parent)
        
        self._node = node
        
        self.setPreferredSize(self._WIDTH, self._HEIGHT)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
    
        self.setFlag(self.ItemClipsChildrenToShape, True)
        
        self._pen = QtGui.QPen(QtGui.QColor('#202020'))
        self._pen.setWidth(1)
        self._brush = QtGui.QBrush(QtGui.QColor('#C0C0C0'))
        
        slidewidget = QtGui.QGraphicsWidget(self)
        
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Expanding)
        
        for function_node in self._node.get_function_nodes():
            item = FunctionWidget(function_node, slidewidget)
            layout.addItem(item)
            
        
        slidewidget.setLayout(layout)
        
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        layout.setContentsMargins(1, 0, 0, 0)
        layout.setSpacing(1)
        
        layout.addItem(slidewidget)
        slidebar = FunctionListSlider(self)
        layout.addItem(slidebar)
        
        self.setLayout(layout)
        self._slidewidget = slidewidget
        self._slidebar = slidebar
        
        
        self._slidewidget.geometryChanged.connect(self._geometryChanged)
        
        self._slidebar.slider_changed.connect(self.scroll)
        
        dispatcher.connect(self._update_list, signal= self._UPDATE_FUNCTION_SELECTION_WIDGET, sender= node)
        
    def paint(self, painter, option, widget):
        
        painter.setRenderHint(painter.Antialiasing)
        
        
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        
        painter.drawRect(0, 0, self.size().width(), self.size().height())
        
        if not self._node.get_function_nodes():
            painter.setFont(QtGui.QFont('Calibri', 9))
            painter.drawText(QtCore.QRectF(0, 0, self.size().width(), self.size().height()),
                             QtCore.Qt.AlignCenter, 'Drop function nodes here..')
        
    @QtCore.Slot()    
    def scroll(self):
        
        slide_length = self._slidewidget.size().height() - self.size().height()
        self._slidewidget.setPos(0, - slide_length * self._slidebar.t())
        
    def _geometryChanged(self):
        
        self._slidebar.update_slider_pos()
        
        if self._slidewidget.size().height() <= self.size().height():
            self.layout().removeItem(self._slidebar)
            self._slidebar.setVisible(False)
            
        elif self.layout().itemAt(self.layout().count()-1) != self._slidebar:
            self.layout().addItem(self._slidebar)
            self._slidebar.setVisible(True)
            
        self.scroll()
        
    def wheelEvent(self, event):
        
        if self._slidebar.isVisible():
            self._slidebar.set_t(self._slidebar.t() - event.delta()/2400)
        else:
            super().wheelEvent(event)
        
    def remove(self, function_node):
        
        self._node.remove_function_node(function_node)
        
        
    def _update_list(self):
        
        for child in self._slidewidget.childItems():
            child.setParent(None)
         
        
        for function_node in self._node.get_function_nodes():
            self._slidewidget.layout().addItem(FunctionWidget(function_node, self._slidewidget))
        
        self._slidewidget.updateGeometry()
        self.updateGeometry()
        self.parentItem().updateGeometry()
        
        
class FunctionSelectionNodeWidget(GUI.NodeWidgets.NodeWidget):
    
    _UPDATE_FUNCTION_SELECTION_WIDGET = 'UPDATE_FUNCTION_SELECTION_WIDGET'
    
    def __init__(self, node):
        
        super().__init__(node)
        
        self._node = node
        
        self.setAcceptDrops(True)
        
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        
        layout.addItem(GUI.BasicItems.Spacer(parent= self))
        layout.addItem(FunctionListBox(node, self))
        layout.addItem(GUI.BasicItems.Spacer(parent= self))
        
        frame = QtGui.QGraphicsWidget(self)
        frame.setLayout(layout)
        
        self.layout().insertItem(self.layout().count()-2, GUI.BasicItems.Spacer(5, QtCore.Qt.Vertical, self))
        self.layout().insertItem(self.layout().count()-2, frame)
        
        self.resize(self.size().width(), self.size().height())
        
        dispatcher.connect(self._update_connectors, signal= self._UPDATE_FUNCTION_SELECTION_WIDGET, sender= node)
        
    
    def dropEvent(self, event):
        
        if event.source().__class__.__name__ == 'SideBarTree':
            """Create new FunctionNode"""
            
            sidebar = event.source()
                
            index = sidebar.selectedIndexes()[0]
            item = index.model().itemFromIndex(index)
            data = item.data()
            
            if 'type' in data and data['type'] == 'mFunctionNode':
                self._node.add_function(data)
        
        
        