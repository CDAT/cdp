import abc


class CDPIO(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def read(self):
        """Read a file."""
        raise NotImplementedError()

    @abc.abstractmethod
    def write(self):
        """Write a file."""
        raise NotImplementedError()
