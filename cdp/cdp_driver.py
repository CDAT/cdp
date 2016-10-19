import abc


class CDPDriver(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parameter):
        self.parameter = parameter

    def __call__(self):
        self.run()

    def run(self):
        """ Run the driver by calling the three
        other functions in this class. """
        self.check_parameter()
        self.run_diags()
        self.export()

    @abc.abstractmethod
    def check_parameter(self):
        """ Check that parameter has the correct
        information for this driver. """
        raise NotImplementedError()

    @abc.abstractmethod
    def run_diags(self):
        """ Given the parameters, run diagnostics. """
        raise NotImplementedError()

    @abc.abstractmethod
    def export(self):
        """ Export the results from run_diags(). """
        raise NotImplementedError()
