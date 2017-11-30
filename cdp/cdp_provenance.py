from __future__ import print_function

import abc
from six import with_metaclass


class CDPProvenance(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def export_prov(self):
        """Export the provenance."""
        raise NotImplementedError()
