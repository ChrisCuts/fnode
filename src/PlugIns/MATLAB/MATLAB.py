# -*- coding: utf-8 -*-
'''
Created on 10.08.2015

@author: derChris
'''

import PlugIns.PlugInTemplate
import PlugIns.NodeTemplates

# extern
import re
#import matlab.engine
import threading
import scipy.io 


import subprocess


### REs
_M_VAR             = r' *[A-Za-z][A-Za-z0-9_]* *'
_M_ARRAY           = r' *\[' + _M_VAR + '( *,' + _M_VAR + ')* *,? *\]'
_M_VAR_OR_ARRAY    = r' *(' + _M_VAR + r'|' + _M_ARRAY + r') *'
_M_FILE_HEADER_RE  = re.compile(r'^function  *'
                              + r'(' + _M_VAR_OR_ARRAY + r'=)? *'                   # Left Side 
                              + _M_VAR                                              # Function Title
                              + r'(\(' + _M_VAR + r'( *,' + _M_VAR + r')* *\))? *') # Arguments
_M_LEFT_SIDE       = re.compile(r'(?<=function)' + _M_VAR_OR_ARRAY + r'(?=\=)')
_M_RIGHT_SIDE      = re.compile(r'(?<=\()' + _M_VAR + r'( *,' + _M_VAR + r')*(?= *\))')
_FIELD_NAME_RE     = re.compile(r'^[A-Z][A-Z0-9_]*$')

_OPTION_RE         = re.compile(r'^[A-Za-z]\w*\s*:\s*.*$')
_OPTION_NAME_RE    = re.compile(r'^[A-Za-z]\w*(?=\s*:)')
_OPTION_DEFAULT_RE = re.compile(r'(?<=:).*$')

################
### OVERLOAD
################

class matFileNode(PlugIns.NodeTemplates.NodeTemplate):
    
    def __init__(self, name, system, data = None):
        
        super().__init__(system, data)
        
        self._name = name
        
        
        if data and 'file' in data:
            self._file = data['file']
            
        else:
            self._file = None
        
        try:
            self._file = r'C:\etec\classification_environment\tmp.mat'
            self._read_variables_from_file()
        except:
            print('error')
        
    def set_file(self, file):
        
        self._file = file
        self._read_mat_file()
        
    def file(self):
        
        return self._file

    def _read_variables_from_file(self):
        
        mat = scipy.io.whosmat(self._file, squeeze_me= True)

        for variable in mat:
            if variable[1] == (1,1):
                ### scalar
                self._outputs.update({variable[0]: PlugIns.NodeTemplates.Connector(variable[0], 'output', node= self)})
            else:
                self._outputs.update({variable[0]: PlugIns.NodeTemplates.DataConnector(variable, node= self)})
            
        
class mFunctionNode(PlugIns.NodeTemplates.FunctionNodeTemplate):
    
    _OPCODE = 'CALL_M_FUNCTION'
    _PLUGIN = 'MATLAB'
    
    @classmethod
    def file_extension(cls):
        
        return '.m'
    
    @classmethod
    def run_sequence_addition(cls):
        
        return RunSequenceAdditions
    
    
    def _read_from_file(self):
        
        self._read_allready = True
        
        field_name = None
        previous_property = None
        
        no_options = False
        
        
        with open(self.path() + self.name(), 'r') as file:
            
            
            line = file.readline()
            line = line.rstrip('\r\n')
            
            if not re.match(_M_FILE_HEADER_RE, line):
                raise Exception('Invalid Header: No valid m-File')
            
            ### get outputs
            leftside = re.search(_M_LEFT_SIDE, line) 
            if leftside:
                leftside = leftside.group().strip()
                if leftside[0] == '[' and leftside[-1] == ']':
                    leftside = re.split(r' *, *', leftside[1:-1])
                    for name in leftside:
                        self._outputs.update({name: PlugIns.NodeTemplates.Connector(name, 'output', node= self)})
                else:
                    self._outputs.update({leftside: PlugIns.NodeTemplates.Connector(leftside, 'output', node= self)})
                
            ### get inputs
            rightside = re.search(_M_RIGHT_SIDE, line)
            if rightside:
                rightside = rightside.group().strip()
                rightside = re.split(r' *, *', rightside)
                for name in rightside:
                    self._inputs.update({name: PlugIns.NodeTemplates.Connector(name, 'input', node= self)})
                
                if 'options' in self._inputs:
                    self._inputs.pop('options')
                else:
                    no_options = True
                    
            for line in file:
                line = line.rstrip('\r\n')
                
                
                if not line or line[0] != '%':
                    break
    
                line = line[1:].strip()
                
                
                if re.search(_FIELD_NAME_RE, line):
                    field_name = line
                    
                    continue
                
                #MAYBE: allow input + output format (3xN)
                ### INPUTS + OUTPUTS
