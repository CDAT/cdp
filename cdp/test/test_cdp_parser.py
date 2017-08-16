import unittest
import os
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

    def test_load_default_args(self):
        try:
            self.write_file('param_file.py', 'vars=["v1", "v2"]\n')
            self.cdp_parser.add_args_and_values(['-p', 'param_file.py'])
            p = self.cdp_parser.get_orig_parameters()
            self.assertTrue(hasattr(p, 'vars'))
            self.assertEquals(p.vars, ['v1', 'v2'])
        except Exception as e:
            print(e)
            self.fail('Failed to load a parameter with -p.')
        finally:
            if os.path.exists('diags.json'):
                os.remove('param_file.py')

    def test_load_custom_args(self):
        try:
            self.cdp_parser.add_args_and_values(['-v', 'v1', 'v2'])
        except Exception as e:
            print(e)
            self.fail('Failed to load variables with -v.')

    def test_get_orig_parameters_with_cmdline_args(self):
        self.cdp_parser.add_args_and_values(['-v', 'v1', 'v2'])
        p = self.cdp_parser.get_orig_parameters()
        self.assertTrue(hasattr(p, 'vars'))
        self.assertEquals(p.vars, ['v1', 'v2'])
    
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
            self.write_file('diags.json', json_str)
            self.cdp_parser.add_args_and_values(['-d', 'diags.json'])
            p = self.cdp_parser.get_other_parameters()

            self.assertEquals(len(p), 2)
            self.assertTrue(hasattr(p[0], 'param1'))
            self.assertTrue(hasattr(p[0], 'param2'))
            self.assertEquals(p[0].param1, 1)
            self.assertEquals(p[0].param2, 2)
            self.assertEquals(p[1].param1, 'one')
            self.assertEquals(p[1].param2, 'two')

        finally:
            if os.path.exists('diags.json'):
                os.remove('diags.json')
        
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
            self.write_file('diags.json', json_str)
            self.write_file('diags1.json', json_str)
            self.cdp_parser.add_args_and_values(['-d', 'diags.json', 'diags1.json'])
            p = self.cdp_parser.get_other_parameters()

            self.assertEquals(len(p), 4)

        finally:
            if os.path.exists('diags.json'):
                os.remove('diags.json')
            if os.path.exists('diags1.json'):
                os.remove('diags1.json')

if __name__ == '__main__':
    unittest.main()
