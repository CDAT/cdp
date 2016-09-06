import unittest
import os
from CDP.PMP.PMPIO import *

class testPMPIO(unittest.TestCase):

    def setUp(self):
        path = os.path.realpath(__file__).replace('test_PMPIO.py', '')
        self.pmp_io = PMPIO(path, 'somefile2')

    def tearDown(self):
        # Eventually delete all of the files that PMPIO creates
        pass


    def test_write_with_failing_extension(self):
        with self.assertRaises(RuntimeError):
            self.pmp_io.write({}, extension='py')

    def test_write_json_with_no_failures(self):
     DOM   try:
            self.pmp_io.write({}, extension='json')
        except:
            self.fail('Cannot write json file. Test failed.')

if __name__ == '__main__':
    unittest.main()
