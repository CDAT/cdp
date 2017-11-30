from __future__ import print_function

import unittest
import os
import sys
import cdp.cdp_parameter
import cdp.cdp_parser


class TestCDPParser(unittest.TestCase):

    class MyCDPParameter(cdp.cdp_parameter.CDPParameter):
        def check_values(self):
            pass

    class MyCDPParser(cdp.cdp_parser.CDPParser):
        def __init__(self, *args, **kwargs):
            super(TestCDPParser.MyCDPParser, self).__init__(
                TestCDPParser.MyCDPParameter, *args, **kwargs)

        def load_default_args(self):
            super(TestCDPParser.MyCDPParser, self).load_default_args()
            self.add_argument(
                '-v', '--vars',
                type=str,
                nargs='+',
                dest='vars',
                help='Variables to use',
                required=False)

    def write_file(self, file_name, contents):
        f = open(file_name, 'w')
        f.write(contents)
        f.close()

    def setUp(self):
        self.cdp_parser = self.MyCDPParser()
        # Writing files in Python 3 seems to be asynchonous or something like that.
        # Hence we need to load pre-written files, but only *.py
        self.prefix = 'cdp/test/parameter_files/'

    def test_load_default_args(self):
        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_load_default_args.py'])
        p = self.cdp_parser.get_orig_parameters()
        self.assertTrue(hasattr(p, 'vars'))
        self.assertEqual(p.vars, ['v1', 'v2'])

    def test_load_custom_args(self):
        self.cdp_parser.add_args_and_values(['-v', 'v1', 'v2'])

    def test_get_orig_parameters_with_cmdline_args(self):
        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_orig_parameters_with_cmdline_args.py', '-v', 'v1', 'v2'])
        p = self.cdp_parser.get_orig_parameters()
        self.assertTrue(hasattr(p, 'vars'))
        self.assertEqual(p.vars, ['v1', 'v2'])

    def test_get_other_parameters(self):
        json_str = '''
            {
                "mydiags": [
                    {
                        "param1": 1,
                        "param2": 2
                    },
                    {
                        "param1": "one",
                        "param2": "two"
                    }
                ]
            }
        '''
        try:
            self.write_file('test_get_other_parameters.json', json_str)
            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters.json'])
            p = self.cdp_parser.get_other_parameters()

            self.assertEqual(len(p), 2)
            self.assertTrue(hasattr(p[0], 'param1'))
            self.assertTrue(hasattr(p[0], 'param2'))
            self.assertEqual(p[0].param1, 1)
            self.assertEqual(p[0].param2, 2)
            self.assertEqual(p[1].param1, 'one')
            self.assertEqual(p[1].param2, 'two')

        finally:
            if os.path.exists('test_get_other_parameters.json'):
                os.remove('test_get_other_parameters.json')
        
    def test_get_other_parameters_with_many_jsons(self):
        json_str = '''
            {
                "mydiags": [
                    {
                        "param1": 1,
                        "param2": 2
                    },
                    {
                        "param1": "one",
                        "param2": "two"
                    }
                ]
            }
        '''
  
        try:
            self.write_file('test_get_other_parameters_with_many_jsons1.json', json_str)
            self.write_file('test_get_other_parameters_with_many_jsons2.json', json_str)
            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters_with_many_jsons1.json', 'test_get_other_parameters_with_many_jsons2.json'])
            p = self.cdp_parser.get_other_parameters()

            self.assertEqual(len(p), 4)

        finally:
            if os.path.exists('test_get_other_parameters_with_many_jsons1.json'):
                os.remove('test_get_other_parameters_with_many_jsons1.json')
            if os.path.exists('test_get_other_parameters_with_many_jsons2.json'):
                os.remove('test_get_other_parameters_with_many_jsons2.json')


    def test_get_other_parameters_with_cfg(self):
        cfg_str = '[Diags1]\n' 
        cfg_str += "num = 5\n"
        cfg_str += "str_path1 = my/output/dir\n"
        cfg_str += "str_path2 = 'my/output/dir'\n"
        cfg_str += 'str_path3 = "my/output/dir"\n'
        cfg_str += 'str_list1 = ["v1", "v2", "v3"]\n'
        cfg_str += "str_list2 = ['v1', 'v2', 'v3']\n"
        cfg_str += "int_list = [-1, 0, 1]\n"
        cfg_str += "float_list = [-1., 0., 1.,]\n"
        cfg_str += "mixed_num_list = [-1., 0, 1.,]\n"

        try:
            self.write_file('test_get_other_parameters_with_cfg.cfg', cfg_str)
            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters_with_cfg.cfg'])
            p = self.cdp_parser.get_other_parameters()[0]

            self.assertIsInstance(p.num, int)
            self.assertIsInstance(p.str_path1, str)
            self.assertIsInstance(p.str_path2, str)
            self.assertIsInstance(p.str_path3, str)

            self.assertIsInstance(p.str_list1, list)
            self.assertIsInstance(p.str_list1[0], str)
            self.assertIsInstance(p.str_list1[1], str)
            self.assertIsInstance(p.str_list1[2], str)

            self.assertIsInstance(p.str_list2[0], str)
            self.assertIsInstance(p.str_list2[1], str)
            self.assertIsInstance(p.str_list2[2], str)

            self.assertIsInstance(p.int_list[0], int)
            self.assertIsInstance(p.int_list[1], int)
            self.assertIsInstance(p.int_list[2], int)

            self.assertIsInstance(p.float_list[0], float)
            self.assertIsInstance(p.float_list[1], float)
            self.assertIsInstance(p.float_list[2], float)

            self.assertIsInstance(p.mixed_num_list[0], float)
            self.assertIsInstance(p.mixed_num_list[1], int)
            self.assertIsInstance(p.mixed_num_list[2], float)

        finally:
            if os.path.exists('test_get_other_parameters_with_cfg.cfg'):
                os.remove('test_get_other_parameters_with_cfg.cfg')

    def test_get_parameters(self):
        cfg_str = '[Diags1]\n'
        cfg_str += "num = 5\n"
        cfg_str += "path = my/output/dir\n"
        cfg_str += "vars = ['v2']\n"

        self.write_file('test_get_parameters.cfg', cfg_str)

        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py', '-d', 'test_get_parameters.cfg', '-v', 'v3'])
        p = self.cdp_parser.get_parameters()[0]

        self.assertEqual(p.num, 10)
        self.assertEqual(p.other_num, 11)
        self.assertEqual(p.path, 'my/output/dir')
        self.assertEqual(p.vars, ['v3'])

    def test_get_parameters_with_p_only(self):
        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters_with_p_only.py'])
        p = self.cdp_parser.get_parameters()[0]
    
    def test_get_parameters_with_d_only(self):
        json_str = '''
            {
                "mydiags": [
                    {
                        "param1": 1,
                        "param2": 2
                    },
                    {
                        "param1": "one",
                        "param2": "two"
                    }
                ]
            }
        '''
  
        try:
            self.write_file('test_get_parameters_with_d_only.json', json_str)
            self.cdp_parser.add_args_and_values(['-d', 'test_get_parameters_with_d_only.json'])
            p = self.cdp_parser.get_parameters()

            self.assertEqual(len(p), 2)

        finally:
            if os.path.exists('test_get_parameters_with_d_only.json'):
                os.remove('test_get_parameters_with_d_only.json')


    def test_get_other_parameters_with_file_paths(self):
        cfg_str1 = '[Diags1]\n'
        cfg_str1 += "num = 0\n"
        cfg_str1 += '[Diags2]\n'
        cfg_str1 += "num = 1\n"

        cfg_str2 = '[Diags1]\n'
        cfg_str2 += "num = 2\n"

        py_str = 'num = 10\n'
        py_str += 'other_num = 11\n'
        py_str += "vars = ['v1']\n"

        try:
            self.write_file('test_get_other_parameters_with_file_paths1.cfg', cfg_str1)
            self.write_file('test_get_other_parameters_with_file_paths2.cfg', cfg_str2)
            self.write_file('params.py', py_str)

            # This is called when by the user when a cdp parser is initalized,
            # so we have do to this here.
            self.cdp_parser.add_args_and_values(['-p', 'params.py'])

            files = ['test_get_other_parameters_with_file_paths1.cfg', 'test_get_other_parameters_with_file_paths2.cfg']
            params = self.cdp_parser.get_other_parameters(files_to_open=files)
            self.assertEqual(len(params), 3)

            for p in params:
                if p.num not in [0, 1, 2]:
                    self.fail('get_other_parameters() did not correctly get the jsons')

        finally:
            if os.path.exists('test_get_other_parameters_with_file_paths1.cfg'):
                os.remove('test_get_other_parameters_with_file_paths1.cfg')
            if os.path.exists('test_get_other_parameters_with_file_paths2.cfg'):
                os.remove('test_get_other_parameters_with_file_paths2.cfg')

if __name__ == '__main__':
    unittest.main()
