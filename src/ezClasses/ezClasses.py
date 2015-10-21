# -*- coding: utf-8 -*-
'''
Created on 05.09.2015

@author: derChris
'''



class ezDict(dict):
    
    def __missing__(self, key):
        
        self.update({key: ezDict()})
        return self[key]
        
    def reduce(self):
        
        items = list(self.items())
        for key, value in items:
            if isinstance(value, ezDict):
                value.reduce()
                
            if not value:
                
                self.pop(key)
                
        return self
                

if __name__ == '__main__':
    
    x = ezDict()
    
    x['heinz']['klaus'] = 'wolfgang'
    
    x['heinz']['juergen'] = 'stefan'
    
    x['stefanie']['ursula'] = {}
    
    print(x)
    
    
    
    print(x.reduce())