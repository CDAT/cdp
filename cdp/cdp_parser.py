from __future__ import print_function

import sys
import argparse
import abc
import json
import yaml
import warnings
from six import with_metaclass

if sys.version_info[0] >= 3:
    import configparser
else:
    import ConfigParser as configparser


class CDPParser(argparse.ArgumentParser):
    def __init__(self, parameter_cls, default_args_file=[], *args, **kwargs):
        # conflict_handler='resolve' lets new args override older ones
        super(CDPParser, self).__init__(conflict_handler='resolve',
                                        *args, **kwargs)
        self.load_default_args(default_args_file)
        self.__parameter_cls = parameter_cls
        self.__args_namespace = None

    def view_args(self):
        """Returns the args namespace"""
        self.parse_arguments()
        return self.__args_namespace

    def overwrite_parameters_with_cmdline_args(self, parameters):
        """Overwrite the parameters with the user's command line arguments."""
        for arg_name, arg_value in vars(self.__args_namespace).items():
            if arg_value is not None:
                # Add it to the parameter
                setattr(parameters, arg_name, arg_value)

    def parse_arguments(self):
        """Parse the command line arguments while checking for the user's arguments"""
        if self.__args_namespace is None:
            self.__args_namespace = self.parse_args()            
            if self.__args_namespace.parameters is None and self.__args_namespace.other_parameters is None:
                print('You must have either the -p or -d arguments.')
                self.print_help()
                sys.exit()

    def get_orig_parameters(self, default_vars=True, check_values=True):
        """Returns the parameters created by -p. If -p wasn't used, returns None."""
        parameter = self.__parameter_cls()

        self.parse_arguments()
        
        if self.__args_namespace.parameters is None:
            return None

        if not default_vars:  # remove all of the variables
            parameter.__dict__.clear()

        #if self.__args_namespace.parameters is not None:
        parameter.load_parameter_from_py(
            self.__args_namespace.parameters)

        for arg_name, arg_value in vars(self.__args_namespace).items():
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

        config = configparser.ConfigParser()
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
    
        self.parse_arguments()

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

    def combine_orig_and_other_params(self, orig_parameters, other_parameters, vars_to_ignore=[]):
        """Combine orig_parameters with all of the other_parameters, while ignoring vars_to_ignore"""
        for parameters in other_parameters:
            for var in orig_parameters.__dict__:
                if var not in vars_to_ignore:
                    parameters.__dict__[var] = orig_parameters.__dict__[var]

    def get_parameters(self, orig_parameters=None, other_parameters=[], vars_to_ignore=[], *args, **kwargs):
        """Get the parameters based on the command line arguments and return a list of them."""
        if orig_parameters is None:
            orig_parameters = self.get_orig_parameters(*args, **kwargs)
        if other_parameters == []:
            other_parameters = self.get_other_parameters(*args, **kwargs)            

        if orig_parameters is not None and other_parameters == []:  # only -p
            return [orig_parameters]
        elif orig_parameters is None and other_parameters != []:  # only -d
            return other_parameters
        elif orig_parameters is not None and other_parameters != []:  # used -p and -d
            self.combine_orig_and_other_params(orig_parameters, other_parameters, vars_to_ignore)
            return other_parameters
        else:
            raise RuntimeError("You ran your script without a '-p' or '-d' argument.")

    def get_parameter(self, warning=True, *args, **kwargs):
        """Return the first Parameter in the list of Parameters."""
        if warning:
            print('Deprecation warning: Use get_parameters() instead, which returns a list of Parameters.')
        return self.get_parameters(*args, **kwargs)[0]

    def load_default_args_from_json(self, files):
        """ take in a list of json files (or a single json file) and create the args from it"""
        if not isinstance(files,(list,tuple)):
            files = [files]
        success = None
        for afile in files:
            print("Loading in json file:",afile)
            with open(afile) as json_file:
                args = json.load(json_file)
                for k in args.keys():
                    if k[0]!="-":
                        continue
                    #try:
                    if 1:
                        param = args[k]
                        option_strings = param.pop("aliases",[])
                        option_strings.insert(0,k)
                        param["type"]=eval(param.pop("type","str"))
                        print("OPT:",option_strings)
                        print("OTHER:",param)
                        self.add_argument(*option_strings,**param)
                        success = True
                    #except:
                    #    warnings.warn("failed to load param {} from json file {}".format(
                    #        k,afile))
                    #    pass
        return success
    def load_default_args(self, files):
        """Load the default arguments for the parser."""
        if self.load_default_args_from_json(files):
            return
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
            default=[],
            help='Path to the other user-defined parameter file',
            required=False)
        self.add_argument(
            '-n', '--num_workers',
            type=int,
            dest='num_workers',
            help='Number of workers, used when running with multiprocessing or distributedly',
            required=False)
        self.add_argument(
            '--scheduler_addr',
            type=str,
            dest='scheduler_addr',
            help='Address of the scheduler in the form of IP_ADDRESS:PORT. Used when running distributedly',
            required=False)

    def add_args_and_values(self, arg_list):
        """Used for testing. Can test args input as if they
        were inputted from the command line."""
        self.__args_namespace = self.parse_args(arg_list)
