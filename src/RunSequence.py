# -*- coding: utf-8 -*-
'''
Created on 11.09.2015

@author: derChris
'''

import logging

#################
### RunSequence
#################
### ERRORS
class LoopBackError(Exception):
            def __init__(self, description):
                super(LoopBackError, self).__init__(description)

class RunSequence():
    
    _logger = logging.getLogger('RunSequence')
    
    def __init__(self, nodes, plugin_manager):
        
        self._plugin_manager = plugin_manager
        self._additions = self._load_additions(nodes)
        
        sequence = self._init_sequence()
        
        
        pipe_map = {}
        
        while nodes:
            
            ### get function node without inputs
            focus = self._get_entry_node(nodes)
            
            if not focus:
                ### no entry point into system
                self._logger.error('No entry point found.')
                return
                #raise LoopBackError('No entry point found.')
            
            branchs = {focus}
            
            #TODO: implement forward direction for double piped nodes
            ### backward direction
            while branchs:
                # choose first branch which path is in paths or the first one to process
                focus = self._choose_next_branch(branchs, pipe_map)
                
                # remove processing node from list
                try:
                    nodes.remove(focus)
                    branchs.remove(focus)
                    
                except ValueError:
                
                    self._logger.error('Node not in list.')
                    return
                    #raise LoopBackError('Node not in list.')
                
                branchs = branchs.union(self._next_nodes(focus, pipe_map))
                
                subsequence, pipe_map = plugin_manager.create_subsequence(self._additions, focus, branchs, pipe_map)
                
                if subsequence:
                    sequence += subsequence
                
                
                

        sequence = self._post_creation_procedure(sequence)
        
        
        for command in sequence:
            
            self._plugin_manager.interpret(command)
        
    def _load_additions(self, nodes):
        
        additions = {}
        
        for node in nodes:
            
            if node.run_sequence_addition():
                additions.update({node.__class__: node.run_sequence_addition()(nodes)})
            
        return additions
    
    def _init_sequence(self):
        
        sequence = []
        # do plugin init sequences
        for addition in self._additions.values():
            
            sequence += addition.sequence_init_procedure()
            
        return sequence
    
    def _post_creation_procedure(self, sequence):
        
        
        for addition in self._additions.values():
            
            sequence = addition.sequence_post_creation(sequence)
            
        return sequence
    
        
    def _next_nodes(self, focus, pipe_map):
        
        nodes = focus.following_nodes()
        
        output = nodes.copy()
        
        while nodes:
            
            node = nodes.pop()
            
            if node.unresolved_input_pipes(pipe_map):
                
                for pipe in node.unresolved_input_pipes(pipe_map):
                    
                    if pipe.node_at_output() == focus:
                        nodes.remove(pipe.node_at_output())
            else:
                output.add(node)
        
        return output
            
            
    def _get_entry_node(self, nodes):
        
        focus = None
        for node in nodes:
            if not node.has_inputs():
                focus = node
                break
        
        
                
        return focus
            
    def _choose_next_branch(self, branchs, pipe_map):
        
        nodes = set()
        focus = None
        
        for addition in self._additions.values():
            nodes.update(addition.priority_nodes(branchs))
            
        if nodes:    
            for node in nodes:
                if not node.unresolved_input_pipes(pipe_map):
                    focus = node
                    break 
            
        if not focus:
            for node in branchs:
                if not node.unresolved_input_pipes(pipe_map):
                    focus = node
                    break
        
            
        if not focus:
            self._logger.error('No node found to proceed with.')
            #raise Exception('No node found to proceed with.')
                        
        return focus

