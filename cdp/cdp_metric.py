import abc
import cdp.cdp_tool


class CDPMetric(cdp.cdp_tool.CDPTool):
    __metaclass__ = abc.ABCMeta

    def __init__(self, var, data1, data2):
        self.var = var
        self.data1 = data1
        self.data2 = data2

    def __call__(self):
        self.compute()

    @abc.abstractmethod
    def compute(self):
        """ Compute the metric. """
        raise NotImplementedError()
