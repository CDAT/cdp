from __future__ import print_function

import sys
import argparse
import abc
import json
import yaml
import warnings
import ast
import itertools
import collections
import copy
import random
import hashlib
from six import with_metaclass

if sys.version_info[0] >= 3:
    import configparser
    from io import StringIO
else:
    import ConfigParser as configparser
    from StringIO import StringIO


class CDPParser(argparse.ArgumentParser):
    def __init__(self, parameter_cls=None, default_args_file=[], *args, **kwargs):
        # conflict_handler='resolve' lets new args override older ones
        self.__default_args = []
        super(CDPParser, self).__init__(conflict_handler='resolve',
                                        *args, **kwargs)
        self.load_default_args(default_args_file)
        self.__args_namespace = None
        self.__parameter_cls = parameter_cls
        
        if not self.__parameter_cls:
            from cdp.cdp_parameter import CDPParameter
            self.__parameter_cls = CDPParameter

    def parse_args(self, args=None, namespace=None):
        """
        Overwrites default ArgumentParser.parse_args().
        We need to save the command used to run the parser, which is args or sys.argv.
        This is because the command used is not always sys.argv.
        """
        self.cmd_used = sys.argv if not args else args
        return super(CDPParser, self).parse_args(args, namespace)

    def view_args(self):
        """Returns the args namespace"""
        self._parse_arguments()
        return self.__args_namespace

    def _was_command_used(self, cmdline_arg):
        """Returns True if the cmdline_arg was used to
        run the script that has this parser."""
        # self.cmd_used is like: ['something.py', '-p', 'test.py', '--s1', 'something']
        for cmd in self.cmd_used:
            # Sometimes, a command is run with '=': 'driver.py --something=this'
            for c in cmd.split('='):
                if cmdline_arg == c:
                    return True
        return False

    def _is_arg_default_value(self, arg):
        """
        Look at the command used for this parser (ex: test.py -s something --s1 something1)
        and if arg wasn't used, then it's a default value.
        """
        # each cmdline_arg is either '-*' or '--*'.
        for cmdline_arg in self._option_string_actions:
            if arg == self._option_string_actions[cmdline_arg].dest and self._was_command_used(cmdline_arg):
                return False
        return True

    def _get_default_from_cmdline(self, parameters):
        """
        Get the default values from the command line and insert it into the parameters object,
        but only if that parameter is NOT already defined.
        """
        for arg_name, arg_value in vars(self.__args_namespace).items():
            if self._is_arg_default_value(arg_name) and not hasattr(parameters, arg_name):
                setattr(parameters, arg_name, arg_value)

    def _parse_arguments(self):
        """Parse the command line arguments while checking for the user's arguments"""
        if self.__args_namespace is None:
            self.__args_namespace = self.parse_args()            

    def get_orig_parameters(self, check_values=False):
        """Returns the parameters created by -p. If -p wasn't used, returns None."""
        self._parse_arguments()
        
        if not self.__args_namespace.parameters:
            return None

        parameter = self.__parameter_cls()

        # remove all of the variables
        parameter.__dict__.clear()

        # if self.__args_namespace.parameters is not None:
        parameter.load_parameter_from_py(
            self.__args_namespace.parameters)

        if check_values:
            parameter.check_values()

        return parameter

    def get_parameters_from_json(self, json_file, check_values=False):
        """Given a json file, return the parameters from it."""
        with open(json_file) as f:
            json_data = json.loads(f.read())

        parameters = []
        for key in json_data:
            for single_run in json_data[key]:
                p = self.__parameter_cls()

                # remove all of the variables
                p.__dict__.clear()

                for attr_name in single_run:
                    setattr(p, attr_name, single_run[attr_name])

                if check_values:
                    p.check_values()

                parameters.append(p)

        return parameters

    def _create_cfg_hash_titles(self, cfg_file):
        """
        Given a path to a cfg file, for any title '[#]', create a hash of it's contents
        and change the title to that. Then return the StringIO object.
        """
        lines = []
        with open(cfg_file) as f:
            lines = f.readlines()

        h_sha256 = hashlib.sha256()
        i = 0
        
        while i < len(lines):
            if lines[i] in ['[#]\n', '[#]']:
                replace_idx = i
                str_list = []
                i += 1
                while i < len(lines) and not lines[i].startswith('['):
                    str_list.append(lines[i])
                    i += 1
                str_list.append(str(random.random()))  # randomize the hash even more
                h_sha256.update(''.join(str_list).encode())
                lines[replace_idx] = '[{}]'.format(h_sha256.hexdigest())
            else:
                i += 1
        return StringIO('\n'.join(lines))

    def get_parameters_from_cfg(self, cfg_file, check_values=False):
        """Given a cfg file, return the parameters from it."""
        parameters = []

        cfg_file_obj = self._create_cfg_hash_titles(cfg_file)
        kwargs = {'strict': False} if sys.version_info[0] >= 3 else {}  # strict keyword doesn't work in Python 2
        config = configparser.ConfigParser(**kwargs)  # Allow for two lines to be the same
        config.readfp(cfg_file_obj)

        for section in config.sections():
            p = self.__parameter_cls()

            # remove all of the variables
            p.__dict__.clear()

            for k, v in config.items(section):
                v = yaml.safe_load(v)
                setattr(p, k, v)

            if check_values:
                p.check_values()

            parameters.append(p)

        return parameters

    def get_other_parameters(self, files_to_open=[], check_values=False):
        """Returns the parameters created by -d, If files_to_open is defined, 
        then use the path specified instead of -d"""
        parameters = []
    
        self._parse_arguments()

        if files_to_open == []:
            files_to_open = self.__args_namespace.other_parameters

        if files_to_open is not None:
            for diags_file in files_to_open:
                if '.json' in diags_file:
                    params = self.get_parameters_from_json(diags_file, check_values)
                elif '.cfg' in diags_file:
                    params = self.get_parameters_from_cfg(diags_file, check_values)
                else:
                    raise RuntimeError(
                        'The parameters input file must be either a .json or .cfg file')

                for p in params:
                    parameters.append(p)

        return parameters

    def _were_cmdline_args_used(self):
        """
        Checks that other parameters, besides '-p' or '-d', were used 
        """
        for cmd in self.cmd_used:
            if cmd.startswith('-') and cmd not in ['-p', '--parameters', '-d', '--diags']:
                return True
        return False

    def _overwrite_parameters_with_cmdline_args(self, parameters):
        """
        Add the command line parameters used to the parameter object.
        """
        for arg_name, arg_value in vars(self.__args_namespace).items():
            if not self._is_arg_default_value(arg_name):
                setattr(parameters, arg_name, arg_value)

    def get_cmdline_parameters(self, check_values=False):
        """
        Use the other command line args besides -p and -d to create a single parameters object.
        """
        self._parse_arguments()

        if not self._were_cmdline_args_used():
            return None 

        parameter = self.__parameter_cls()

        # remove all of the variables
        parameter.__dict__.clear()

        self._overwrite_parameters_with_cmdline_args(parameter)

        if check_values:
            parameter.check_values()

        return parameter

    def _add_default_values(self, parameter, default_vars=False, cmd_default_vars=False):
        """
        Add the default values to the parameter.
        These can come from the default values defined in the Parameter class,
        or the `default` option defined in ArgumentParser.add_argument().
        """
        # Add the command line default parameters first
        if cmd_default_vars:
            for arg_name, arg_value in vars(self.__args_namespace).items():
                #print('examining (arg_name, arg_value): ({}, {})'.format(arg_name, arg_value))
                if arg_name in parameter.__dict__ or not self._is_arg_default_value(arg_name):
                    continue
                # Only add the default values, that aren't already in parameter.
                setattr(parameter, arg_name, arg_value)
        
        # Then add the defaults defined in the Parameter class
        if default_vars:
            for arg_name, arg_value in vars(self.__parameter_cls()).items(): 
                if arg_name in parameter.__dict__:
                    continue
                setattr(parameter, arg_name, arg_value)

    def combine_params(self, cmdline_parameters=None, orig_parameters=None, other_parameters=None, vars_to_ignore=[], default_vars=False, cmd_default_vars=False):
        """
        Combine cmdline_params (-* or --*), orig_parameters (-p), and other_parameters (-d),
        while ignoring vars_to_ignore.
        Add any default arguments here as well.
        """
        if other_parameters:
            for parameters in other_parameters:
                self._add_default_values(parameters, default_vars, cmd_default_vars)

                # orig_parameters args take precedence over other_parameters
                if orig_parameters:
                    for var in orig_parameters.__dict__:
                        if var not in vars_to_ignore:
                            parameters.__dict__[var] = orig_parameters.__dict__[var]

                # cmd_line args take the final precedence
                if cmdline_parameters:
                    for var in cmdline_parameters.__dict__:
                        if var not in vars_to_ignore:
                            parameters.__dict__[var] = cmdline_parameters.__dict__[var]

        else:
            # just combine cmdline_params with orig_params
            if orig_parameters and cmdline_parameters:
                self._add_default_values(orig_parameters, default_vars, cmd_default_vars)

                for var in cmdline_parameters.__dict__:
                    # if var not in vars_to_ignore and self._was_command_used(var):
                    if var not in vars_to_ignore:
                        # Only add it if it was not in param and was passed from cmd line
                        orig_parameters.__dict__[var] = cmdline_parameters.__dict__[var]

            elif orig_parameters:
                self._add_default_values(orig_parameters, default_vars, cmd_default_vars)
            elif cmdline_parameters:
                self._add_default_values(cmdline_parameters, default_vars, cmd_default_vars)

    def combine_orig_and_other_params(self, orig_parameters, other_parameters, vars_to_ignore=[]):
        """Combine orig_parameters with all of the other_parameters, while ignoring vars_to_ignore"""
        print('Depreciation warning: please use combine_params() instead')
        self.combine_params(None, orig_parameters, other_parameters, vars_to_ignore)

    def granulate(self, parameters):
        """
        Given a list of parameters objects, for each parameters with a `granulate` attribute,
        create multiple parameters objects for each result in the Cartesian product of `granulate`.
        """
        final_parameters = []
        for param in parameters:
            if not hasattr(param, 'granulate') or (hasattr(param, 'granulate') and not param.granulate):
                final_parameters.append(param)
                continue

            # granulate param
            vars_to_granulate = param.granulate  # ex: ['seasons', 'plevs']
            # check that all of the vars_to_granulate are iterables
            vals_to_granulate = []  # ex: [['ANN', 'DJF', 'MAM'], [850.0, 250.0]]
            for v in vars_to_granulate:
                if not hasattr(param, v):
                    raise RuntimeError("Parameters object has no attribute '{}' to granulate.".format(v))
                param_v = getattr(param, v)
                if not isinstance(param_v, collections.Iterable):
                    raise RuntimeError("granulate option '{}' is not an iterable.".format(v))
                if param_v:  # ignore [] 
                    vals_to_granulate.append(param_v)

            # ex: [('ANN', 850.0), ('ANN', 250.0), ('DJF', 850.0), ('DJF', 250.0), ...]
            granulate_values = list(itertools.product(*vals_to_granulate))
            for g_vals in granulate_values:
                p = copy.deepcopy(param)
                for i, g_val in enumerate(g_vals):
                    # Make sure to insert a list with one element
                    setattr(p, vars_to_granulate[i], [g_val])
                final_parameters.append(p)

        return final_parameters

    def get_parameters(self, cmdline_parameters=None, orig_parameters=None, other_parameters=[], vars_to_ignore=[], default_vars=True, cmd_default_vars=True, *args, **kwargs):
        """Get the parameters based on the command line arguments and return a list of them."""
        if not cmdline_parameters:
            cmdline_parameters = self.get_cmdline_parameters(*args, **kwargs)
        if not orig_parameters:
            orig_parameters = self.get_orig_parameters(*args, **kwargs)
        if other_parameters == []:
            other_parameters = self.get_other_parameters(*args, **kwargs)
        self.combine_params(cmdline_parameters, orig_parameters, other_parameters, vars_to_ignore, default_vars, cmd_default_vars)

        if other_parameters != []:
            return self.granulate(other_parameters)
        elif orig_parameters:
            return self.granulate([orig_parameters])
        elif cmdline_parameters:
            return self.granulate([cmdline_parameters])

        # user didn't give any command line options, so create a parameter from the
        # defaults of the command line argument or the Parameter class.
        elif cmd_default_vars:
            p = self.__parameter_cls()
            for arg_name, arg_value in vars(self.__args_namespace).items():
                setattr(p, arg_name, arg_value)
            return self.granulate([p])
        elif default_vars:
            p = self.__parameter_cls()
            return self.granulate([p])

    def get_parameter(self, warning=False, *args, **kwargs):
        """Return the first Parameter in the list of Parameters."""
        if warning:
            print(
                'Depreciation warning: Use get_parameters() instead, which returns a list of Parameters.')
        return self.get_parameters(*args, **kwargs)[0]

    def load_default_args_from_json(self, files):
        """Take in a list of json files (or a single json file) and create the args from it."""
        if not isinstance(files, (list, tuple)):
            files = [files]
        success = None
        for afile in files:
            with open(afile) as json_file:
                args = json.load(json_file)
                for k in args.keys():
                    if k[0] != "-":
                        continue
                    try:
                        params = args[k]
                        option_strings = params.pop("aliases", [])
                        option_strings.insert(0, k)
                        # Sometime we can't set a type
                        # like action="store_true"
                        # setting it to null in json file
                        # leads to exception in eval
                        # hence not setting it
                        try:
                            params["type"] = eval(params.pop("type", "str"))
                        except:
                            pass
                        self.store_default_arguments(option_strings, params)
                        success = True
                    except:
                       warnings.warn("Failed to load param {} from json file {}".format(
                           k, afile))

        return success

    def store_default_arguments(self, options, params):
        self.__default_args.insert(0,([options, params]))

    def print_available_defaults(self):
        p = argparse.ArgumentParser()
        for opt, param in self.__default_args:
            p.add_argument(*opt, **param)
        p.print_help()

    def available_defaults(self):
        return [x[0] for x in self.__default_args]

    def use(self, options):
        if not isinstance(options, (list, tuple)):
            options = [options]
        for option in options:
            match = False
            for opts, params in self.__default_args:
                if option in opts:
                    match = True
                    break
                elif option[0] != "--" and "--" + option in opts:
                    match = True
                    break
                elif option[0] != "-" and "-" + option in opts:
                    match = True
                    break
            if match:
                self.add_argument(*opts, **params)
            else:
                raise RuntimeError(
                    "could not match {} to any of the default arguments {}".format(
                        option, self.available_defaults))

    def load_default_args(self, files=[]):
        """Load the default arguments for the parser."""
        if self.load_default_args_from_json(files):
            return
        self.add_argument(
            '-p', '--parameters',
            type=str,
            dest='parameters',
            help='Path to the user-defined parameter file.',
            required=False)
        self.add_argument(
            '-d', '--diags',
            type=str,
            nargs='+',
            dest='other_parameters',
            default=[],
            help='Path to the other user-defined parameter file.',
            required=False)
        self.add_argument(
            '-n', '--num_workers',
            type=int,
            dest='num_workers',
            help='Number of workers, used when running with multiprocessing or in distributed mode.',
            required=False)
        self.add_argument(
            '--scheduler_addr',
            type=str,
            dest='scheduler_addr',
            help='Address of the scheduler in the form of IP_ADDRESS:PORT. Used when running in distributed mode.',
            required=False)
        self.add_argument(
            '-g', '--granulate',
            type=str,
            nargs='+',
            dest='granulate',
            help='A list of variables to granulate.',
            required=False)

    def add_args_and_values(self, arg_list):
        """Used for testing. Can test args input as if they
        were inputted from the command line."""
        self.__args_namespace = self.parse_args(arg_list)
