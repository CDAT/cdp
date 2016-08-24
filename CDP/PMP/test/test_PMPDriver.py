import unittest
from CDP.PMP.PMPParameter import *
from CDP.PMP.PMPDriverRunDiags import *

class testPMPDriverRunDiags(unittest.TestCase):

    def setUp(self):
        self.pmp_parameter = PMPParameter()
        self.pmp_driver_run_diags = PMPDriverRunDiags(self.pmp_parameter)


    def test_calculate_level_with_height(self):
        var = ['hus_850']
        var_name_split = var[0].split('_')
        self.pmp_driver_run_diags.calculate_level(var_name_split)
        self.assertEquals(self.pmp_driver_run_diags.level, 850*100)

    def test_calculate_level_with_no_height(self):
        var = ['hus']
        var_name_split = var[0].split('_')
        self.pmp_driver_run_diags.calculate_level(var_name_split)
        self.assertEquals(self.pmp_driver_run_diags.level, None)


if __name__ == '__main__':
    unittest.main()
