# -*- coding: utf-8 -*-
'''
Created on 16.09.2015

@author: derChris
'''


from PySide import QtGui, QtCore, QtSvg
from pydispatch import dispatcher
import itertools

import GUI.BasicItems
import GUI.NodeWidgets


class CloseHoverItem(QtGui.QGraphicsItem):
    
    triggered = QtCore.Signal()
    
    
    _DEFAULT_WIDTH = 12
    _DEFAULT_HEIGHT = 12
    
    
    _bounds = QtCore.QRectF(-_DEFAULT_WIDTH/2, -_DEFAULT_HEIGHT/2, _DEFAULT_WIDTH, _DEFAULT_HEIGHT)
    _pic = QtSvg.QSvgRenderer(':/close_inverted.svg')
    _pic_rect = _bounds
    
    
    
    def __init__(self, parent):
        
        super().__init__(parent)
        
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        
        
        
    def boundingRect(self):
        
        return self._bounds 

    def paint(self, painter, options, widget):
        
        self._pic.render(painter, self._pic_rect)
        
    def mousePressEvent(self, event):
        
        pass
    
    def mouseReleaseEvent(self, event):
        """Is the mouse still on the button -> close node"""
        if self.boundingRect().contains(event.pos()):
            
            self.triggere.emit()
            
    
            
class BranchWidget(QtGui.QGraphicsItem):
    
    _BRANCH_CREATED = 'BRANCH_CREATED'
    _BRANCH_DELETED = 'BRANCH_DELETED'
    
    _NODE_DELETED = 'NODE_DELETED'
    
    _CONNECTOR_CREATED = 'CONNECTOR_CREATED'
    _CONNECTOR_DELETED = 'CONNECTOR_DELETED'
    
    _WIDTH = 16
    _HEIGHT = 6
    _RADIUS = 1.5
    
    _BRUSH = QtGui.QBrush(QtGui.QColor('#808080'))
    _BRUSH_SELECTED = QtGui.QBrush(QtGui.QColor('#606060'))
    
    def __init__(self, branch):
        
        super().__init__()
        
        
        self._branch = branch
        #self._connected_pipe_widget = pipe_widget
        self._connected_pipe_widgets = []
        
        self._gui_data = GUI.BasicItems.SharedGUIDataQTProxy(branch.gui_data())
        self.setPos(self._gui_data.pos())
        
        #TODO: implement style
        connector = branch.free_connector('input')
        self._input_connector = GUI.BasicItems.ConnectorWidget(connector, self)
        self._input_connector._style = 'input'
        self._input_connector.setFlag(self.ItemStacksBehindParent, True)
        
        
        self._provisional_connector = None
        
        self.setZValue(11)
        
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsMovable \
                      | self.ItemSendsScenePositionChanges \
                      | self.ItemIsSelectable)
        
        
        ### painter
        self._pen = QtGui.QPen(QtGui.QColor('#202020'))
        self._pen.setWidth(1)
        self._brush = self._BRUSH
        
        
        self._rect = QtCore.QRectF(-self._WIDTH/3, -self._HEIGHT/2, self._WIDTH, self._HEIGHT)
        self._bounds = QtCore.QRectF(-10, -12, 20, 22)
        
        self._close_button = CloseHoverItem(self)
        self._close_button.setPos(12, -10)
        self._close_button.setVisible(False)
        #self._close_button.triggered.connect(self.delete)
        
        
        ### event listening
        dispatcher.connect(self.delete, signal=self._NODE_DELETED, sender= branch)
        
        
    def paint(self, painter, option, widget):
        
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        
        
        painter.drawRoundedRect(self._rect, self._RADIUS, self._RADIUS)
        
    def boundingRect(self):
        
        return self._bounds
    
    def mousePressEvent(self, event):
        
        if event.modifiers() == QtCore.Qt.ControlModifier:
            connector = self._branch.free_connector()
            
            if connector not in self.scene().map():
                raise Exception('GUI not connected to kernel properly.')
            
            widget = self.scene().map()[connector]
            
            self.scene().mapto({connector: widget})
            
            self._provisional_connector = widget
            widget.mousePressEvent(event)
            
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        
        if self.scene().current_pipe:
            if self._provisional_connector:
                self._provisional_connector.mouseMoveEvent(event)
            else:
                connector = self._branch.free_connector()
                
                if connector not in self.scene().map():
                    raise Exception('GUI not connected to kernel properly.')
            
                widget = self.scene().map()[connector]
                
                self.scene().mapto({connector: widget})
                
                self._provisional_connector = widget
                
                widget.mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        
        self.ungrabMouse()
        
        if self.scene().current_pipe and self._provisional_connector:
            self._provisional_connector.mouseReleaseEvent(event)
            self._provisional_connector = None
            
            self._branch.connection_removed()
        else:
            self._provisional_connector = None
            
            super().mouseReleaseEvent(event)
    
    def hoverEnterEvent(self, event):
        
        self._close_button.setVisible(True)
    
    def hoverLeaveEvent(self, event):
        
        self._close_button.setVisible(False)
        
        
    def itemChange(self, change, value):
        """Catch item moving or deleted."""
        
        if change == self.ItemSceneChange:
                if value:
                    # connector added to scene <- value is the scene
                    value.mapto({self._branch: self})
                else:
                    # connector removed from scene: scene() is the old one
                    self.scene().unmap(self._branch)
                        
        elif change == self.ItemSelectedChange:
            if value:
                self._brush = self._BRUSH_SELECTED
                
            else:
                self._brush = self._BRUSH
                
        
        return super().itemChange(change, value)
    
    
    def delete(self):
        
    
        try:
            self.scene().removeItem(self)
        except AttributeError:
            pass
    
    def gui_data(self):
        
        return self._gui_data
    
    def node(self):
        
        return self._branch
    
