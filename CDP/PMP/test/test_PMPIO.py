import unittest
import os
import MV2
from CDP.PMP.PMPIO import *

class testPMPIO(unittest.TestCase):

    def setUp(self):
        self.path = os.path.realpath(__file__).replace('test_PMPIO.py', '')
        self.filename = 'test'
        self.pmp_io = PMPIO(self.path, self.filename)

    def test_write_with_failing_extension(self):
        with self.assertRaises(RuntimeError):
            self.pmp_io.write({}, extension='py')

    def test_write_json_with_no_failures(self):
        try:
            self.pmp_io.write({}, extension='json')
        except:
            self.fail('Cannot write json file. Test failed.')
        finally:
            os.remove(self.path + '/' + self.filename + '.json')

    def test_write_txt_with_no_failures(self):
        try:
            self.pmp_io.write({}, extension='txt')
        except:
            self.fail('Cannot write test file. Test failed.')
        finally:
            os.remove(self.path + '/' + self.filename + '.txt')

    def test_write_nc_with_no_failures(self):
        try:
            self.pmp_io.write(MV2.arange(12.), extension='nc')
        except:
            self.fail('Cannot write Net-CDF file. Test failed.')
        finally:
            os.remove(self.path + '/' + self.filename + '.nc')


if __name__ == '__main__':
    unittest.main()
