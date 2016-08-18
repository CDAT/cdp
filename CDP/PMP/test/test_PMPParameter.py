import unittest
from CDP.PMP.PMPParameter import *

class testPMPParameter(unittest.TestCase):

    def setUp(self):
        self.pmp_parameter = PMPParameter()

    def test_check_vars_with_nonlist_vars(self):
        self.pmp_parameter.vars = 'clt, hfss, pr'
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_vars()

    def test_check_ref_with_nonlist_ref(self):
        self.pmp_parameter.ref = 'default'
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_ref()

    def test_check_target_grid_with_nonstr_grid(self):
        self.pmp_parameter.target_grid = ['default']
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_target_grid()

if __name__ == '__main__':
    unittest.main()