class BranchMark(QtGui.QGraphicsItem):

    def __init__(self, pipe, pipe_widget, pos):
        
        super().__init__()
        
        self._pipe = pipe
        self._pipe_widget = pipe_widget
        
        self.setZValue(10)
        self.setPos(pos)
        
        self._radius = 4
        self._rect = QtCore.QRectF(-self._radius, -self._radius, 2*self._radius, 2*self._radius)
        
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        
    def paint(self, painter, option, widget):
        
        painter.drawEllipse(self._rect)
        
    def boundingRect(self):
        
        return self._rect
    
    def mousePressEvent(self, event):
    
        if event.modifiers() == QtCore.Qt.ControlModifier:
            
            # create branch
            data = {'gui_data': {'pos': (self.scenePos().x(), self.scenePos().y())},
                    'type': 'Branch'}
            branch = self.scene().system().add_node(data)
            
            # check branch widget registration
            if branch not in self.scene().map():
                raise Exception('GUI not connected to kernel properly.')
            
            # rearrange existing pipe
            branchwidget = self.scene().map()[branch]
            input_connector_widget = self._pipe_widget.input_connector_widget()
            
            self._pipe_widget.loosen_connection(self._pipe_widget.input_connector_widget())
            
            self._pipe_widget.snap_to_connector_widget(branchwidget._input_connector)
            self._pipe_widget.register()
            
            # create new pipe to old output
            connector = branch.free_connector()
            widget = GUI.BasicItems.ConnectorWidget(connector, branchwidget)
            widget._style = 'output'
            widget.setFlag(self.ItemStacksBehindParent, True)
            
            
            self.scene().mapto({connector: widget})
            
            self.scene().system()._add_pipe(connector,
                                           input_connector_widget.connector())

            
            branchwidget.grabMouse()
            branchwidget.mousePressEvent(event)
            
            
            
            
    def mouseMoveEvent(self, event):
        
        
        super().mouseMoveEvent(event)
    def setClosestPos(self, pos, pipe_widget):
        
        self._pipe_widget = pipe_widget
        self.setPos(pos)
        
