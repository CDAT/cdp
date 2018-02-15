from __future__ import print_function

import unittest
import os
import sys
import cdp.cdp_parameter
import cdp.cdp_parser
import os

class TestCDPParserOverload(unittest.TestCase):
    def setUp(self):
        pth = os.path.join(os.path.dirname(__file__),"json_files")
        self.my_parser = cdp.cdp_parser.CDPParser(None,[os.path.join(pth,"DefArgsCIA.json"),
                                                    os.path.join(pth,"mydefs.json")])
        self.my_parser.use("p")
        self.my_parser.use("diags")
        self.my_parser.use("mns2")
        self.my_parser.use("mns")

    def test_overload(self):
        # print(self.my_parser.view_args())
        p = self.my_parser.get_parameter()
        self.assertTrue(hasattr(p,"modnames2"))
        self.assertTrue(p.modnames2 == None)
        self.assertTrue(hasattr(p,"modnames"))
        self.assertTrue(p.modnames == "BBBB")

    def test_overload_cmd_line(self):
        self.my_parser.add_argument("--mns2","--modnames2",dest="modnames2",default="NEW")
        p = self.my_parser.get_parameter()
        self.assertTrue(p.modnames2 == "NEW")

class TestCDPParser(unittest.TestCase):

    class MyCDPParameter(cdp.cdp_parameter.CDPParameter):
        def __init__(self):
            self.vars = ['default_vars']
            self.param1 = 'param1'
            self.param2 = 'param2'

        def check_values(self):
            pass

    class MyCDPParser(cdp.cdp_parser.CDPParser):
        def __init__(self, *args, **kwargs):
            super(TestCDPParser.MyCDPParser, self).__init__(
                TestCDPParser.MyCDPParameter, *args, **kwargs)

        def load_default_args(self, files=[]):
            super(TestCDPParser.MyCDPParser, self).load_default_args(files)
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
        # Writing files in Python 3 seems to be asynchronous or something like that.
        # Hence we need to load pre-written files, but only *.py
        self.prefix = 'cdp/test/parameter_files/'

    def test_init_parser_without_parameter_class(self):
        class MyOtherParser(cdp.cdp_parser.CDPParser):
            pass
        
        MyOtherParser()
        cdp.cdp_parser.CDPParser()

    def test_load_default_args(self):
        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_load_default_args.py'])
        p = self.cdp_parser.get_orig_parameters()
        self.assertTrue(hasattr(p, 'vars'))
        self.assertEqual(p.vars, ['v1', 'v2'])

    def test_load_from_json_and_use_only_one(self):
        mycdp = self.MyCDPParser(os.path.join(sys.prefix, 'share' ,'cdp', 'default_args.json'))
        mycdp.use("-n")
        nm_spc = mycdp.parse_args([])
        actual_used = []
        for att in dir(nm_spc):
            if not att[0] == "_":
                actual_used.append(att)
        self.assertEqual(sorted(actual_used),['num_workers', 'vars'])

    def test_load_custom_args(self):
        self.cdp_parser.add_args_and_values(['-v', 'v1', 'v2'])

    def test_get_orig_parameters(self):
        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_orig_parameters.py'])
        p = self.cdp_parser.get_orig_parameters()
        self.assertTrue(hasattr(p, 'param1'))
        self.assertEqual(p.param1, 'py_param1')

        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_orig_parameters.py', '-v', 'v1', 'v2'])
        # when mixing and matching any two of the three input options(*py, *cfg/*json, cmdline args), 
        # you must use CDPParser.get_parameter() or CDP.get_parameters()
        p = self.cdp_parser.get_parameter()
        self.assertTrue(hasattr(p, 'vars'))
        self.assertEqual(p.vars, ['v1', 'v2'])
        p = self.cdp_parser.get_parameter(default_vars=False)
        self.assertEqual(getattr(p, 'param2', None), None)

        self.cdp_parser.add_argument(
            '--param2',
            type=str,
            dest='param2',
            default='param2_cmd_default',
            required=False)

        p = self.cdp_parser.get_orig_parameters(default_vars=False, cmd_default_vars=False)
        self.assertEqual(p.param1, 'py_param1')
        self.assertEqual(getattr(p, 'param2', None), None)

        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_orig_parameters.py'])
        p = self.cdp_parser.get_orig_parameters(default_vars=False, cmd_default_vars=True)
        self.assertEqual(p.param2, 'param2_cmd_default')
        self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_orig_parameters.py', '--param2', 'new_param2'])
        p = self.cdp_parser.get_parameter(default_vars=False, cmd_default_vars=True)
        self.assertEqual(p.param2, 'new_param2')

    def test_get_other_parameters(self):
        json_str = '''
            {
                "mydiags": [
                    {
                        "param1": 1,
                        "param2": 2
                    },
                    {
                        "param1": "one"
                    }
                ]
            }
        '''
        try:
            self.write_file('test_get_other_parameters.json', json_str)
            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters.json'])
            p = self.cdp_parser.get_other_parameters(default_vars=True)

            self.assertEqual(len(p), 2)
            self.assertTrue(hasattr(p[0], 'param1'))
            self.assertTrue(hasattr(p[0], 'param2'))
            self.assertEqual(p[0].param1, 1)
            self.assertEqual(p[0].param2, 2)
            self.assertEqual(p[1].param1, 'one')
            self.assertEqual(p[1].param2, 'param2')

            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters.json'])
            p = self.cdp_parser.get_other_parameters(default_vars=False)
            self.assertEqual(getattr(p[1], 'param2', None), None)

            self.cdp_parser.add_argument(
                '--param2',
                type=str,
                dest='param2',
                default='param2_cmd_default',
                required=False)

            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters.json'])
            p = self.cdp_parser.get_other_parameters(default_vars=False, cmd_default_vars=False)
            self.assertEqual(p[1].param1, 'one')
            self.assertEqual(getattr(p[1], 'param2', None), None)

            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters.json'])
            p = self.cdp_parser.get_other_parameters(default_vars=False, cmd_default_vars=True)
            self.assertEqual(p[1].param2, 'param2_cmd_default')
            self.cdp_parser.add_args_and_values(['-d', 'test_get_other_parameters.json', '--param2', 'new_param2'])
            # when mixing and matching any two of the three input options(*py, *cfg/*json, cmdline args),
            # you must use CDPParser.get_parameters()
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=True)
            self.assertEqual(p[1].param2, 'new_param2')

        finally:
            if os.path.exists('test_get_other_parameters.json'):
                os.remove('test_get_other_parameters.json')

    def test_get_cmdline_parameters(self):
        self.cdp_parser.add_argument(
            '--default_val',
            type=str,
            dest='default_val',
            default='default_val',
            required=False)

        self.cdp_parser.add_args_and_values(['-v', 'v1', 'v2', 'v3'])
        params = self.cdp_parser.get_cmdline_parameters()
        params2 = self.cdp_parser.get_parameter()
        self.assertEqual(params.vars, ['v1', 'v2', 'v3'])
        self.assertEqual(params2.vars, ['v1', 'v2', 'v3'])
        self.assertEqual(params.default_val, 'default_val')

        # default_vars=True, check_values=True, cmd_default_vars=True
        # testing cmd_default_vars=False
        params = self.cdp_parser.get_cmdline_parameters(cmd_default_vars=False)
        self.assertEqual(getattr(params, 'default_val', None), None)

        # testing default_vars=True and cmd_default_vars=False
        self.cdp_parser.add_args_and_values(['--default_val', 'cmdline_val'])
        params = self.cdp_parser.get_cmdline_parameters(cmd_default_vars=False)
        self.assertEqual(params.vars, ['default_vars'])

        # testing default_vars=False and cmd_default_vars=False
        self.cdp_parser.add_args_and_values(['--default_val', 'cmdline_val'])
        params = self.cdp_parser.get_cmdline_parameters(default_vars=False, cmd_default_vars=False)
        self.assertEqual(getattr(params, 'vars', None), None)

    def test__were_cmdline_args_used(self):
        cfg_str = '[Diags1]\n' 
        cfg_str += "num = 5\n"

        try:
            self.write_file('test__were_cmdline_args_used.cfg', cfg_str)
            self.cdp_parser.add_args_and_values(['-d', 'test__were_cmdline_args_used.cfg'])
            self.assertFalse(self.cdp_parser._were_cmdline_args_used())

            self.cdp_parser.add_args_and_values(['-d', 'test__were_cmdline_args_used.cfg', '-v', 'v1'])
            self.assertTrue(self.cdp_parser._were_cmdline_args_used())
            self.cdp_parser.add_args_and_values(['-v', 'v1'])
            self.assertTrue(self.cdp_parser._were_cmdline_args_used())

        finally:
            if os.path.exists('test__were_cmdline_args_used.cfg'):
                os.remove('test__were_cmdline_args_used.cfg')

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
        cfg_str += "vars = ['v2']\n"

        try:
            self.write_file('test_get_parameters.cfg', cfg_str)
                        
            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py'])
            p = self.cdp_parser.get_parameters()[0]
            self.assertEqual(p.num, 10)
            self.assertEqual(p.other_num, 11)
            self.assertEqual(p.vars, ['v1'])
            
            self.cdp_parser.add_args_and_values(['-d', 'test_get_parameters.cfg'])
            p = self.cdp_parser.get_parameters()[0]
            self.assertEqual(p.num, 5)
            self.assertEqual(p.vars, ['v2'])

            self.cdp_parser.add_args_and_values(['-v', 'v3'])
            p = self.cdp_parser.get_parameters()[0]
            self.assertEqual(p.vars, ['v3'])

            # testing vars_to_ignore
            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py', '-d', 'test_get_parameters.cfg'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False)[0]
            self.assertEqual(p.vars, ['v1'])
            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py', '-d', 'test_get_parameters.cfg'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False, vars_to_ignore=['vars'])[0]
            self.assertEqual(p.vars, ['v2'])

            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py', '-v', 'v3'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False)[0]
            self.assertEqual(p.vars, ['v3'])
            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py', '-v', 'v3'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False, vars_to_ignore=['vars'])[0]
            self.assertEqual(p.vars, ['v1'])

            self.cdp_parser.add_args_and_values(['-d', 'test_get_parameters.cfg', '-v', 'v3'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False)[0]
            self.assertEqual(p.vars, ['v3'])
            self.cdp_parser.add_args_and_values(['-d', 'test_get_parameters.cfg', '-v', 'v3'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False, vars_to_ignore=['vars'])[0]
            self.assertEqual(p.vars, ['v2'])

            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py', '-d', 'test_get_parameters.cfg', '-v', 'v3'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False)[0]
            self.assertEqual(p.vars, ['v3'])
            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_get_parameters.py', '-d', 'test_get_parameters.cfg', '-v', 'v3'])
            p = self.cdp_parser.get_parameters(default_vars=False, cmd_default_vars=False, vars_to_ignore=['vars'])[0]
            self.assertEqual(p.vars, ['v2'])

        finally:
            if os.path.exists('test_get_parameters.cfg'):
                os.remove('test_get_parameters.cfg')

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
            self.write_file('test_get_other_parameters_with_file_paths.py', py_str)

            # This is called when by the user when a cdp parser is initialized,
            # so we have do to this here.
            self.cdp_parser.add_args_and_values(['-p', 'test_get_other_parameters_with_file_paths.py'])

            files = ['test_get_other_parameters_with_file_paths1.cfg', 'test_get_other_parameters_with_file_paths2.cfg']
            params = self.cdp_parser.get_other_parameters(files_to_open=files)
            self.assertEqual(len(params), 3)

            for p in params:
                if p.num not in [0, 1, 2]:
                    self.fail('get_other_parameters() did not correctly get the jsons')

        finally:
            if os.path.exists('test_get_other_parameters_with_file_paths.py'):
                os.remove('test_get_other_parameters_with_file_paths.py')
            if os.path.exists('test_get_other_parameters_with_file_paths1.cfg'):
                os.remove('test_get_other_parameters_with_file_paths1.cfg')
            if os.path.exists('test_get_other_parameters_with_file_paths2.cfg'):
                os.remove('test_get_other_parameters_with_file_paths2.cfg')

    def test__is_arg_default_value(self):
        self.cdp_parser.add_argument(
            '--dv',
            type=str,
            dest='default_val',
            default='default_val',
            required=False)

        self.cdp_parser.add_argument(
                '--ndv',
                type=str,
                dest='no_default_val',
                required=False)
        
        cfg_str = '[Diags1]\n'
        cfg_str += "num = 0\n"

        try:
            self.write_file('test__is_arg_default_value.cfg', cfg_str)

            self.cdp_parser.add_args_and_values(['-d', 'test__is_arg_default_value.cfg'])
            self.assertTrue(self.cdp_parser._is_arg_default_value('default_val'))
            self.assertTrue(self.cdp_parser._is_arg_default_value('no_default_val'))

            self.cdp_parser.add_args_and_values(['--dv', 'cmdline_default_val'])
            self.assertFalse(self.cdp_parser._is_arg_default_value('default_val'))
            self.assertTrue(self.cdp_parser._is_arg_default_value('no_default_val'))

            self.cdp_parser.add_args_and_values(['--ndv', 'cmdline_no_default_val'])
            self.assertTrue(self.cdp_parser._is_arg_default_value('default_val'))
            self.assertFalse(self.cdp_parser._is_arg_default_value('no_default_val'))

            self.cdp_parser.add_args_and_values(['--dv', 'cmdline_default_val', '--ndv', 'cmdline_no_default_val'])
            self.assertFalse(self.cdp_parser._is_arg_default_value('default_val'))
            self.assertFalse(self.cdp_parser._is_arg_default_value('no_default_val'))

        finally:
            if os.path.exists('test__is_arg_default_value.py'):
                os.remove('test__is_arg_default_value.py')

    def test_cmdline_args_with_default_values(self):
        self.cdp_parser.add_argument(
                '--default_val',
                type=str,
                dest='default_val',
                default='default_val',
                required=False)

        self.cdp_parser.add_argument(
                '--no_default_val',
                type=str,
                dest='no_default_val',
                required=False)

        # py_str1 = 'something_else = 10\n'
        # py_str2 = "default_val = 'default_val_from_py'"

        try:
            # self.write_file('test_cmdline_args_with_default_values.py', py_str1)
            # self.write_file('test_cmdline_args_with_default_values2.py', py_str2)

            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_cmdline_args_with_default_values.py'])
            params = self.cdp_parser.get_parameter()
            self.assertEqual(params.default_val, 'default_val')
            self.assertEqual(params.no_default_val, None)

            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_cmdline_args_with_default_values.py', '--default_val', 'new_default_val'])
            params = self.cdp_parser.get_parameter()
            self.assertEqual(params.default_val, 'new_default_val')
            self.assertEqual(params.no_default_val, None)

            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_cmdline_args_with_default_values2.py'])
            params = self.cdp_parser.get_parameter()
            self.assertEqual(params.default_val, 'default_val_from_py')
            self.assertEqual(params.no_default_val, None)

            self.cdp_parser.add_args_and_values(['-p', self.prefix + 'test_cmdline_args_with_default_values2.py', '--default_val', 'new_default_val', '--no_default_val', 'new_no_default_val'])
            params = self.cdp_parser.get_parameter()
            self.assertEqual(params.default_val, 'new_default_val')
            self.assertEqual(params.no_default_val, 'new_no_default_val')

        finally:
            # if os.path.exists('test_cmdline_args_with_default_values.py'):
            #    os.remove('test_cmdline_args_with_default_values.py')
            # if os.path.exists('test_cmdline_args_with_default_values2.py'):
            #    os.remove('test_cmdline_args_with_default_values2.py')
            pass
    
    def test_without_any_params(self):
            self.cdp_parser.add_argument(
                '--param1',
                type=str,
                dest='param1',
                default='param1_cmd_default',
                required=False)

            self.cdp_parser.add_argument(
                '--new_param',
                type=str,
                dest='new_param',
                default='new_param_cmd_default',
                required=False)

            # params should only have the defaults from the command line parser
            # only vars and param1 are in the command line parser, make sure that param2 didn't show up
            self.cdp_parser.add_args_and_values('')
            params = self.cdp_parser.get_parameter()
            self.assertTrue(hasattr(params, 'vars')) 
            self.assertTrue(hasattr(params, 'param1'))
            self.assertTrue(hasattr(params, 'new_param'))
            self.assertTrue(hasattr(params, 'param2'))
            self.assertEqual(params.vars, None)
            self.assertEqual(params.param1, 'param1_cmd_default')
            self.assertEqual(params.new_param, 'new_param_cmd_default')
            self.assertEqual(params.param2, 'param2')

            self.cdp_parser.add_args_and_values('')
            params = self.cdp_parser.get_parameter(cmd_default_vars=False)
            self.assertTrue(hasattr(params, 'vars')) 
            self.assertTrue(hasattr(params, 'param1'))
            self.assertTrue(hasattr(params, 'param2'))
            self.assertFalse(hasattr(params, 'new_param'))
            self.assertEqual(params.vars, ['default_vars'])
            self.assertEqual(params.param1, 'param1')
            self.assertEqual(params.param2, 'param2')

    def test_granulate(self):
        cfg_str = '[Diags1]\n'
        cfg_str += "nums = [0, 1]\n"
        cfg_str += "letters = [A, B, C]\n"
        cfg_str += "faces = [':)']\n"
        cfg_str += "dont_granulate = ['dont', 'granulate', 'this']\n"
        cfg_str += "info = 'This is some information.'\n"
        cfg_str += "empty=[]\n"
        cfg_str += "granulate = [nums, letters, faces, empty]\n"

        try:
            self.write_file('test_granulate.cfg', cfg_str)
            self.cdp_parser.add_args_and_values(['-d', 'test_granulate.cfg'])
            params = self.cdp_parser.get_parameters()
            
            self.assertEqual(len(params), 6)
            self.assertEqual(getattr(params[0], 'nums'), [0])
            self.assertEqual(getattr(params[0], 'letters'), ['A'])
            self.assertEqual(getattr(params[1], 'nums'), [0])
            self.assertEqual(getattr(params[1], 'letters'), ['B'])
            self.assertEqual(getattr(params[2], 'nums'), [0])
            self.assertEqual(getattr(params[2], 'letters'), ['C'])
            self.assertEqual(getattr(params[3], 'nums'), [1])
            self.assertEqual(getattr(params[3], 'letters'), ['A'])
            self.assertEqual(getattr(params[4], 'nums'), [1])
            self.assertEqual(getattr(params[4], 'letters'), ['B'])
            self.assertEqual(getattr(params[5], 'nums'), [1])
            self.assertEqual(getattr(params[5], 'letters'), ['C'])

            for p in params:
                self.assertEqual(getattr(p, 'faces'), [':)'])
                self.assertEqual(getattr(p, 'dont_granulate'), ['dont', 'granulate', 'this'])
                self.assertEqual(getattr(p, 'info'), 'This is some information.')
                self.assertEqual(getattr(p, 'granulate'), ['nums', 'letters', 'faces', 'empty'])

        finally:
            if os.path.exists('test_granulate.cfg'):
                os.remove('test_granulate.cfg')

    def test_cfg_hash(self):
        cfg_str = '[#]\n'
        cfg_str += '[#]\n'
        cfg_str += "num = 0\n"
        cfg_str += '[#]\n'
        cfg_str += "num = 0\n"
        cfg_str += "num1 = 1\n"
        cfg_str += '[Diags1]\n'
        cfg_str += "num = 0\n"
        cfg_str += "num = 0\n"
        cfg_str += '[#]\n'
        cfg_str += "num = 0\n"
        cfg_str += "num1 = 1\n"
        cfg_str += '[#]'

        try:
            self.write_file('test_cfg_hash.cfg', cfg_str)
            self.cdp_parser.add_args_and_values(['-d', 'test_cfg_hash.cfg'])
            params = self.cdp_parser.get_parameters()
            self.assertEqual(len(params), 6)
            self.assertEqual(getattr(params[1], 'num'), 0)
            self.assertEqual(getattr(params[2], 'num'), 0)
            self.assertEqual(getattr(params[2], 'num1'), 1)
            self.assertEqual(getattr(params[3], 'num'), 0)
            self.assertEqual(getattr(params[4], 'num'), 0)
            self.assertEqual(getattr(params[4], 'num1'), 1)

        finally:
            if os.path.exists('test_cfg_hash.cfg'):
                os.remove('test_cfg_hash.cfg')
        
if __name__ == '__main__':
    unittest.main()
