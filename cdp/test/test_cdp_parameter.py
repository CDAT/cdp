import unittest
import os
import cdp.cdp_parameter


class TestCDPParameter(unittest.TestCase):
    class MyCDPParameter(cdp.cdp_parameter.CDPParameter):
        def check_values(self):
            pass

    def write_file(self, file_name, contents):
        f = open(file_name, 'w')
        f.write(contents)
        f.close()

    def setUp(self):
        self.cdp_parameter = self.MyCDPParameter()

    def test_load_working_parameter(self):
        self.write_file('CDPParameterFile.py', 'var0 = "var0"\n')
        self.cdp_parameter.load_parameter_from_py('CDPParameterFile.py')
        self.assertEquals(self.cdp_parameter.var0, 'var0')
        os.remove('CDPParameterFile.py')
        os.remove('CDPParameterFile.pyc')

    def test_load_broken_parameter_with_dot_in_path(self):
        self.write_file('CDP.Parameter.File.Wrong.py', 'var0 = "var0"\n')
        with self.assertRaises(ValueError):
            self.cdp_parameter.load_parameter_from_py(
                'CDP.Parameter.File.Wrong.py')
        os.remove('CDP.Parameter.File.Wrong.py')

    def test_load_parameter_with_non_existing_file(self):
        with self.assertRaises(IOError):
            self.cdp_parameter.load_parameter_from_py('thisFileDoesntExist.py')

    def test_load_parameter_with_import_in_file(self):
        self.write_file('CDPParameterFile2.py',
                        'import datetime\ndatetime.datetime.now()\n')
        try:
            self.cdp_parameter.load_parameter_from_py('CDPParameterFile2.py')
        except:
            self.fail('Test failed with import statement in parameter file.')
        finally:
            os.remove('CDPParameterFile2.py')
            os.remove('CDPParameterFile2.pyc')

if __name__ == '__main__':
    unittest.main()
