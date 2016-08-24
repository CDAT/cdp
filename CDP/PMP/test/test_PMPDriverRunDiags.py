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

    def test_that_load_obs_dic_passes(self):
        try:
            self.pmp_driver_run_diags.load_obs_dic()
        except:
            self.fail('Cannot open observation dictionary. Test failed.')

    def test_that_set_regions_dic_passes(self):
        try:
            self.pmp_driver_run_diags.set_regions_dic()
        except:
            self.fail('Cannot open default_regions dictionary. Test failed.')

if __name__ == '__main__':
    unittest.main()