class PipeWidget(QtGui.QGraphicsItem):
    """Connector pipe QGraphicsItem"""
    
    _BEZIER_DISTANCE_SNAPPED = 100
    _BEZIER_DISTANCE_LOOSE = 25
    
    _branchmark = None
    
    _PIPE_DELETED = 'PIPE_DELETED'
    
    _DON_T_CREATE_WIDGET = 'DON_T_CREATE_WIDGET'
    
    def __init__(self, pipe = None, *connectors):
        
        super().__init__()
        
        self._loose_end = None
        self._snapped_to = None
        self._fixed_to = None

        ### graphicsitem
        self.setAcceptHoverEvents(True)
                
        ### painter
        self._inner_pen = QtGui.QPen()
        self._inner_pen.setColor(QtGui.QColor('#808080'))
        self._inner_pen.setWidth(2)
        self._outer_pen = QtGui.QPen()
        self._outer_pen.setColor(QtGui.QColor('#202020'))
        self._outer_pen.setWidth(4)
        self._outer_pen.setCapStyle(QtCore.Qt.FlatCap)
        self.setZValue(-1)
        
        ### geometry
        
        self._out = QtCore.QPointF(0, 0)
        self._pipe = pipe
        
        self._path = QtGui.QPainterPath()
        self._c1 = self._output_bezier_point(50)
        
        ### connections
        if connectors:
            
            self.fix_to(connectors[0])
            self.snap_to_connector_widget(connectors[1])
            self.register()
            
        if self._pipe:
            dispatcher.connect(self.delete, signal=self._PIPE_DELETED, sender= pipe)
        
    
    def _input_bezier_point(self, size):
        
        if self._snapped_to:
            dist = size.manhattanLength()/2
            dist = min(dist, self._BEZIER_DISTANCE_SNAPPED)
            dist = max(dist, 5)
            return size + QtCore.QPointF(dist, 0)
        else:
            return size + QtCore.QPointF(self._BEZIER_DISTANCE_LOOSE, 0)
    
    def _output_bezier_point(self, size):
        
        if self._snapped_to:
            dist = size.manhattanLength()/2
            dist = min(dist, self._BEZIER_DISTANCE_SNAPPED)
            dist = max(dist, 5)
            return QtCore.QPointF(-dist, 0)
        else:
            return QtCore.QPointF(-self._BEZIER_DISTANCE_LOOSE, 0)
        
    def paint(self, painter, option, widget):
        u"""Calculates cubic b�zier curve and paints it."""
        painter.setRenderHint(painter.Antialiasing)
        
        painter.setPen(self._outer_pen)
        painter.drawPath(self._path)
        painter.setPen(self._inner_pen)
        painter.drawPath(self._path)
        
    def boundingRect(self):
        
        return self._path.controlPointRect().adjusted(-10, -10, 20, 20)
        
    
    def _resize(self, c1, c2):
        
        self.prepareGeometryChange()
        size = self._out - self.pos()
        
        self._path = QtGui.QPainterPath()
        self._path.cubicTo(c1(size), c2(size), size)
        
        self.update()
        
        
    def fix_to(self, connector_widget):
        
        if connector_widget.style() == 'input':
            self.setPos(connector_widget.scenePos())
            
            self._loose_end = 'output'
        elif connector_widget.style() == 'output':
            self._out = connector_widget.scenePos()
            self._loose_end = 'input'
        else:
            raise Exception('Unknown connector style.')
        
        self._fixed_to = connector_widget
        
        
    def snap_to_connector_widget(self, connector_widget):
        
        
        if connector_widget.style() == 'input':
            self.setPos(connector_widget.scenePos())
            
        elif connector_widget.style() == 'output':
            
            self._out = connector_widget.scenePos()
            
        else:
            raise Exception('Unknown connector style.')
    
        c1 = self._output_bezier_point
        c2 = self._input_bezier_point

        if self._loose_end:
            self._snapped_to = connector_widget
        
        self._resize(c1, c2)
    
        return True
    
    def loose_end(self):
        
        return self._loose_end
        
    def move_to(self, pos):
        if self._loose_end == 'input':
            c1 = c2 = self._input_bezier_point
            self.setPos(pos)
        elif self._loose_end == 'output':
            c1 = c2 = self._output_bezier_point
            self._out = pos
        else:
            return
        
        self._snapped_to = None
        
        self._resize(c1, c2)
        
    def loosen_connection(self, connector_widget):
        
        self.unregister(connector_widget)
        
        if self._fixed_to == connector_widget:
            # swap it
            self._fixed_to, self._snapped_to = self._snapped_to, self._fixed_to
            
        
        self._loose_end = connector_widget.style()
        
    def delete(self):
        
        self.unregister()
            
        try:
            self.scene().removeItem(self)
        except AttributeError:
            pass
        
    def pipe(self):
        
        return self._pipe
    
    def unregister(self, connector_widget= None):
        
        if self._pipe and (not connector_widget or self._snapped_to == connector_widget):

            if isinstance(self._snapped_to, GUI.BasicItems.ConnectorWidget):
                self._snapped_to.unregister(self)
                self._pipe.remove_connectors(self._snapped_to.connector())
                
        if self._pipe and (not connector_widget or self._fixed_to == connector_widget):
            
            if isinstance(self._fixed_to, GUI.BasicItems.ConnectorWidget):
                self._fixed_to.unregister(self)
                self._pipe.remove_connectors(self._fixed_to.connector())
            
    def register(self):
        
        if self._snapped_to and self._fixed_to:
            
            self._snapped_to.register(self)
            self._fixed_to.register(self)
            
            if not self._pipe:
                 
                self._pipe = self.scene().system()._add_pipe(self._snapped_to.connector(), self._fixed_to.connector(), flags= self._DON_T_CREATE_WIDGET)
                dispatcher.connect(self.delete, signal=self._PIPE_DELETED, sender= self._pipe)
            else:
                if isinstance(self._snapped_to, (GUI.BasicItems.ConnectorWidget, GUI.NodeWidgets.NodeConnectorWidget)):
                    self._pipe.add_connector(self._snapped_to.connector())
                    
                if isinstance(self._fixed_to, (GUI.BasicItems.ConnectorWidget, GUI.NodeWidgets.NodeConnectorWidget)):
                    self._pipe.add_connector(self._fixed_to.connector())
                    
            self._loose_end = None
        else:
            if self.scene():
                self.scene().removeItem(self)
            
            if self._pipe:
                self._pipe.delete()
       
