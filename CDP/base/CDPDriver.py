import abc

class CDPDriver(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parameter=None, *tools=list()):
        self.parameter = parameter
        self.tools = tools

    def set_parameter(p):
        self.parameter = p

    def get_parameter():
        return self.parameter

    def set_tools(self, *tools):
        self.tools = list(tools)

    def get_tools():
        return self.tools


    @abc.abstractmethod
    def check_parameter():
        """Check that self.parameter has the correct information for this driver."""
        raise NotImplementedError()

    @abc.abstractmethod
    def run_diags():
        """Given parameters and tools, run diagnostics."""
        raise NotImplementedError()

    @abc.abstractmethod
    def export():
        """Export the results from run_diags()."""
        raise NotImplementedError()

    def run():
        unpack_parameter()
        run_diags()
        export()
