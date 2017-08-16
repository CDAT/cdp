from __future__ import print_function

import argparse
import abc
import json
import ConfigParser
import yaml


class CDPParser(argparse.ArgumentParser):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parameter_cls, *args, **kwargs):
        # conflict_handler='resolve' lets new args override older ones
        super(CDPParser, self).__init__(conflict_handler='resolve',
                                        *args, **kwargs)
        self.load_default_args()
        self.__parameter_cls = parameter_cls
        self.__args_namespace = None

    def overwrite_parameters_with_cmdline_args(self, parameters):
        """Overwrite the parameters with the user's command line arguments."""
        for arg_name, arg_value in vars(self.__args_namespace).iteritems():
            if arg_value is not None:
                # Add it to the parameter
                setattr(parameters, arg_name, arg_value)

    def get_orig_parameters(self, default_vars=True, check_values=True):
        """Returns the parameters created by -p"""
        parameter = self.__parameter_cls()

        if self.__args_namespace is None:
            self.__args_namespace = self.parse_args()

        if not default_vars:  # remove all of the variables
            parameter.__dict__.clear()

        if self.__args_namespace.parameters is not None:
            parameter.load_parameter_from_py(
                self.__args_namespace.parameters)

        for arg_name, arg_value in vars(self.__args_namespace).iteritems():
            if arg_value is not None:
                # Add it to the parameter
                setattr(parameter, arg_name, arg_value)

        if check_values:
            parameter.check_values()

        return parameter

    def get_parameters_from_json(self, json_file, default_vars=True, check_values=True):
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

                self.overwrite_parameters_with_cmdline_args(p)

                if check_values:
                    p.check_values()

                parameters.append(p)

        return parameters

    def get_parameters_from_cfg(self, json_file, default_vars=True, check_values=True):
        """Given a cfg file, return the parameters from it."""
        parameters = []

        config = ConfigParser.ConfigParser()
        config.read(json_file)

        for section in config.sections():
            p = self.__parameter_cls()

            if not default_vars:  # remove all of the variables
                p.__dict__.clear()

            for k, v in config.items(section):
                v = yaml.safe_load(v)
                setattr(p, k, v)

            self.overwrite_parameters_with_cmdline_args(p)

            if check_values:
                p.check_values()

            parameters.append(p)

        return parameters

    def get_other_parameters(self, files_to_open=[], default_vars=True, check_values=True):
        """Returns the parameters created by -d, If files_to_open is defined, 
        then use the path specified instead of -d"""
        parameters = []
    
        if self.__args_namespace is None:
            self.__args_namespace = self.parse_args()

        if files_to_open == []:
            files_to_open = self.__args_namespace.other_parameters

        if files_to_open is not None:
            for diags_file in files_to_open:
                if '.json' in diags_file:
                    params = self.get_parameters_from_json(diags_file, default_vars, check_values)
                elif '.cfg' in diags_file:
                    params = self.get_parameters_from_cfg(diags_file, default_vars, check_values)
                else:
                    raise RuntimeError('The parameters input file must be either a .json or .cfg file')

                for p in params:
                    parameters.append(p)

        return parameters

    def get_parameters(self, orig_parameters=None, other_parameters=[], vars_to_ignore=[], *args, **kwargs):
        """Combine orig_parameters with all of the other_parameters, while ignoring vars_to_ignore."""
    
        if orig_parameters is None:
            orig_parameters = self.get_orig_parameters(*args, **kwargs)
        if other_parameters == []:
            other_parameters = self.get_other_parameters(*args, **kwargs)
            
        for parameters in other_parameters:
            for var in orig_parameters.__dict__:
                if var not in vars_to_ignore:
                    parameters.__dict__[var] = orig_parameters.__dict__[var]

        return other_parameters if other_parameters != [] else [orig_parameters]

    def load_default_args(self):
        """Load the default arguments for the parser."""
        self.add_argument(
            '-p', '--parameters',
            type=str,
            dest='parameters',
            help='Path to the user-defined parameter file',
            required=False)
        self.add_argument(
            '-d', '--diags',
            type=str,
            nargs='+',
            dest='other_parameters',
            help='Path to the other user-defined parameter file',
            required=False)

    def add_args_and_values(self, arg_list):
        """Used for testing. Can test args input as if they
        were inputted from the command line."""
        self.__args_namespace = self.parse_args(arg_list)
