from __future__ import print_function

import sys
import argparse
import abc
import json
import yaml
import warnings
from six import with_metaclass
import ast

if sys.version_info[0] >= 3:
    import configparser
else:
    import ConfigParser as configparser


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

    def _is_arg_default_value(self, arg):
        """
        Look at the command used for this parser (ex: test.py -s something --s1 something1)
        and if arg wasn't used, then it's a default value.
        """
        # each cmdline_arg is either '-*' or '--*'.
        for cmdline_arg in self._option_string_actions:
            # self.cmd_used is like: ['something.py', '-p', 'test.py', '--s1', 'something']
            if arg == self._option_string_actions[cmdline_arg].dest and cmdline_arg in self.cmd_used:
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

    def get_orig_parameters(self, default_vars=True, check_values=True, cmd_default_vars=True):
        """Returns the parameters created by -p. If -p wasn't used, returns None."""
        self._parse_arguments()
        
        if not self.__args_namespace.parameters:
            return None

        parameter = self.__parameter_cls()

        if not default_vars:  # remove all of the variables
            parameter.__dict__.clear()

        # if self.__args_namespace.parameters is not None:
        parameter.load_parameter_from_py(
            self.__args_namespace.parameters)

        if cmd_default_vars:
            self._get_default_from_cmdline(parameter)

        if check_values:
            parameter.check_values()

        return parameter

    def get_parameters_from_json(self, json_file, default_vars=True, check_values=True, cmd_default_vars=True):
        """Given a json file, return the parameters from it."""
        with open(json_file) as f:
            json_data = json.loads(f.read())

        parameters = []
        for key in json_data:
            for single_run in json_data[key]:
                p = self.__parameter_cls()

                if not default_vars:  # remove all of the variables
                    p.__dict__.clear()

                for attr_name in single_run:
                    setattr(p, attr_name, single_run[attr_name])

                if cmd_default_vars:
                    self._get_default_from_cmdline(p)

                if check_values:
                    p.check_values()

                parameters.append(p)

        return parameters

    def get_parameters_from_cfg(self, json_file, default_vars=True, check_values=True, cmd_default_vars=True):
        """Given a cfg file, return the parameters from it."""
        parameters = []

        config = configparser.ConfigParser()
        config.read(json_file)

        for section in config.sections():
            p = self.__parameter_cls()

            if not default_vars:  # remove all of the variables
                p.__dict__.clear()

            for k, v in config.items(section):
                v = yaml.safe_load(v)
                setattr(p, k, v)

            if cmd_default_vars:
                self._get_default_from_cmdline(p)

            if check_values:
                p.check_values()

            parameters.append(p)

        return parameters

    def get_other_parameters(self, files_to_open=[], default_vars=True, check_values=True, cmd_default_vars=True):
        """Returns the parameters created by -d, If files_to_open is defined, 
        then use the path specified instead of -d"""
        parameters = []
    
        self._parse_arguments()

        if files_to_open == []:
            files_to_open = self.__args_namespace.other_parameters

        if files_to_open is not None:
            for diags_file in files_to_open:
                if '.json' in diags_file:
                    params = self.get_parameters_from_json(diags_file, default_vars, check_values, cmd_default_vars)
                elif '.cfg' in diags_file:
                    params = self.get_parameters_from_cfg(diags_file, default_vars, check_values, cmd_default_vars)
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

    def _overwrite_parameters_with_cmdline_args(self, parameters, cmd_default_vars=True):
        """
        Overwrite the parameters with the user's command line arguments.
        Case 1: No param in parameters, use what's in --param. Even if cmdline arg (--param) is a default argument.
        Case 2: When there's a param in parameters and --param is given, use cmdline arg, but only if it's NOT a default value.

        So the only use of the default in a cmdline arg is when there's nothing for it in parameters.
        """
        for arg_name, arg_value in vars(self.__args_namespace).items():
            if not cmd_default_vars and self._is_arg_default_value(arg_name):
                continue

            # Case 1
            if not hasattr(parameters, arg_name):
                setattr(parameters, arg_name, arg_value)
            # Case 2
            if hasattr(parameters, arg_name) and not self._is_arg_default_value(arg_name):
                setattr(parameters, arg_name, arg_value)

    def get_cmdline_parameters(self, default_vars=True, check_values=False, cmd_default_vars=True):
        """
        Use the other command line args besides -p and -d to create a single parameters object.
        cmd_default_vars is used to see if the `default` option in ArgumentParser.add_argument() should be used.
        """
        self._parse_arguments()

        if not self._were_cmdline_args_used():
            return None 

        parameter = self.__parameter_cls()

        if not default_vars:  # remove all of the variables
            parameter.__dict__.clear()

        self._overwrite_parameters_with_cmdline_args(parameter, cmd_default_vars)

        if check_values:
            parameter.check_values()

        return parameter

    def combine_params(self, cmdline_parameters=None, orig_parameters=None, other_parameters=None, vars_to_ignore=[]):
        """Combine cmdline_params (-* or --*), orig_parameters (-p), and other_parameters (-d), while ignoring vars_to_ignore"""
        if other_parameters:
            for parameters in other_parameters:
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

        # might just combine cmdline_params with orig_params
        elif not other_parameters and orig_parameters and cmdline_parameters:
            for var in cmdline_parameters.__dict__:
                if var not in vars_to_ignore:
                    orig_parameters.__dict__[var] = cmdline_parameters.__dict__[var]

    def combine_orig_and_other_params(self, orig_parameters, other_parameters, vars_to_ignore=[]):
        """Combine orig_parameters with all of the other_parameters, while ignoring vars_to_ignore"""
        print('Deprication warning: please use combine_params() instead')
        self.combine_params(None, orig_parameters, other_parameters, vars_to_ignore)

    def get_parameters(self, cmdline_parameters=None, orig_parameters=None, other_parameters=[], vars_to_ignore=[], *args, **kwargs):
        """Get the parameters based on the command line arguments and return a list of them."""
        if not cmdline_parameters:
            cmdline_parameters = self.get_cmdline_parameters(*args, **kwargs)
        if not orig_parameters:
            orig_parameters = self.get_orig_parameters(*args, **kwargs)
        if other_parameters == []:
            other_parameters = self.get_other_parameters(*args, **kwargs)

        self.combine_params(cmdline_parameters, orig_parameters, other_parameters, vars_to_ignore)

        if other_parameters != []:
            return other_parameters
        elif orig_parameters:
            return [orig_parameters]
        else:
            return [cmdline_parameters]

    def get_parameter(self, warning=False, *args, **kwargs):
        """Return the first Parameter in the list of Parameters."""
        if warning:
            print(
                'Deprecation warning: Use get_parameters() instead, which returns a list of Parameters.')
        return self.get_parameters(*args, **kwargs)[0]

    def load_default_args_from_json(self, files):
        """ take in a list of json files (or a single json file) and create the args from it"""
        if not isinstance(files, (list, tuple)):
            files = [files]
        success = None
        for afile in files:
            with open(afile) as json_file:
                args = json.load(json_file)
                for k in args.keys():
                    if k[0] != "-":
                        continue
                    # try:
                    if 1:
                        params = args[k]
                        option_strings = params.pop("aliases", [])
                        option_strings.insert(0, k)
                        params["type"] = eval(params.pop("type", "str"))
                        self.store_default_arguments(option_strings, params)
                        success = True
                    # except:
                    #    warnings.warn("failed to load param {} from json file {}".format(
                    #        k,afile))
                    #    pass
        return success

    def store_default_arguments(self, options, params):
        self.__default_args.append([options, params])

    def print_available_defaults(self):
        p = argparse.ArgumentParser()
        for opt, param in self.__default_args:
            p.add_argument(*opt, **params)
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

    def add_args_and_values(self, arg_list):
        """Used for testing. Can test args input as if they
        were inputted from the command line."""
        self.__args_namespace = self.parse_args(arg_list)