#                 if (field_name == 'OUTPUTS') and re.match(_INPUT_RE, line):
#                     
#                     input_name    = re.search(_INPUT_NAME_RE, line).group()
#                     input_format  = re.search(_INPUT_FORMAT_RE, line)
#                     if input_format:
#                         input_format = input_format.group().strip()
#                     
#                     if field_name == 'INPUTS':
#                         self._inputs.update({input_name : input_format})
#                     if field_name == 'OUTPUTS':
#                         self._outputs.update({input_name : input_format})
                    
                        
                    continue
                ### OPTIONS
                if field_name == "OPTIONS" and re.match(_OPTION_RE, line):
                    
                    property_name    = re.search(_OPTION_NAME_RE, line).group()
                    property_default = re.search(_OPTION_DEFAULT_RE, line).group().strip()
                    
                    if not no_options:
                        self._options.update({property_name : PlugIns.NodeTemplates.ValueConnector(property_name, 'input', property_default, node= self)})
                    
                    continue
                
                ### GENERAL PROPERTIES
                if field_name:
                    
                    property_name    = re.search(_OPTION_NAME_RE, line)
                    if property_name:
                        property_name = property_name.group()
                        
                    elif line.strip() == '':
                        previous_property = None
                        continue
                    elif previous_property:
                        self._properties[field_name][previous_property] += '\n' + line
                    
                    property_default = re.search(_OPTION_DEFAULT_RE, line)
                    if property_default:
                        property_default = property_default.group().strip()
                        previous_property = property_name
                        
                        if field_name not in self._properties:
                            self._properties.update({field_name: {}})
                
                        self._properties[field_name].update({property_name: property_default})
                        
                    else:
                        continue

    
    
    
class RunSequenceAdditions(PlugIns.NodeTemplates.RunSequenceAdditions):
    
    #_OPCODE = 'CALL_M_FUNCTION'
    _OP_M_ADD_PATH        = 'ADD_PATH'
    _OP_M_REMOVE_PATH     = 'REMOVE_PATH'
    _OP_M_CLEAR           = 'CLEAR'
    
    _PLUGIN = 'MATLAB'
    
    def __init__(self, nodes):
        
        self._paths = set()
        names = {}
        self._path_conflict_table = {}
        
        ### look for identical function names
        # and set up path conflict table
        for node in nodes:
    
            if isinstance(node, mFunctionNode):
                if node.name() not in names:
                    # no other function with the same name
                    self._paths.add(node.path())
                    names.update({node.name(): node.path()})
                elif names[node.name()] == node.path():
                    pass
                else:
                    if node.name() not in self._path_conflict_table:
                        # second appearance
                        #initial_paths.update({node.path(): node.name()})
                        self._path_conflict_table.update({node.name(): [node.path(), names[node.name()]]})
                    else:
                        self._path_conflict_table[node.name()].append(node.path())
        
    
    def _change_path(self, node):
        
        sub_sequence = []
        
        remove_paths = self._path_conflict_table[node.name()].copy()
        remove_paths.remove(node.path())
         
        sub_sequence.append((self._PLUGIN, self._OP_M_REMOVE_PATH, remove_paths))
        self._paths = {path for path in self._paths if path not in remove_paths}
         
        sub_sequence.append((self._PLUGIN, self._OP_M_ADD_PATH, [node.path()]))
                     
        return sub_sequence
    
    def sequence_init_procedure(self):
        
        sequence = [(self._PLUGIN, self._OP_M_CLEAR)]
        sequence += [(self._PLUGIN, self._OP_M_ADD_PATH, list(self._paths))] 
        
        return sequence
        
    def sequence_pre_append_procedure(self, node):
        
        pass
    
    def sequence_post_creation(self, sequence):
        
        sequence += [(self._PLUGIN, self._OP_M_REMOVE_PATH, list(self._paths))]
        
        
        return sequence
    
    
    def priority_nodes(self, nodes):
        
        nice_nodes = set()
        
        for node in nodes:
            if isinstance(node, mFunctionNode) and node.path() in self._paths:
                nice_nodes.add(node)
        
        return nice_nodes
    
    def create_sequence_item(self, node, branchs, pipe_map):
        subsequence = []
        if node.path() not in self._paths:
            ad = self._change_path(node)
            
            subsequence += ad
        
        sequenceitem, pipe_map = super().create_sequence_item(node, branchs, pipe_map)
        subsequence.append(sequenceitem)
        
        return subsequence, pipe_map


class MATLABEngineThread(threading.Thread):
     
    _MATLAB_ENGINE_STARTET = 'MATLAB_ENGINE_STARTET'
     
    def __init__(self):
         
        super().__init__(daemon= True)
        self._eng = None
         
         
    def run(self):
        
        
        retcode = subprocess.call(["matlab", "-r", "\"run('C:\\etec\\PyDevWorkSpace\\ClassificationEnviroment\\matlab\\fNode.m');\""])#"-r", "fNode"
        
        if retcode:
            raise Exception('MATLAB process stopped not properly.')
         
    def eng(self):
        
        return self._eng



class MATLAB(PlugIns.PlugInTemplate.PlugIn):
    
    _OP_M_EDIT_CODE = 'EDIT_CODE'
    _OP_M_QUIT_SESSION = 'QUIT_SESSION'
    
    def __init__(self, logger):
        
        super().__init__()
        
        logger.info('Starting MATLAB')
        
        self._logger = logger
        

    def edit_code(self, file):
        
        if self._tcp_link:
            ###TODO: try except and check if DONE is returned
            print(self._tcp_link.send( (self._OP_M_EDIT_CODE, file) ))
        
           
    def nodes(self):
        
        return {mFunctionNode, matFileNode}
    
    
    def interpret(self, *operation):
        
        if not isinstance(operation, (tuple, list)) and operation[0] != 'MATLAB':
            self._logger.warning('Unknown format')
            
        operation = operation[1:]
        
        if self._tcp_link:
            
            ###TODO: try except
            ret = self._tcp_link.send( operation )
            
            if isinstance(ret, (list)) and ret[0] == 'RETURN':
                self._logger.info(str(ret[1]))
            elif isinstance(ret, (list)) and ret[0] == 'ERROR':
                if len(ret) > 1:
                    self._logger.error(str(ret[1:]))
                else:
                    self._logger.error('Unknown error accounted')
                
    def quit(self):
        
        
        if self._tcp_link:
            
            self._tcp_link.send( (self._OP_M_QUIT_SESSION,))
                                             
