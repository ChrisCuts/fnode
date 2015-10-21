# -*- coding: utf-8 -*-
'''
Created on 01.09.2015

@author: derChris
'''

from pydispatch import dispatcher

from PlugIns.NodeTemplates import NodeTemplate, Connector

# SIGNALs
_PIPE_CREATED = 'PIPE_CREATED'
_PIPE_DELETED = 'PIPE_DELETED'
_PIPE_UPDATED = 'PIPE_UPDATED'

class BranchConnector(Connector):

    _CONNECTOR_CREATED = 'CONNECTOR_CREATED'
    _CONNECTOR_DELETED = 'CONNECTOR_DELETED'
    
    def __init__(self, name, style, pipe= None, node= None):
        
        super().__init__(name, style, pipe, node)
        
        self._branch = node
        
        
        dispatcher.send(self._CONNECTOR_CREATED, sender= self, node= node)
        
    def register_pipe(self, pipe):
        
        
        super().register_pipe(pipe)
        
        if not self._pipe:
            self.delete()
            
        self._branch.update_connectors()
        
    def delete(self):
        
        
        self._branch.connection_removed()  
        
        #dispatcher.send(signal= self._CONNECTOR_DELETED, sender= self)
        
class Branch(NodeTemplate):
     
    _BRANCH_CREATED = 'BRANCH_CREATED'
    _BRANCH_DELETED = 'BRANCH_DELETED'
    
    _CONNECTOR_CREATED = 'CONNECTOR_CREATED'
    _CONNECTOR_DELETED = 'CONNECTOR_DELETED'
    
    def __init__(self, system, pipe= None, data = None):
        
        super().__init__(system, data)
        
        
        #dispatcher.send(signal= self._NODE_CREATED, sender= self)
        
    def create_sequence_item(self, nodes, pipemap):
        
        ### pass on pipe_ids
        pipe_id = id(self._inputs[0].pipe())
        
        for connector in self._outputs.values():
            
            pipemap.update({id(connector.pipe()): (pipemap[pipe_id][0], connector.pipe().connector_at_output())})
        
        # remove input pipe
        if self.input_connectors()[0] != pipemap[pipe_id][1]:
            raise Exception('Pipe missregister!')
        
        del(pipemap[pipe_id])
        
        return None, pipemap
        
    def connector(self, field, name):
        
        if '_' + field in self.__dict__ and isinstance(self.__dict__['_' + field], dict):
            
            if name in self.__dict__['_' + field]:
                
                return self.__dict__['_' + field][name]
            
            elif field == 'outputs':
                
                return self.free_connector()
            
            elif field == 'inputs' and name == 0:
                
                return self.free_connector('input')
            else:
                
                raise KeyError(str(name) + ' is not in ' + field)
            
        else:
            raise KeyError(field + ' is not a valid field name.')
        
    def free_connector(self, style= 'output'):
        
        outputs = {}
        number = 0
        for output in self._outputs.values():
            outputs.update({number: output})
            
            number += 1
            
        self._outputs = outputs
        
        connector = BranchConnector(number, style, node= self)
        
        if style == 'output':
            self._outputs.update({number: connector})
        elif style == 'input':
            self._inputs = {0:  connector}
            
        return connector
    
    def update_connectors(self):
        
        outputs = {}
        number = 0
        for output in self._outputs.values():
            
            if output.pipe():
                outputs.update({number: output})
            
                number += 1
            
        self._outputs = outputs
        
    def connection_removed(self):
        
        self.update_connectors()
        
        if self._inputs and not self._inputs[0].pipe():
            
            self.delete()
            
        if len(self._outputs) == 1:
            
            connectors = [self._outputs[0].pipe().connector_at_output(),
                          self._inputs[0].pipe().connector_at_input()]
            
            
            self.delete()
            
            self._system._add_pipe(*connectors)
            
    def name(self):
        
        return 'branch'
    
    
class Pipe():
    
    def __init__(self, *connectors, system= None, flags= None):
        
        self._output = None
        self._input = None
        
        self._system = system
        
        for connector in connectors:
            if connector.style() == 'input':
                self._output = connector
                connector.register_pipe(self)
            elif connector.style() == 'output':
                self._input = connector
                connector.register_pipe(self)
            
        dispatcher.send(signal = _PIPE_CREATED, sender= self, flags= flags)
        
    def has_output(self):
        
        if self._output:
            return True
        else:
            return False
    
    def connector_at_output(self):
        
        return self._output
    
    def node_at_output(self):
        
        return self._output.node()
    
    def has_input(self):
        
        if self._input:
            return True
        else:
            return False
    
    def connector_at_input(self):
        
        return self._input
        
    def node_at_input(self):
        
        return self._input.node()
    
    def is_connected(self):
        
        return self._input and self._output
    
    def add_connector(self, *connector_to_add):
        
        
        for connector in connector_to_add:
            if connector.style() == 'input':
                if self._output and self._output != connector:
                    self._output.register_pipe(None)
                self._output = connector
                
            elif connector.style() == 'output':
                if self._input and self._input != connector:
                    self._input.register_pipe(None)
                self.input = connector
                
            
            connector.register_pipe(self)
        
        
        
    def remove_connectors(self, *connectors):
        
        for connector in connectors:
            
            if connector.style() == 'input':
                if self._output:
                    self._output.register_pipe(None)
                self._output = None
                
            elif connector.style() == 'output':
                if self._input:
                    self._input.register_pipe(None)
                self._input = None
        
            connector.register_pipe(None)
            
        
    def delete(self):
        
        
        if self._output:
            self._output.register_pipe(None)
        if self._input:
            self._input.register_pipe(None)
            
        if self._system:
            self._system._remove_pipe(self)
        
        dispatcher.send(signal = _PIPE_DELETED, sender= self)
    
        
    def gui_data(self):
        
        return self._gui_data
        
    def get_data(self):
        
        data = {'connectors': []}
        
        if self._input:
            data['connectors'].append({'node': id(self._input.node()),
                                       'name': self._input.name(),
                                       'field': self._input.field()})
        
        if self._output:
        
            data['connectors'].append({'node': id(self._output.node()),
                                       'name': self._output.name(),
                                       'field': self._output.field()})
        
        
        return data
        
        
        
        
        
        