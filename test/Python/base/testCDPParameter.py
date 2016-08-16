import unittest
import sys
sys.path.insert(0, '../../../src/Python/base/')
from CDPParameter import *

class testCDPParameter(unittest.TestCase):
    def setUp(self):

        #CDPParameter is an abstract base class, so we need to inherit from
        #it to test it.
        class myCDPParameter(CDPParameter):
            def check_values(self):
                pass

        self.cdpparameter = myCDPParameter()

    def test_load_working_parameter(self):
        self.assertEquals(None, self.cdpparameter.load_parameter_from_py('./testCDPParameter.py'))

if __name__ == '__main__':
    unittest.main()
