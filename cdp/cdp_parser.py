import argparse
import abc


class CDPParser(argparse.ArgumentParser):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parameter_cls, *args, **kwargs):
        # conflict_handler='resolve' lets new args override older ones
        super(CDPParser, self).__init__(conflict_handler='resolve',
                                        *args, **kwargs)
        self.load_default_args()
        self._parameter = parameter_cls()
        self._args_namespace = None

    def get_parameter(self, default_vars=True, check_values=True):
        """ Returns the parameter created by
        the command line inputs """

    	if not default_vars:  # remove all of the variables
    	    self._parameter.__dict__.clear()

        if self._args_namespace is None:
            self._args_namespace = self.parse_args()

        if self._args_namespace.parameter is not None:
            self._parameter.load_parameter_from_py(
                self._args_namespace.parameter)

        # Overwrite the values of the parameter with the user's args
        for arg_name, arg_value in vars(self._args_namespace).iteritems():
            if arg_value is not None:
                # Add it to the parameter
                setattr(self._parameter, arg_name, arg_value)

        if check_values:
            self._parameter.check_values()
        return self._parameter

    def load_default_args(self):
        """ Load the default arguments for
        the parser. """
        self.add_argument(
            '-p', '--parameters',
            type=str,
            dest='parameter',
            help='Path to the user-defined parameter file',
            required=False)

    def add_args_and_values(self, arg_list):
        """ Used for testing. Can test args input as if they
        were inputted from the command line. """
        self._args_namespace = self.parse_args(arg_list)
