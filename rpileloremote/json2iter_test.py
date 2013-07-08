import unittest
from json2iter import JSON2Iters
from itertools import *
from time import sleep, time

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

class TestJSON2Iters(unittest.TestCase):
    def test_int(self):
        int_list = [ x for x in take(10,JSON2Iters('42')) ]
        self.assertListEqual(10*[42], int_list)

    def test_timemout_empy(self):
        now = time()
        for x in JSON2Iters('{ "type" : "end", "timeout" : 1 }'):
            pass
        self.assertTrue(time() - now >= 1)

    def test_timemout(self):
        now = time()
        for x in JSON2Iters('{ "type" : "end", "timeout" : 1 , "value": 42}'):
            pass
        self.assertTrue(time() - now >= 1)

    def test_cycle(self):
        it =  JSON2Iters('{ "type" : "cycle", "value": { "type" : "end", "timeout" : 0.1, "value": 42 } }')
        int_list = [x for x in take(10,it)]
        self.assertListEqual(10*[42],int_list)
    
    def test_concat(self):
        it = JSON2Iters('{ "type" : "concat", "values": [{ "type" : "end", "timeout" : 0.5, "value": 1 }, { "type" : "end", "timeout" : 0.5, "value": 2 }, { "type" : "end", "timeout" : 0.5, "value": 3 }] }')
        now = time()
        for val in it:
            dt = time() - now
            if dt < 0.4 :
                self.assertEqual(val,1)
            elif dt > 0.6 and dt < 0.9:
                self.assertEqual(val,2)
            elif dt > 1.1:
                self.assertEqual(val,3)

    def test_math(self):
        import math
        for op in  [ "sin", "cos", "tan", "atan", "exp", "log", "sqrt" ]:
            it =  JSON2Iters('{ "type" : "%s", "value": 42 }' % op)
            int_list = [x for x in take(10,it)]
            value = getattr(math,op)(42)
            self.assertListEqual(int_list, 10*[value])

    def test_range(self):
        it = JSON2Iters('{ "type": "range", "min": 0, "max": 10}')
        int_list = [ x for x in it ]
        self.assertListEqual(int_list,range(10))
        
        
if __name__ == '__main__':
    unittest.main()

    
