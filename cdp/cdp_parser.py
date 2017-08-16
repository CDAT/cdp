import argparse
import abc
import json


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

    def get_other_parameters(self, default_vars=True, check_values=True):
        """Returns the parameters created by -d"""
        parameters = []
        self.__args_namespace = self.parse_args()

        if self.__args_namespace.other_parameters is not None:
            with open(self.__args_namespace.other_parameters) as json_file:
                json_data = json.loads(json_file.read())

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

        raise RuntimeError('get_other_parameters() was called without the -d argument')


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
            dest='other_parameters',
            help='Path to the other user-defined parameter file',
            required=False)

    def add_args_and_values(self, arg_list):
        """Used for testing. Can test args input as if they
        were inputted from the command line."""
        self.__args_namespace = self.parse_args(arg_list)
