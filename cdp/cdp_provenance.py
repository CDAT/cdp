import abc


class CDPProvenance(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def export_prov(self):
        """Export the provenance."""
        raise NotImplementedError()
