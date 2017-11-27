import abc


class CDPProvenance(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def export_prov(self):
        """Export the provenance."""
        raise NotImplementedError()
