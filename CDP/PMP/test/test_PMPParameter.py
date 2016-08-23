import unittest
from CDP.PMP.PMPParameter import *

class testPMPParameter(unittest.TestCase):

    def setUp(self):
        self.pmp_parameter = PMPParameter()

    def test_check_vars_with_nonlist_value(self):
        self.pmp_parameter.vars = 'clt, hfss, pr'
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_vars()

    def test_check_ref_with_nonlist_value(self):
        self.pmp_parameter.ref = 'default'
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_ref()

    def test_check_target_grid_with_nonstr_value(self):
        self.pmp_parameter.target_grid = ['default']
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_target_grid()

    def test_check_regrid_tool_with_nonstr_value(self):
        self.pmp_parameter.regrid_tool = ['regrid2']
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_regrid_tool()

    def test_check_regrid_method_with_nonstr_value(self):
        self.pmp_parameter.regrid_method = ['linear']
        with self.assertRaises(TypeError):
            self.pmp_parameter.check_regrid_method()

    def test_check_save_mod_clims_with_none(self):
        self.pmp_parameter.save_mod_clims = None
        with self.assertRaises(ValueError):
            self.pmp_parameter.check_save_mod_clims()


if __name__ == '__main__':
    unittest.main()
