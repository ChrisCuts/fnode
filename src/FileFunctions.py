# -*- coding: utf-8 -*-
'''
Created on 13.08.2015

@author: derChris
'''

import os
import re

from collections import OrderedDict

### CONSTs
_INITIAL_FILE_SCAN_DEPTH = 2
_DEFAULT_WORKPATH = 'C:\etec\classification_environment'
### REs
_NUMBER_RE  = re.compile('[+-]?[0-9]+(\.[0-9]+)?([eE][+-][0-9]+)?')

_NEXT_FOLDER_IN_PATH = re.compile(r'^\w*(?=\\)')


_function_abilities = {}

class Folder():
    
    def __init__(self, name, parent = None, file_manager= None):
        
        self._name = name
        self._parent = parent
        
        if file_manager:
            self._file_manager = file_manager
        elif parent:
            self._file_manager = parent._file_manager
            
        self._files = OrderedDict()
        self._subfolders = []
        
        if parent:
            parent.append_folder(self)
            
    def append_folder(self, item):
        
        self._subfolders.append(item)
        
    def name(self):
        
        return self._name
    
    def path(self):
        if self._parent:
            return self._parent.path() + self._name + '\\'
        elif self._name == '.':
            
            return self._file_manager.current_workpath() + '\\'
        else:
            return self._name
    
    def relative_path(self):
        
        if self._parent:
            return self._parent.relative_path() + self._name + '\\'
        elif self._name == '.':
            
            return '.\\'
        else:
            return self._name
        
    def files(self):
        
        return self._files
    
    def subfolders(self):
        
        return self._subfolders
    
    def find_folder(self, path):
        
        if path.startswith(self._name):
            
            path = path[len(self._name):]
            
            if path.startswith('\\'):
                path = path[1:]
            
            
            if path == '':
                return self
            
            elif re.search(_NEXT_FOLDER_IN_PATH, path):
                #look for next folder
                sub = re.search(_NEXT_FOLDER_IN_PATH, path).group()
                
                
            else:
                sub = path
            
            if not self._subfolders:
                    self.scan_folders()
                    
            for subfolder in self._subfolders:
                if subfolder.name() == sub:
                    return subfolder.find_folder(path)
            
        else:
            
            raise Exception(self._name + ' does not start with path.')
        
    def find_function(self, path, name):
    
        folder = self.find_folder(path)    
        #look for function
        for file in folder._files:
            if file[0] == name:
                return file
        
        raise Exception('File not found.')
    
        
    def scan_folders(self, depth = 0):
        
        for name in os.listdir(self.path()[2:]):
            
            if not re.match('\_', name):
                
                if os.path.isdir(self.path() + '\\' + name):
                    
                    ### is folder
                    if depth >= _INITIAL_FILE_SCAN_DEPTH:
                        return
                    else:
        
                        names = {}
                        for subfolder in self._subfolders:
                            names.update({subfolder.name(): subfolder})
                            
                        if name in names:
                            names[name].scan_folders(depth+1)
                        else:
                            
                            subfolder = Folder(name, self, self._file_manager)
                            subfolder.scan_folders(depth+1)
                            
                else:
                    ### is file
                    # use overloaded function class for each file ending
                    # class template is FileFunctions.FunctionTemplate
                    
                    for file_ending, class_handle in self._file_manager.supported_file_extensions().items():
                        
                        if name.endswith(file_ending):
                            files = set()
                            
                            if name not in files:
                                self._files.update({name: {'name': name,
                                                           'folder_item': self,
                                                           'type': class_handle.__name__}}) #'node': class_handle
                            
                                
                            
        
        
class FileManager():
    
    def __init__(self, plugin_manager):
        
        self._current_workpath = _DEFAULT_WORKPATH 
        self._plugin_manager = plugin_manager
        
        #os.chdir(self.current_workpath())
        
        self._root_folder = Folder('.', file_manager= self) 
        self._root_folder.scan_folders()
        
        
        
    def root_folder(self):
        return self._root_folder    
    
    def current_workpath(self):
        return self._current_workpath

    def supported_file_extensions(self):

        return self._plugin_manager.function_node_extensions()
        
##############
### TEST
##############
if __name__ == '__main__':
    pass




