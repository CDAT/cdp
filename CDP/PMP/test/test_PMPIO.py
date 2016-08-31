import unittest
from CDP.PMP.PMPIO import *

class testPMPIO(unittest.TestCase):

    def setUp(self):
        self.pmp_io = PMPIO('root', 'file_template')

    def tearDown(self):
        #eventually delete all of the files that PMPIO creates
        pass


    def test_write_with_failing_extension(self):
        with self.assertRaises(RuntimeError):
            self.pmp_io.write({}, extension='.py')

if __name__ == '__main__':
    unittest.main()
