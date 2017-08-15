import abc


class CDPOutput(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parameter):
        self.parameter = parameter

    def __call__(self):
        self.run()

    def run(self):
        """Create the output based on the parameter."""
        self.check_parameter()
        self.create_output()

    @abc.abstractmethod
    def check_parameter(self):
        """Check that parameter has the correct information
        for this kind of output."""
        raise NotImplementedError()

    @abc.abstractmethod
    def create_output(self):
        """Given the parameter, create the respective output."""
        raise NotImplementedError()
