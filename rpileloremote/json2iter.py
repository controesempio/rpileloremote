from itertools import *
from time import time as now, sleep
import json
import math

def variableRange(min_iter, max_iter):
    '''A range iterator, but with variable minimum and maximum'''
    current = None
    while True:
        min_val = min_iter.next()
        max_val = max_iter.next()

        if current == None or current < min_val:
            current = min_val
        else:
            current += 1

        if current >= max_val:
            return
        yield current

def restart(iterator):
    return chain.from_iterable(repeat(iterator))
        
def timeout(iterator,timeout_iterator):
    '''An iterator which is stopped after some time'''
    last_now = now()
    while True:
        if (now() - last_now) >= timeout_iterator.next():
            return
        yield iterator.next()

def timer(iterator,period):
    '''An iterator which is updated only at some periods of time'''
    last_now = now()
    output = None
    while True:
        while (now() - last_now > period):
            last_now = last_now + period
            output = iterator.next()
        yield output
        
class JSON2Iters(object):
    '''A JSON parser that creates iterators '''
    def __init__(self, jsonString):
        self.json = json.loads(jsonString)

    def __iter__(self):
        return self._parse(self.json).__iter__()

    @classmethod
    def _parse(cls, value):
        '''Recursive function which parses JSON and returns an iterator'''
        if type(value) is int or type(value) is float:
            return repeat(value)
    
        if type(value) is not dict:
            print "Only objects are accepted"
            return None

        if not 'type' in value:
            print "No type no party"
            return None

        t = value['type']
        if t == 'cycle':
            return cycle(cls._parse(value['value']))
        elif t == 'concat':
            return chain.from_iterable(map(cls._parse,value['values']))
        elif t == 'end':
            try:
                new_val = value['value']
            except KeyError:
                new_val = 0
            return timeout(cls._parse(new_val),cls._parse(value['timeout']))
        elif t == 'range':
            return variableRange(cls._parse(value['min']),cls._parse(value['max']))
        elif hasattr(math,t):
            return imap(getattr(math,t), cls._parse(value['value']))
        else:
            raise NotImplementedError
