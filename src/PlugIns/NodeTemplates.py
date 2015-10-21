# -*- coding: utf-8 -*-
'''
Created on 28.08.2015

@author: derChris
'''

import re
from collections import OrderedDict
from pydispatch import dispatcher
from abc import abstractmethod
from ezClasses.ezClasses import ezDict

####################
### SHARED GUI INFO
####################

class SharedGUIData():
    
    _DEFAULT_X = 0
    _DEFAULT_Y = 0
    
    
    _DEFAULT_HEIGHT = 300
    _DEFAULT_WIDTH = 220
    
    def __init__(self, data = None):
        
        if data and 'pos' in data:
            self._pos = data['pos']
        else:
            self._pos = (self._DEFAULT_X, self._DEFAULT_Y)
        if data and 'size' in data:
            self._size = data['size']
        else:
            self._size = (self._DEFAULT_WIDTH, self._DEFAULT_HEIGHT)        
        
    def pos(self):
        
        return self._pos
    
    def size(self):
        
        return self._size
    
    def set_pos(self, pos):
        
        self._pos = pos
    
    def set_size(self, size):
        
        self._size = size
        
    def get_data(self):
        """
        Get information to save object
        
        """
        
        data = {}
        
        if self._pos != (self._DEFAULT_X, self._DEFAULT_Y):
            data.update({'pos': self._pos})
        if self._size != (self._DEFAULT_WIDTH, self._DEFAULT_HEIGHT):
            data.update({'size': self._size})
            
        return data   
        
        
####################
### CONNECTOR
####################

class Connector():
    
    def __init__(self, name, style, pipe = None, node= None):
        
        
        self._name = name
        self._style = style
        
        self._pipe = pipe
        self._node = node
        
        if style == 'input':
            self._field = 'inputs'
        elif style == 'output':
            self._field = 'outputs'
        else:
            raise Exception('Invalid style: "' + style + '"')
        
           
    def register_pipe(self, pipe):
        
        self._pipe = pipe
        
    def pipe(self):
        
        return self._pipe
    
    def clear(self):
         
        if self._pipe:
             
            self._pipe.delete()
            self._pipe = None
        
    def get_data(self):
        
        if self._pipe:
            return {self._name: id(self._pipe)}
        else:
            return {}
        
    def sequence_data(self, pipemap):
        
        if self._pipe:
            if id(self._pipe) in pipemap:
                # get variable
                variable_id = pipemap[id(self._pipe)][0]
                # delete pipe from map
                if pipemap[id(self._pipe)][1] != self:
                    raise Exception('Pipe missregister!')
                
                del(pipemap[id(self._pipe)])
                
                #TODO: don t send name
                return {self._name: variable_id}, pipemap 
            
            elif self.style() == 'output':
                pipemap.update({id(self._pipe): (RunSequenceAdditions._get_new_variable_id(pipemap), self._pipe.connector_at_output())})
                
                return {self._name: pipemap[id(self._pipe)][0]}, pipemap
            else:
                raise Exception('Pipe unresolved: ' + self._name + ' ' + self._node.name() + ' (' + str(id(self._node)) + ')')
        else:
            return {self._name: None}, pipemap
            
    def name(self):
        
        return self._name
    
    def style(self):
        
        return self._style
    
    def node(self):
        
        return self._node
    
    def field(self):
        
        return self._field
    
    
    def copy(self, node):
        
        return Connector(self._name, self._style, None, node)
    
class ValueConnector(Connector):
    
    _VALUE_UPDATED = 'VALUE_CONNECTOR_VALUE_UPDATED'
    _PIPE_CONNECTION_STATUS = 'PIPE_CONNECTION_STATUS'
    
    _FLOAT_RE  = re.compile('\ *[+-]?[0-9]+(\.[0-9]+)?([eE][+-][0-9]+)?\ *')
    _INT_RE    = re.compile('\ *[+-]?[0-9]+\ *')

    def __init__(self, name, style, default_value, pipe = None, node= None):
        
        super(ValueConnector, self).__init__(name, style, pipe, node)
        
        self._value = default_value
        self._field = 'options'
        
    def set_value(self, value):
        
        self._value = value
        
        dispatcher.send(signal = self._VALUE_UPDATED, sender= self, tag= self._name, value= value)
    
    def value(self):
        
        return self._value
    
    def get_data(self):
        
        data = {self._name: {'value': self._value}}
        
        if self._pipe:
            data[self._name].update({'pipe': id(self._pipe)})
            
        return data
    
    def register_pipe(self, pipe):
        
        super().register_pipe(pipe)
        
        dispatcher.send(self._PIPE_CONNECTION_STATUS, self, True if pipe else False)
        
    def sequence_data(self, pipemap):
        
        if self._pipe:
            return super().sequence_data(pipemap)
        else:
            if re.match(self._INT_RE, self._value):
                return {self._name: ('int', int(self._value))}, pipemap
            
            if re.match(self._FLOAT_RE, self._value):
                return {self._name: ('float', float(self._value))}, pipemap
            
            return {self._name: ('string', self._value)}, pipemap
        
