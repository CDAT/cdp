import abc

class CDPOutput(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parameter):
        self.parameter = parameter

    def set_parameter(p):
        self.parameter = p

    def get_parameter():
        return self.parameter


    @abc.abstractmethod
    def check_parameter():
        """Check that self.parameter has the correct information for this kinda of output."""
        raise NotImplementedError()

    @abc.abstractmethod
    def create_output():
        """Given parameters, create the respective output."""
        raise NotImplementedError()

    def run():
        check_parameter()
        create_output()
