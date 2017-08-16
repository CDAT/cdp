from __future__ import print_function

import unittest
import os
import cdp.cdp_parameter
import cdp.cdp_parser
import cdp.cdp_run


class MyCDPParameter(cdp.cdp_parameter.CDPParameter):
    def check_values(self):
        pass


class MyCDPParser(cdp.cdp_parser.CDPParser):
    def __init__(self, *args, **kwargs):
        super(MyCDPParser, self).__init__(
            MyCDPParameter, *args, **kwargs)

    def load_default_args(self):
        super(MyCDPParser, self).load_default_args()
        self.add_argument(
            '-v', '--vars',
            type=str,
            nargs='+',
            dest='vars',
            help='Variables to use',
            required=False)


class TestCDPRun(unittest.TestCase):

    def write_file(self, file_name, contents):
        f = open(file_name, 'w')
        f.write(contents)
        f.close()

    def setUp(self):
        self.cdp_parser = MyCDPParser()

        self.py_str = 'num = 1\n'

        self.cfg_str = '[Diags1]\n'
        self.cfg_str += "num = 5\n"
        self.cfg_str += '[Diags2]\n'
        self.cfg_str += "num = 10\n"
        self.cfg_str += '[Diags3]\n'
        self.cfg_str += "num = 15\n"
        self.cfg_str += '[Diags4]\n'
        self.cfg_str += "num = 20\n"


    def test_serial(self):

        def func(params):
            num = params.num

        try:
            self.write_file('params.py', self.py_str)
            self.write_file('diags.cfg', self.cfg_str)

            self.cdp_parser.add_args_and_values(['-p', 'params.py', '-d', 'diags.cfg'])
            params = self.cdp_parser.get_parameters()

            cdp.cdp_run.serial(func, params)

        except Exception as e:
            print(e)
            self.fail('cdp.cdp_run.serial() failed')

        finally:
            if os.path.exists('params.py'):
                os.remove('params.py')
            if os.path.exists('diags.cfg'):
                os.remove('diags.cfg')

    '''
    def test_multiprocess(self):

        def func(params):
            pass

        try:
            self.write_file('params.py', self.py_str)
            self.write_file('diags.cfg', self.cfg_str)

            self.cdp_parser.add_args_and_values(['-p', 'params.py', '-d', 'diags.cfg'])
            params = self.cdp_parser.get_parameters()
            # import pickle
            # for p in params:
            #     pickle.dump(p, open("shit.p", "wb"))

            # cdp.cdp_run.multiprocess(func, params)
        
        finally:
            if os.path.exists('params.py'):
                os.remove('params.py')
            if os.path.exists('diags.cfg'):
                os.remove('diags.cfg')

    def test_distribute(self):
        # scheduler and workers need to be able to start from cdp.cdp_run.distribute()
        # this isn't a thing as of now

        def func(params):
            pass

        try:
            py_str = self.py_str + 'scheduler_addr="127.0.0.1:8786"'
            self.write_file('params.py', py_str)
            self.write_file('diags.cfg', self.cfg_str)

            self.cdp_parser.add_args_and_values(['-p', 'params.py', '-d', 'diags.cfg'])
            params = self.cdp_parser.get_parameters()

            cdp.cdp_run.distribute(func, params)
        
        finally:
            if os.path.exists('params.py'):
                os.remove('params.py')
            if os.path.exists('diags.cfg'):
                os.remove('diags.cfg')
    '''

if __name__ == '__main__':
    unittest.main()
