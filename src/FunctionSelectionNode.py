# -*- coding: utf-8 -*-
'''
Created on 17.09.2015

@author: derChris
'''

from pydispatch import dispatcher

import PlugIns.NodeTemplates
import PlugIns.MATLAB.MATLAB
import Pipe

class FunctionSelectionNode(PlugIns.NodeTemplates.NodeTemplate):
    
    _UPDATE_FUNCTION_SELECTION_WIDGET = 'UPDATE_FUNCTION_SELECTION_WIDGET'
    
    _DON_T_CREATE_WIDGET = 'DON_T_CREATE_WIDGET'
    
    def __init__(self, system, data= None):
        
        
        super().__init__(system, data)
        
        self._function_nodes = []
        
        self._name = 'Function Selection'
        
        if data and 'nodes' in data:
            for function_data in data['nodes']:
                self._function_nodes.append(PlugIns.MATLAB.MATLAB.mFunctionNode(function_data['name'], system, function_data))
        
        for function_node in self._function_nodes:
            
            for input_connection in function_node.inputs().items():
                
                if input_connection[0] not in self._inputs:
                    
                    self._inputs.update({input_connection[0]: input_connection[1].copy(self)})
            
            for output_connection in function_node.outputs().items():
                if output_connection[0] not in self._outputs:
                    self._outputs.update({output_connection[0]: output_connection[1].copy(self)})
        
        
    def get_function_nodes(self):
        
        return self._function_nodes
    
    
    def remove_function_node(self, node):
        
        self._function_nodes.remove(node)
        
        inputs = {}
        outputs = {}
        for function_node in self._function_nodes:
            inputs.update(function_node.inputs())
            outputs.update(function_node.outputs())
        
        for input_connection in self._inputs:
            
            if input_connection not in inputs:
                self._inputs[input_connection].clear()
                self._inputs.pop(input_connection)
                
        for output_connection in self._outputs:
            
            if output_connection not in outputs:
                self._outputs[output_connection].clear()
                self._outputs.pop(output_connection)
        
        
        dispatcher.send(self._UPDATE_FUNCTION_SELECTION_WIDGET, sender= self)
        
        
    def add_function(self, data):
    
        name = data['name']
        
        self._function_nodes.append(PlugIns.MATLAB.MATLAB.mFunctionNode(name, self._system, data))
        
        for function_node in self._function_nodes:
            
            for input_connection in function_node.inputs().items():
                if input_connection[0] not in self._inputs:
                    self._inputs.update({input_connection[0]: input_connection[1].copy(self)})
            
            for output_connection in function_node.outputs().items():
                if output_connection[0] not in self._outputs:
                    self._outputs.update({output_connection[0]: output_connection[1].copy(self)})
                    
        dispatcher.send(self._UPDATE_FUNCTION_SELECTION_WIDGET, sender= self)
        
        
    def create_sequence_item(self, nodes, pipemap):
        
        ### connect input pipes to first node with same input
        for tag, connector in self._inputs.items():
            
            if connector.pipe() and id(connector.pipe()) in pipemap:
                for function_node in self._function_nodes:
                    if tag in function_node.inputs():
                        
                        virtual_connector = PlugIns.NodeTemplates.Connector(tag,
                                                                    style= 'output')
                        
                        pipe = Pipe.Pipe(function_node.inputs()[tag], virtual_connector,
                                         flags= self._DON_T_CREATE_WIDGET)
                        variable_id = pipemap[id(connector.pipe())][0]
                        
                        pipemap.update({id(pipe) : (variable_id, function_node.inputs()[tag])})
                        
                        del(pipemap[id(connector.pipe())])
                            
                        break
        
        
        virtual_connectors = []
        ### connect output pipes to last node with same output
        for tag, connector in self._outputs.items():
            
            if connector.pipe():
                for function_node in reversed(self._function_nodes):
                    if tag in function_node.outputs():
                         
                        virtual_connector = PlugIns.NodeTemplates.Connector(tag,
                                                                    style= 'input')
                         
                        pipe = Pipe.Pipe(function_node.outputs()[tag], virtual_connector,
                                         flags= self._DON_T_CREATE_WIDGET)
                        
                        virtual_connectors.append(virtual_connector)
                        break
                
        ### create pipes
        subsequence = []
        pipes = set()
            
        for num, function_node in enumerate(self._function_nodes):
            
            #connect node with next except it's the last one
            if num < len(self._function_nodes)-1:
                for tag, connector in function_node.outputs().items():
                    if tag in self._function_nodes[num+1].inputs():
                        
                        pipes.add(Pipe.Pipe(connector, self._function_nodes[num+1].inputs()[tag],
                                            flags= self._DON_T_CREATE_WIDGET))
            
            
            
            sequenceitem, pipemap = function_node.sequence_data(nodes, pipemap)
            
            subsequence.append(sequenceitem)
            
            
        for pipe in pipes:
            pipe.delete()
        
        
        ### connect virtual output connectors with output connectors
        for virtual_connector in virtual_connectors:
            
            pipe = self._outputs[virtual_connector.name()].pipe()
            
            variable_id = pipemap[id(virtual_connector.pipe())][0]
            
            pipemap.update({id(pipe): (variable_id, pipe.connector_at_output())}) 
            
            # delete pipe
            del(pipemap[id(virtual_connector.pipe())])
            virtual_connector.clear()
        
        
        
        return subsequence, pipemap
        
    def get_data(self):
        
        data = super().get_data()
        
        data.update({'nodes': [function_node.get_data() for function_node in self._function_nodes]})
        
        return data
    
        