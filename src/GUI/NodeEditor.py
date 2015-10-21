# -*- coding: utf-8 -*-
'''
Created on 10.08.2015

@author: derChris
'''

from PySide import QtCore, QtGui, QtSvg
from pydispatch import dispatcher


import GUI.NodeWidgets
import GUI.PipeWidgets
import GUI.BasicItems
import GUI.FunctionSelectionNodeWidget

import PlugIns.NodeTemplates
import PlugIns.MATLAB.MATLAB
import Pipe
import FunctionSelectionNode


### REG EXP
_NUMBER_DOUBLE_RE  = QtCore.QRegExp('[+-]?[0-9]+((\.|,)[0-9]+)?([eE][+-]?[0-9]+)?')

### SIGNALS
_FUNCTION_NODE_OPTIONS_VALUE_UPDATED = 'FUNCTION_NODE_OPTIONS_VALUE_UPDATED'

_DON_T_CREATE_WIDGET = 'DON_T_CREATE_WIDGET'


class DropItem(QtGui.QGraphicsItem):
    
    def __init__(self):
        
        super().__init__()
        
        self.setAcceptDrops(True)
        
    def paint(self, painter, option, widget):
        
        pass
    
    def boundingRect(self):
        
        return QtCore.QRectF(-1000, -1000, 2000, 2000) 
    
    
    def dragEnterEvent(self, event):
        
        event.accept()
        
    
        
    def dropEvent(self, event):
        
        if event.source().__class__.__name__ == 'SideBarTree':
            
            """Create new FunctionNode"""
            sidebar = event.source()
                
            index = sidebar.selectedIndexes()[0]
            item = index.model().itemFromIndex(index)
            data = item.data()
                
            pos = event.pos()
    
            data.update({'gui_data': {'pos': (pos.x(), pos.y())}})
            self.scene().system().add_node(data)
        
    def update_size(self, new_rect):
        
        self.bounds = new_rect
        
        try:
            self.update()
        except RuntimeError as e:
            if e.args[0] != 'Internal C++ object (DropItem) already deleted.':
                raise e
             
class NodeScene(QtGui.QGraphicsScene):
    
    def __init__(self, parent = None, system = None):
        
        super().__init__(parent)
        
        self._system = system
        self.current_pipe = None
        self.current_branch = None
        self.branch_mark = None
        
        self._map = {}
        
        self._dropitem = DropItem()
        self.addItem(self._dropitem)
        
        
        self.sceneRectChanged.connect(self._dropitem.update_size)
        
    def system(self):
        
        return self._system
        
        
    def map(self):
        
        return self._map
    
    def mapto(self, mapping):
        
        self._map.update(mapping)
        
        
    def unmap(self, key):
        
        self._map.pop(key)
        
    def keyReleaseEvent(self, event):
        
        if event.key() == QtCore.Qt.Key_Control:
            if self.current_branch:
                self.current_branch = None
            if self.branch_mark:
                self.removeItem(self.branch_mark)
                self.branch_mark = None
                
        super(NodeScene, self).keyReleaseEvent(event)
        
    def mouseMoveEvent(self, event):
        
        if self.current_pipe:
            
            item = self.itemAt(event.scenePos(), QtGui.QTransform())
            
            if isinstance(item, (GUI.NodeWidgets.NodeConnectorItem, GUI.PipeWidgets.BranchWidget)):
                item.mouseMoveEvent(event)
            
        if not event.isAccepted():  
                  
            super(NodeScene, self).mouseMoveEvent(event)
                
    def selectedNodes(self):
        
        nodes = []
        
        for widget in self.selectedItems(): 
            if isinstance(widget, (GUI.NodeWidgets.NodeWidget, GUI.PipeWidgets.BranchWidget)):
                nodes.append(widget.node())
            
        return nodes
    
    def dropitem(self):
        
        return self._dropitem
    
    def save_to_svg(self):
        
        svgGen = QtSvg.QSvgGenerator()

        svgGen.setFileName( r"C:\Users\derChris\Desktop\temp.svg" )
        svgGen.setSize(QtCore.QSize(200, 200))
        svgGen.setViewBox(QtCore.QRect(0, 0, 200, 200))
        svgGen.setTitle("SVG Generator Example Drawing")
        svgGen.setDescription("An SVG drawing created by the SVG Generator "
                                    "Example provided with Qt.")
        
        painter = QtGui.QPainter( svgGen )
        self.render( painter )
        painter.end()
        
