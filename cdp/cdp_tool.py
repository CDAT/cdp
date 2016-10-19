import abc


class CDPTool(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def compute(self):
        """ Compute something. """
        raise NotImplementedError()
