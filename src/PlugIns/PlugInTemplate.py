# -*- coding: utf-8 -*-
'''
Created on 11.09.2015

@author: derChris
'''

from abc import abstractmethod



class PlugIn():
    @abstractmethod
    def __init__(self):
        
        self._tcp_link = None
        
    
    @abstractmethod
    def nodes(self):
        
        return None
    
    @abstractmethod
    def run_sequence_additions(self):
        
        return None
    
    @abstractmethod
    def interpreter(self):
        
        pass
    
    def name(self):
        
        return self.__class__.__name__
    
    def set_tcp_link(self, link):
        
        self._tcp_link = link
        
        
    def quit(self):
        
        pass