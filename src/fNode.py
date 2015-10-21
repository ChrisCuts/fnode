# -*- coding: utf-8 -*-
'''
Created on 13.08.2015

@author: derChris
'''

### extern
from pydispatch import dispatcher
import logging

### project intern
import GUI.MainWindow
import GUI.LogWidget

from PySide import QtGui, QtCore
import Pipe
import FunctionSelectionNode

from PlugIns.PlugInManager import PlugInManager
from RunSequence import RunSequence


from FileFunctions import FileManager

import SaveLoad

### SIGNALS

_UNDO_STATUS = 'UNDO_STATUS'
_REDO_STATUS = 'REDO_STATUS'
_SAVED_STATUS = 'SAVED_STATUS'

_SYSTEM_CLEARED = 'SYSTEM_CLEARED'

_FILE_LOADED = 'FILE_LOADED'

_SAVE_BEFORE_QUIT = 'SAVE_BEFORE_QUIT?' 
   
### CONSTs
_UNDOBUFFER_SIZE = 50


###################
### FunctionSystem
###################
class FunctionSystem():
    
    _logger = logging.getLogger('System')
    
    def __init__(self):
        
        self._logger = GUI.LogWidget.LogWidget()
    
        self._nodes = []
        self._pipes = []
        self._clipboard = []
        
        self._filename = ''
        self._saved = False
        
        self._plugin_manager = PlugInManager()
        self._file_manager = FileManager(self._plugin_manager)
        
        self._gui = GUI.MainWindow.GUI(self)
        
        self._undobuffer = []
        self._redobuffer = []
        
    def _build(self, data):
        """Create FunctionNodes out of given data"""
        if isinstance(data, dict):
            
            pipe_info = {}
            if 'nodes' in data:
                ### build function nodes
                for node_data in data['nodes']:
                
                    func_node = self._add_node(node_data.copy())
                    pipe_info.update({node_data['id']: func_node})
            
             
            if 'pipes' in data:
                
                for pipe_data in data['pipes']:
                    
                    connectors = []
                    for connector_info in pipe_data['connectors']:
                        try:
                            connectors.append(pipe_info[connector_info['node']]
                                              .connector(connector_info['field'],
                                                         connector_info['name']))
                        except KeyError:
                            self._logger.warning('Pipe not created')
                        
                    if len(connectors) == 2:
                        self._add_pipe(*connectors)
    
    def _add_pipe(self, *connectors, flags= None):
        
        pipe = Pipe.Pipe(*connectors, system= self, flags= flags)
        self._pipes.append(pipe)
    
        return pipe
    
    def add_pipe(self, *connectors, flags= None):
        
        self._undo_save_state()
        
        return self._add_pipe(*connectors, flags= flags)
      
    
    def _add_node(self, data):
        
        if 'type' in data and data['type'] == 'Branch':
            node = Pipe.Branch(self, data= data)
        elif 'type' in data and data['type'] == 'FunctionSelectionNode':
            node = FunctionSelectionNode.FunctionSelectionNode(self, data)
        else:
            node = self._plugin_manager.create_node(data, system= self)
        
        self._nodes.append(node)
        
        dispatcher.send(signal= node._NODE_CREATED, sender= node)
    
                
        return node
            
    def add_node(self, data):
        
        self._undo_save_state()
        
        return self._add_node(data)
    
    def get_data(self):
        
        data = {'nodes': [],
                'pipes': [],
                'currentworkpath': self._file_manager.current_workpath()}
        
        for func in self._nodes:
            data['nodes'].append(func.get_data())
        for pipe in self._pipes:
            data['pipes'].append(pipe.get_data())
        
        
        return data

    def save(self):
        print('save to: ', self.file_manager().current_workpath() + '\save.json')
        #TODO: save functions in file
        SaveLoad.save(self.file_manager().current_workpath() + '\save.json', self.get_data())
        
        self._saved = True
        dispatcher.send(_SAVED_STATUS, sender= self, status= True)
        
    def load(self, filename):
        print('load from: ', filename)
        data = SaveLoad.load(filename)
        try:
            self._build(data)

            self._filename = filename
            self._saved = True
            
            dispatcher.send(_FILE_LOADED, sender= self)
            
            dispatcher.send(_UNDO_STATUS, sender= self, status= False)
            dispatcher.send(_REDO_STATUS, sender= self, status= False)
            dispatcher.send(_SAVED_STATUS, sender= self, status= True)
            
            self._undobuffer = []
            self._redobuffer = []
        except:
            import traceback
            traceback.print_exc()
            
        
    def _clear(self):
       
        self._nodes = []
        self._pipes = []
        
        dispatcher.send(signal= _SYSTEM_CLEARED, sender= self)
        
    def clear(self):
        
        self._undo_save_state()
        self._clear()
             
    def _remove_node(self, node):
        
        try:
            self._nodes.remove(node)
        except ValueError:
            print('node not in list')
        
    def remove_node(self, node):
        
        self._undo_save_state()
        
        self._remove_node(node)
        
    def _remove_pipe(self, pipe):
        
        self._pipes.remove(pipe)
        
    def remove_pipe(self, pipe):
        
        self._undo_save_state()
        
        self._remove_pipe(pipe)
           
    def undo(self):
        print('undo', self._undobuffer)
        if self._undobuffer:
            status = self._undobuffer.pop()
            
            dispatcher.send(_REDO_STATUS, sender= self, status= True)
            self._redobuffer.append(self.get_data())
            
            self._clear()
            self._build(status)
            
            if not self._undobuffer:
                dispatcher.send(_UNDO_STATUS, sender= self, status= False)
                
    
    def redo(self):
        print('redo')
        if self._redobuffer:
            status = self._redobuffer.pop()
            
            self._undobuffer.append(self.get_data())
            
            self._clear()
            self._build(status)
            dispatcher.send(_UNDO_STATUS, sender= self, status= True)
            
            if not self._redobuffer:
                dispatcher.send(_REDO_STATUS, sender= self, status= False)
            
    def _undo_save_state(self):
        print('undo save state')
        #TODO: save action name and merge
        self._undobuffer.append(self.get_data())
        self._redobuffer.clear()
        
        self._saved = False
        
        dispatcher.send(_UNDO_STATUS, sender= self, status= True)
        dispatcher.send(_REDO_STATUS, sender= self, status= False)
        dispatcher.send(_SAVED_STATUS, sender= self, status= False)
        
        
        if len(self._undobuffer) > _UNDOBUFFER_SIZE:
            self._undobuffer = self._undobuffer[-_UNDOBUFFER_SIZE:]    
        
    def undo_save_state(self):
        
        self._undo_save_state()
        
    def cut(self, nodes):
        
        self._undo_save_state()
        
        self.copy(nodes)
                            
        for node in nodes:
            node.delete()
        
    def copy(self, nodes):
        print('copy')
        self._clipboard.clear()
        
        self._clipboard = {'nodes': [],
                           'pipes': [],
                           'currentworkpath': self._file_manager.current_workpath()}
        
        # nodes
        for node in nodes:
            self._clipboard['nodes'].append(node.get_data())
        
        # pipes
        for node in nodes:
            for connector in node.output_connectors():
                
                if connector.pipe():
                    for node2 in nodes:
                        if node2 != node and connector.pipe() in [connector.pipe() for connector in node2.connectors()]:
                            self._clipboard['pipes'].append(connector.pipe().get_data())
            
        
    def paste(self):
        
        self._build(self._clipboard)
    
    def show(self):
        
        self._gui.start()
        
    def quit(self):
        
        if not self._saved:
            dispatcher.send(_SAVE_BEFORE_QUIT, sender= self)
        
        self._gui.quit()
        self._logger.close()
        
        self._plugin_manager.quit()
        
    def run(self):
        
        RunSequence(self._nodes.copy(), self._plugin_manager)

    def file_manager(self):
        
        return self._file_manager
    
    def plugin_manager(self):

        return self._plugin_manager
    
    def change_current_workpath(self, path):
        
        print(path)
        
    def filename(self):
        
        return self._filename
    
    def saved(self):
        
        return self._saved
    
    
def start():
    
    import sys
    
    QtCore.QCoreApplication.addLibraryPath(r'C:\Users\derChris\Anaconda\envs\p34\Lib\site-packages\PySide\plugins')
    app = QtGui.QApplication(sys.argv)
    
    _expthook = sys.excepthook
    def exception_hook(exctype, value, traceback):
        
        _expthook(exctype, value, traceback)
        sys.exit(1)
        
    sys.excepthook = exception_hook
    
    system = FunctionSystem()
    
    
    system.load(system.file_manager().current_workpath() + '\save.json')    
    
#     data= {'type': 'FunctionSelectionNode'}
#     system.add_node(data)
    system.show()
    
    sys.exit(app.exec_())
    
    return ''
    
    
if __name__ == '__main__':
    
    start()
    
    
    
    
    
    
    
    
    