#             if isinstance(self._snapped_to, (ConnectorWidget, NodeConnectorWidget)):
#                 self._snapped_to.connector().register_pipe(None)
#                 
#             if isinstance(self._fixed_to, (ConnectorWidget, NodeConnectorWidget)):
#                 self._fixed_to.connector().register_pipe(None)
            
    def input_connector_widget(self):
        
        if self._snapped_to.style() == 'input':
            return self._snapped_to
        else:
            return self._fixed_to
        
    def output_connector_widget(self):
        
        if self._snapped_to.style() == 'output':
            return self._snapped_to
        else:
            return self._fixed_to
        
    def _find_closest_point_on_curve(self, pos):
        
        t_upper = 0.05
        t_lower = 1 - t_upper
        
        old_dist = 1000
        
        for _ in itertools.repeat(None, 100):
            
            length = t_upper - t_lower
            t_1 = length / 4     + t_lower
            t_2 = length * 3 / 4 + t_lower
            
            dist_1 = QtGui.QVector2D(pos - self._path.pointAtPercent(t_1))
            dist_2 = QtGui.QVector2D(pos - self._path.pointAtPercent(t_2))
            
            if dist_1.lengthSquared() < dist_2.lengthSquared():
                # t_1 closer
                if abs(dist_1.lengthSquared() - old_dist) < 0.01: 
                    
                    return self._path.pointAtPercent(t_1)
                
                t_upper = length / 2 + t_lower
                
                old_dist = 0.5*old_dist + 0.5*dist_1.lengthSquared()
            else:
                if abs(dist_2.lengthSquared() - old_dist) < 0.01:
                    
                    return self._path.pointAtPercent(t_2)
                t_lower = length / 2 + t_lower
                
                old_dist = 0.5*old_dist + 0.5*dist_1.lengthSquared()
        
        print('fail')
        return self._path.pointAtPercent((t_2 + t_1) / 2)
       
    
    def hoverMoveEvent(self, event):
        
        if event.modifiers() == QtCore.Qt.ControlModifier:
            
            if self.scene().branch_mark:
                
                self.scene().branch_mark.setClosestPos(self.mapToScene(self._find_closest_point_on_curve(event.pos())), self)
                
            else:
                
                self.scene().branch_mark = BranchMark(self._pipe, self, event.scenePos())
                self.scene().addItem(self.scene().branch_mark)
            
            
        super().hoverEnterEvent(event)