class DataConnector(Connector):
    
    _ITERATOR_UPDATED = 'ITERATOR_UPDATED'
    
    def __init__(self, info, pipe = None, node= None):
        
        super().__init__(info[0], 'output', pipe, node)
        
        self._array_size = info[1]
        self._type = info[2]
        
        self._iterate_via = None # Dimension
        
        self._subconnectors = None
        
    def display(self):
        if self._iterate_via == None:
            return None, None
        else:
            return self._iterate_via, self._array_size[self._iterate_via-1]
    
    def increase_iteration_dimension(self):
        
        if self._iterate_via == len(self._array_size):
            self._iterate_via = None
        elif not self._iterate_via:
            self._iterate_via = 1
            
            if self._type == 'struct':
                
                self._create_subconnectors()
        else:
            self._iterate_via += 1
        
        dispatcher.send(signal = self._ITERATOR_UPDATED, sender= self)
    
        
####################
### NODE TEMPLATE
####################

class NodeTemplate():
    
    _NODE_CREATED = 'NODE_CREATED'
    _NODE_DELETED = 'NODE_DELETED'
    
    
    def __init__(self, system, data = None):
        
        if data and 'gui_data' in data:
            self._gui_data = SharedGUIData(data['gui_data'])
        else:
            self._gui_data = SharedGUIData()
        
        self._name = ''
        self._system = system
        
        self._inputs = OrderedDict()
        self._outputs = OrderedDict()
        
    def __getitem__(self, field):

        if '_' + field in self.__dict__ and isinstance(self.__dict__['_' + field], OrderedDict):
            return self.__dict__['_' + field]
        else:
            raise KeyError(field + ' is not a valid field name.')
        
    def connector(self, field, name):
        
        if '_' + field in self.__dict__ and isinstance(self.__dict__['_' + field], OrderedDict):
            
            if name in self.__dict__['_' + field]:
                
                return self.__dict__['_' + field][name]
            
            else:
                raise KeyError(name + ' is not in ' + field)
            
        else:
            raise KeyError(field + ' is not a valid field name.')
        
        
    ### get info
    def inputs(self):
        
        return self._inputs
        
    def input_connectors(self):
        
        return tuple(self._inputs.values())
    
    def output_connectors(self):
        
        return tuple(self._outputs.values())
    
    def outputs(self):
        
        return self._outputs
    
    def connectors(self):
        
        inputs = list(self._inputs.values())
        outputs = list(self._outputs.values())
        
        return inputs + outputs
    
    def following_nodes(self):
        
        nodes = set()
        
        for connector in self.output_connectors():
            if connector.pipe():
                nodes.add(connector.pipe().node_at_output())
    
        
        return nodes
    
    def preceding_nodes(self):
        
        nodes = set()
        
        for connector in self.input_connectors():
            nodes.add(connector.pipe().node_at_input())

        return nodes
    
    def gui_data(self):
        
        return self._gui_data
    
    def get_data(self):
        
        data = ezDict()
                
        for connector in self.input_connectors():
                data['fields']['inputs'].update(connector.get_data())
        
        for connector in self.output_connectors():
                data['fields']['outputs'].update(connector.get_data())
            
            
        data.update({'id'  : id(self),
                'name': self.name(),
                'type': self.__class__.__name__,
                'gui_data': self._gui_data.get_data()})
                        
        return data.reduce() # remove 'empty' subdicts
    
    @abstractmethod
    def sequence_data(self, branchs, pipemap):
         
        pass
    
    def has_inputs(self):
        
        for connector in self.input_connectors():
            if connector.pipe():
                return True
            
        return False
    
    def unresolved_input_pipes(self, pipe_map):
        
        pipes = set()
        
        for connector in self.connectors():
            
            if connector.style() == 'input' and connector.pipe():
                if id(connector.pipe()) not in pipe_map:
                    pipes.add(connector.pipe())
            
        return pipes
    
    
    def name(self):
        
        return self._name
    
    ### manipulate
    def delete(self):
        
        self._system._remove_node(self)
        
        for connector in self.connectors():
            connector.clear()
            
        
        dispatcher.send(signal = self._NODE_DELETED, sender = self)
    
    def remove_node(self):
        
        self._system.remove_node(self)
        
        for connector in self.connectors():
            connector.clear()
            
        dispatcher.send(signal = self._NODE_DELETED, sender = self)
    
    
    @abstractmethod
    def create_sequence_item(self, nodes, pipe_map):
        
        pass
    
    @classmethod
    def run_sequence_addition(cls):
        
        return None
    
    
