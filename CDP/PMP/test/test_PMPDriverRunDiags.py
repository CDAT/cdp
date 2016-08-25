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

    def test_loading_of_obs_info_dic(self):
        try:
            path = 'obs_info_dictionary.json'
            self.pmp_driver_run_diags.load_path_as_file_obj(path)
        except:
            self.fail('Cannot open obs_info_dictionary.json. Test failed.')

    def test_loading_of_default_regions(self):
        try:
            path = 'default_regions.py'
            self.pmp_driver_run_diags.load_path_as_file_obj(path)
        except:
            self.fail('Cannot open default_regions.py. Test failed.')

    def test_loading_of_disclaimer_file(self):
        try:
            path = 'disclaimer.txt'
            self.pmp_driver_run_diags.load_path_as_file_obj(path)
        except:
            self.fail('Cannot open disclaimer.txt. Test failed.')

if __name__ == '__main__':
    unittest.main()
