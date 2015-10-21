# -*- coding: utf-8 -*-
'''
Created on 14.09.2015

@author: derChris
'''



# -*- coding: utf-8 -*-
'''
Created on 27.08.2015

@author: derChris
'''

import socketserver
import threading
import socket

import json

import logging

class TCPLink():
    
    def __init__(self, address, plugin, logger):
        
        self._address = address
        self._plugin = plugin
        
        self._logger = logger
        
    def send(self, message):
        
        s = socket.socket()
        
        s.connect(self._address)
        
        dumped = json.dumps(message)
        
        #MAYBE: replace readline in MATLAB
        s.sendall(dumped.encode() + b'\n')
        
        try:
            data = s.recv(1024)
            
            data = json.loads(data.decode())
        except:
            data = ['CONNECTION LOST']
            #TODO: retry
            self._plugin.set_tcp_link(None)
            self._logger.warning(self._plugin.name() + ' connection lost.')
            
        s.close()
        
        return data     
    
class TCPRegistrationHandler(socketserver.BaseRequestHandler):
    
    _logger = logging.getLogger('TCPServer')
    
    def handle(self):
        
        self.data = self.request.recv(1024).strip()
        
        for plugin in self.server._plugins:
            plugin_name = plugin.name().encode()
            
            if self.data == b'Hallo fNODES. Here is ' + plugin_name + b'.':
                
                self.request.sendall(b'Welcome ' + plugin_name)
    
                ### establish link
                plugin.set_tcp_link(TCPLink(('localhost', 53715+1), plugin, self._logger))
                
                self._logger.info(plugin.name() + ' connected.')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    
    def __init__(self, adress, handler, plugins):
        self._plugins = plugins
        
        super().__init__(adress, handler)
        
        logging.getLogger('TCPServer').info('server started')
        
        
def set_up_server(plugins):
    
    HOST, PORT = 'localhost', 53715
    
    logging.getLogger('TCPBridge').info('start server')
    
    socket.setdefaulttimeout(1)
    
    server = ThreadedTCPServer((HOST, PORT), TCPRegistrationHandler, plugins)

    server_thread = threading.Thread(target=server.serve_forever)
    
    server_thread.daemon = True
    server_thread.start()
    
    
    
##############
### TESTS
##############    
if __name__ == '__main__':
    TCP_IP = 'localhost'
    TCP_PORT = 53715
    BUFFER_SIZE = 1024
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.connect((TCP_IP, TCP_PORT))
     
    s.sendall(b'Hello damn right!!\n')
    s.close()
    
    print('done')