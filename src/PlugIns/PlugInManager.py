# -*- coding: utf-8 -*-
'''
Created on 27.08.2015

@author: derChris
'''

import os
import importlib
import logging

import PlugIns.TCPBridge
import PlugIns.NodeTemplates
from PlugIns.PlugInTemplate import PlugIn


class PlugInManager():
    
    def __init__(self):
        
        self._plugins = set()
        
        self.load_plugins()
        
        PlugIns.TCPBridge.set_up_server(self._plugins)
    
    def __getitem__(self, plugin):

        plugin_classes = {plugin.__class__.__name__: plugin for plugin in self._plugins}
        
        if plugin in plugin_classes and isinstance(plugin_classes[plugin], PlugIn):
            return plugin_classes[plugin]
        else:
            raise KeyError(plugin + ' is not a loaded plugin.')
        
        
    def load_plugins(self):
        
        path = os.path.dirname(__file__)
        
        for dirname in os.listdir(path):
            
            if not dirname.startswith('_') and os.path.isdir(path + '\\' + dirname):
                
                for name in os.listdir(path + '\\' + dirname):
                    
                    if dirname + '.py' == name:
                        
                        plugin = importlib.import_module('PlugIns.' + dirname + '.' + dirname)
                        
                        try:
                            logger = logging.getLogger(dirname)
                            plugin_object = plugin.__dict__[dirname](logger)
                        except KeyError:
                            raise Exception('PlugIn class "' + dirname + '" doesn''t exist.')
                        
                        if not isinstance(plugin_object, PlugIn):
                            raise Exception('PlugIn class has to be a derivative of PlugInTemplate.PlugIn')
                        
                        self._plugins.add(plugin_object)
                        
                        
    def function_node_extensions(self):
        
        functions = {}
        
        for plugin in self._plugins:
            
            for node in plugin.nodes():
                
                if isinstance(node, PlugIns.NodeTemplates.FunctionNodeTemplate):
                    functions.update({node.file_extension(): node})
                
        return functions


    def create_subsequence(self, additions, node, branchs, pipemap):
        
        if node.__class__ in additions:
            #TODO: exception handling
            
            return additions[node.__class__].create_sequence_item(node, branchs, pipemap)
        else:
            return node.create_sequence_item(node, pipemap)
            #raise Exception('No addition found for: ' + node.name())
        
    def create_node(self, function_info, system):
        
        if 'type' not in function_info:
            raise Exception('Incompatible function info.')
        
        for plugin in self._plugins:
            
            for node in plugin.nodes():
                
                if node.__name__ == function_info['type']:
                    return node(function_info['name'], system= system, data= function_info)
                        
        raise Exception('No appropriate node class found for: ' + function_info['type'])

    def interpret(self, command):
        
        for plugin in self._plugins:
            
            if plugin.__class__.__name__ == command[0]:
                
                plugin.interpret(*command)

    def quit(self):
        
        for plugin in self._plugins:
            
            plugin.quit()
            
    
##############
### TEST
##############

if __name__ == '__main__':
    
    man = PlugInManager()
    
    
    