###################
### NODEEDITOR
###################  
class NodeEditor(QtGui.QGraphicsView):
    """A QGraphicsView with zoom abilities"""
    
    _NODE_CREATED = 'NODE_CREATED'
    _CONNECTOR_CREATED = 'CONNECTOR_CREATED'
    _PIPE_CREATED = 'PIPE_CREATED'
    _SYSTEM_CLEARED = 'SYSTEM_CLEARED'
    
    def __init__(self, parent = None, system = None):
    
        #self._scene = QtGui.QGraphicsScene()
        self._scene = NodeScene(system = system)
        super().__init__(self._scene, parent)
        
        self._system = system
        
        self._function_node_map = {}
        
        #self._scene.setSceneRect(-parent.width()/2, -parent.height()/2, parent.width()-20, parent.height()-20)
        
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setDragMode(self.RubberBandDrag)
        
        dispatcher.connect(self.add_function_widget, signal=self._NODE_CREATED)
        dispatcher.connect(self.add_pipe_widget, signal=self._PIPE_CREATED)
        dispatcher.connect(self.add_connector_widget, signal=self._CONNECTOR_CREATED)
        dispatcher.connect(self.clear, signal=self._SYSTEM_CLEARED)
      
      
        self.horizontalScrollBar().valueChanged.connect(self._resize_dropitem)
        self.verticalScrollBar().valueChanged.connect(self._resize_dropitem)
        
         
        
    def _resize_dropitem(self):
        
        self._scene.dropitem().update_size(self.mapToScene(self.rect()).boundingRect())
        
    def wheelEvent(self, event):
        """Sets scale factor and scales the QGraphicsView"""
        
        if event.modifiers() == QtCore.Qt.ControlModifier:
            scale_factor = 1 + event.delta() / 2400
            self.scale(scale_factor, scale_factor)
        else:
            super().wheelEvent(event)
        
        
    def keyPressEvent(self, event):
    
        if event.key() == QtCore.Qt.Key_Control:
            self.setDragMode(self.ScrollHandDrag)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.viewport().setCursor(QtCore.Qt.ArrowCursor)
            
        elif event.key() == QtCore.Qt.Key_A and event.modifiers() == QtCore.Qt.ControlModifier:
            '''select all'''
            for item in self.items():
                if isinstance(item, GUI.NodeWidgets.NodeWidget):
                    item.setSelected(True)
        
        elif event.key() == QtCore.Qt.Key_Delete:
            '''delete selected nodes'''
            #self._system.undo_save_state()
            self._system.undo_save_state()
            for node in self.scene().selectedNodes():
                
                node.delete()
                
        ### debug            
        elif event.key() == QtCore.Qt.Key_P and event.modifiers() == QtCore.Qt.ControlModifier:
            '''print all pipes'''
            data = self._system.get_data()
            if 'pipes' in data:
                for pipe in data['pipes']:
                    print('PIPE:')
                    if 'connectors' in pipe:
                        for con in pipe['connectors']:
                            print('connector:\n', con)
                    print('\n')
            
            print('current pipe:', self.scene().current_pipe)
        
        elif event.key() == QtCore.Qt.Key_S and event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier:
            '''save scene to svg'''
            print('save to svg')
            self.scene().save_to_svg()
            
        super(NodeEditor, self).keyPressEvent(event)
        
    
    def keyReleaseEvent(self, event):
        
        if event.key() == QtCore.Qt.Key_Control:
            self.setDragMode(self.RubberBandDrag)
        
        
            
        super(NodeEditor, self).keyReleaseEvent(event)
    
    def mousePressEvent(self, event):
        
        if event.button() == QtCore.Qt.MiddleButton:
            
            self.setDragMode(self.ScrollHandDrag)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.viewport().setCursor(QtCore.Qt.ArrowCursor)
            
            event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress, event.pos(), QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, event.modifiers())
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
            self.viewport().setCursor(QtCore.Qt.ArrowCursor)
        
    def mouseReleaseEvent(self, event):
        
        if event.button() == QtCore.Qt.MiddleButton:
            event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, event.pos(), QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, event.modifiers())
            super().mouseReleaseEvent(event)
            
            self.setDragMode(self.RubberBandDrag)
            
        else:
            super().mouseReleaseEvent(event)
            self.viewport().setCursor(QtCore.Qt.ArrowCursor)
            
    def add_function_widget(self, sender):
        
        widget = None
        
        if isinstance(sender, Pipe.Branch):
            
            widget = GUI.PipeWidgets.BranchWidget(sender)
            
        elif isinstance(sender, PlugIns.MATLAB.MATLAB.matFileNode):
            
            widget = GUI.NodeWidgets.MatFileWidget(sender)
            
        elif isinstance(sender, FunctionSelectionNode.FunctionSelectionNode):
            
            widget = GUI.FunctionSelectionNodeWidget.FunctionSelectionNodeWidget(sender)
            
        elif isinstance(sender, PlugIns.NodeTemplates.FunctionNodeTemplate):
            
            widget = GUI.NodeWidgets.FunctionWidget(sender)
        
        if widget:
            self.scene().addItem(widget)
        
    def add_pipe_widget(self, sender, flags):
        
        if flags == _DON_T_CREATE_WIDGET:
            self.scene().current_pipe = None
            return
        
        
        input_connector_widget = None
        output_connector_widget = None
        
        if sender.connector_at_output() in self.scene().map():
            input_connector_widget = self.scene().map()[sender.connector_at_output()]
        if sender.connector_at_input() in self.scene().map():
            output_connector_widget = self.scene().map()[sender.connector_at_input()]
        
        if input_connector_widget and output_connector_widget:
            pipe_widget = GUI.PipeWidgets.PipeWidget(sender, input_connector_widget, output_connector_widget)   
        
            self.scene().addItem(pipe_widget)
        
    def add_connector_widget(self, sender, node):
        
        if isinstance(node, Pipe.Branch) and node in self.scene().map():
            
            widget = GUI.BasicItems.ConnectorWidget(sender, self.scene().map()[node])
            widget.setFlag(widget.ItemStacksBehindParent, True)
            
            self.scene().mapto({sender: widget})

    def clear(self, sender):
        
        if sender == self._system:
            #self.scene().clear()
            for item in self.scene().items():
                
                if item.scene() == self.scene():
                    self.scene().removeItem(item)
        
    
##################
### FUNCTIONNODE
##################

    
if __name__ == '__main__':
    
    import sys
    
    tmp = {1:2}
    
    try:
        tmp.remove(2)
    except KeyError:
        print(sys.exc_info())
