# -*- coding: utf-8 -*-
'''
Created on 23.09.2015

@author: derChris
'''


import os

os.chdir(os.path.dirname(__file__))

print(os.getcwd())

command = r'''
C:\Users\derChris\Anaconda\envs\p34\Lib\site-packages\PySide\pyside-rcc.exe -py3 -o ../icons.py icons.qrd'''
  
os.system(command)