############################
### FUNCTION NODE TEMPLATE
############################
class FunctionNodeTemplate(NodeTemplate):
    
    _FUNCTION_NODE_OPTIONS_VALUE_UPDATED = 'FUNCTION_NODE_OPTIONS_VALUE_UPDATED'
    
    def __init__(self, name, system, data = None):
        
        if data and 'path' in data:
            
            self._folder = system.file_manager().root_folder().find_folder(data['path'])
            
        elif data and 'folder_item' in data:
            
            self._folder = data['folder_item']
        else:
            raise Exception('No path or folder given')
            
        super(FunctionNodeTemplate, self).__init__(system, data)
        
        self._name = name
        self._options = OrderedDict()
        self._properties = dict()
        
        try:
            self._read_from_file()
        except FileNotFoundError:
            self._name = '<' + self._name + '>'
            
        
        if data and 'fields' in data and 'options' in data['fields']:
             
            for tag, info in data['fields']['options'].items():
                 
                if tag in self._options and 'value' in info:
                    
                    self._options[tag].set_value(info['value'])
                    
    ### protected
    @abstractmethod    
    def _read_from_file(self):
        pass
    
    ### public
    ### get info
    def get_data(self):
        
        data = super(FunctionNodeTemplate, self).get_data()
        
        for connector in self._options.values():
            data['fields']['options'].update(connector.get_data())
            
        data.update({'path': self._folder.relative_path()})
        
        return data.reduce()
    
    def sequence_data(self, branchs, pipemap):
        
        data = ezDict()
        
        for connector in self.input_connectors():
            connector_data, pipemap = connector.sequence_data(pipemap)
            data['fields']['inputs'].update(connector_data)
        
        for connector in self._options.values():
            connector_data, pipemap = connector.sequence_data(pipemap)
            data['fields']['options'].update(connector_data)
         
        ### replace output pipe IDs with variable id
        for connector in self.output_connectors():
            connector_data, pipemap = connector.sequence_data(pipemap)
            data['fields']['outputs'].update(connector_data)
             
             
        data.update({'name': self.name(),
                'path': self.path(),
                'type': self.__class__.__name__})
         
        return (self._PLUGIN, self._OPCODE, data), pipemap
    
    
    def has_inputs(self):
        
        if super().has_inputs():
            return True
        
        for connector in self._options.values():
            if connector.pipe():
                return True
            
        return False
    
    @classmethod
    @abstractmethod
    def file_extension(cls):
        pass
    
    
    def path(self):
        
        if self._folder:
            return self._folder.path()
        else:
            return None
    
    def options(self):
        
        return self._options
        
    def option_connectors(self):
        
        return tuple(self._options.values())
    def update_options_value(self, tag, value):
        
        for connector in self.connectors():
            if connector.name() == tag:
                
                connector.set_value(value)
                
    def is_connected(self, pipe_id):
        
        for connector in self.input_connectors():
            if connector.pipe() and id(connector.pipe()) == pipe_id:
                return True
        
        return False
    
    ### manipulate object
    def register_pipe(self, style, connector, pipe):
        
        super(FunctionNodeTemplate, self).register_pipe(style, connector, pipe)
            
        if style == 'options':
            self._options[connector].register_pipe(pipe)
            
        
        
        
#     def update_options_value(self, tag, value):
#         
#         self._options.update({tag: value})
#         
#         dispatcher.send(signal = self._FUNCTION_NODE_OPTIONS_VALUE_UPDATED, sender= self, tag= tag, value= value)
        
    def remove_pipe(self, deleted_pipe):
        
        ### whole cleanup
        super(FunctionNodeTemplate, self).remove_pipe(deleted_pipe)
        self._options = {slot: pipe for slot, pipe in self._options.items() if pipe != deleted_pipe}
        
    def connectors(self):
        
        options = list(self._options.values())
        
        return super().connectors() + options
      
    
class RunSequenceAdditions():
    
    @classmethod
    def _get_new_variable_id(cls, pipe_map):
        # determine new variable_id (the lowest unused)
        variable_id = 1
        used_variable_ids = [value[0] for value in pipe_map.values()]
        for variable_id in used_variable_ids:
            variable_id += 1
        
        return variable_id
    
    
    def sequence_init_procedure(self, nodes):
        
        pass
    
    def sequence_pre_append_procedure(self, node):
        
        pass
    
    def sequence_post_append(self, node):
        
        pass
    
    def priority_node(self, nodes):
    
        return None
    
    def sequence_post_creation(self, sequence):
        
        return sequence
    
    def create_sequence_item(self, node, branchs, pipe_map):
        
        
        code, pipe_map = node.sequence_data(branchs, pipe_map)
        
        
        return code, pipe_map
    
    
    
if __name__ == '__main__':
    
    def func(name, **kwargs):
        print(name)
        print(kwargs)
        
    