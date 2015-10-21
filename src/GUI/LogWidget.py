# -*- coding: utf-8 -*-
'''
Created on 22.09.2015

@author: derChris
'''



from PySide import QtGui#, QtCore
import logging

_WELCOME = '''
        =================
         Welcome to fNODE
        =================

'''

class LogWidget(QtGui.QTextEdit):

    
    def __init__(self, parent= None):
    
        super().__init__(parent)
        
        ### GUI
        #self._edit = QtGui.QTextEdit(self)
        self.setReadOnly(True)
        
        #self.setFeatures(self.DockWidgetFloatable | self.DockWidgetMovable | self.DockWidgetClosable)
        #self.setFloating(True)
        
        #self.setWidget(self._edit)
        self.setWindowTitle('fNode Logger')
        self.setWindowIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        self.setGeometry(1150, 600, 500, 300)
        
        self.setStyleSheet('''QTextEdit {color: #808080;
                                         font: bold 11pt System;
                                         background: #000000;}''')
        
        ### log handling
        #format_str = '<%(asctime)s - %(name)s - %(levelname)s> %(message)s'
        format_str = '%(name)s.%(levelname)s>> %(message)s\t\t(%(asctime)s)'
        #logger.addHandler(handler)
        logging.basicConfig(stream= self, format= format_str, level= logging.DEBUG)

        logging.getLogger('logwidget').debug('Welcome')
        
        self.setPlainText(_WELCOME)
        
        self.show()
        
    def write(self, msg):
        
        if msg != '\n':
            self.append(msg)
    
    def changeEvent(self, event):
        
        #if event.type() == QtCore.QEvent.ActivationChange:
             
#             if self.isActiveWindow():
#                 print('stack parent under')
#                 self.parent().stackUnder(self)
#             else:
#                 self.stackUnder(self.parent())
        super().changeEvent(event)