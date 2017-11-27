

import abc


class CDPIO(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self):
        """Read a file."""
        raise NotImplementedError()

    @abc.abstractmethod
    def write(self):
        """Write a file."""
        raise NotImplementedError()
