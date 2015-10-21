# -*- coding: utf-8 -*-
'''
Created on 18.08.2015

@author: derChris
'''

import json


def save(file, data):
    
    
    
    with open(file, 'w') as file:
            json.dump(data, file, sort_keys=True, indent=4, separators=(',', ': '))
    
def load(file):
    
    
    with open(file, 'r') as file:
        data = json.load(file)

    return data
    