import unittest
from CDP.PMP.PMPParameter import *

class testPMPParameter(unittest.TestCase):

    def setUp(self):
        self.pmp_parameter = PMPParameter()
    
    def test_check_vars_with_nonlist_vars(self):
        self.pmp_parameter.vars = 'clt, hfss, pr'
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_vars()

    def test_check_vars_with_nonvalid_vars(self):
        self.pmp_parameter.vars = ['this_is_not_a_var']
        with self.assertRaises(ValueError):
            self.pmp_parameter.check_vars()

if __name__ == '__main__':
    unittest.main()
