import abc
import importlib
import sys
import os

class CDPParameter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def check_values():
        """Check that all of the variables in this parameter file are valid.
        If loading from a file using load_parameter_from_py(), check if all of
        the correct variables are defined in that file."""
        raise NotImplementedError()

    def __get__(self):
        check_values()

    #Parameter files can also be initalized from a file.
    #This is bad practice, but it was a requirement.
    def load_parameter_from_py(self, parameter_file_path):
        #Ex: parameter_file_path is '/Users/shaheen2/Desktop/parameter.py'
        #path_to_module = '/Users/shaheen2/Desktop'
        #module_name = 'parameter'
        #self.user_file is a reference to the parameter file, which is parameter.py in this case
        #self.user_defined_vars has all of the definded variables such as vars, output_path, etc

        path_to_module = os.path.split(parameter_file_path)[0]
        module_name = os.path.split(parameter_file_path)[1]
        if module_name.count('.') > 1:
            raise ValueError("Filename cannot contain '.' outside the extension.")
        if('.' in module_name):
            module_name = module_name.split('.')[0]

        sys.path.append(path_to_module)
        self.user_file = importlib.import_module(module_name)
        self.user_defined_vars = [user_var for user_var in dir(self.user_file) if not user_var.startswith('__')]

        #initalize the variables in this parameter, so the driver can access them as if they were defined regularly
        #This is the bad practice I was talking about
        for var in self.user_defined_vars:
            exec("self." + var + " = self.user_file." + var)
