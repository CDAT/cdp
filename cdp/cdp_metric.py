import abc
import cdp.cdp_tool
import cdp._cache

class CDPMetric(cdp.cdp_tool.CDPTool):
    """
    Abstract class for defining metrics.

    Below is an example on how to create your own metric.

    >>> import cdp.cdp_metric
    >>> class MyMetric(cdp.cdp_metric.CDPMetric):
    ...    def __init__(self):
    ...       metric_path = 'something'
    ...       super(MyMetric, self).__init__(metric_path)
    ...    def compute(self, a, b):
    ...       return a + b
    ...

    Now this is how you use the metric. The compute function is automatically
    called when you __call__() the function object.

    >>> my_metric = MyMetric()
    >>> my_metric(1, 2)
    Using metric: something
    3
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, metric_path=None):
        # metric_path: printed when this metric is used.
        #  Let's users know when a metric is called in the code.
        # _values: dictionary of the computed values. This allows for compound metrics.
        self._metric_path = metric_path
        # get the 'filename' from /path/to/filename.py
        name_with_py = self._metric_path.split('/')[-1]
        name = name_with_py.split('.')[0]
        self._values = {name: self}

    def __call__(self, *args, **kwargs):
        self._show_metric_information()
        if self._is_compound():
            # Remove the 'CompoundMetric' key from the _values because it's just a key with a blank value
            self._values.pop('CompoundMetric')
            # loop through and calculate all of the metrics
            for key, value in self._values.items():
                # replaces the function with the actual value
                self._values[key] = value(*args, **kwargs)
            return self._values
        else:
            #return cdp._cache.cache(self.compute, *args, **kwargs)
	    return self.compute(*args, **kwargs)

    def __add__(self, other):
        class CompoundMetric(CDPMetric):
            def compute(self):
                pass
        compound_metric = CompoundMetric('CompoundMetric')
        self._add_values_dict_into_first(compound_metric, self)
        self._add_values_dict_into_first(compound_metric, other)
        return compound_metric

    def __sub__(self, other):
        class CompoundMetric(CDPMetric):
            def compute(self):
                pass
        if not self._is_compound():
            raise TypeError('First operand must be a CompoundMetric')
        compound_metric = CompoundMetric('CompoundMetric')
        self._add_values_dict_into_first(compound_metric, self)
        self._subtract_values_dict_into_first(compound_metric, other)
        return compound_metric

    def _is_compound(self):
        """ Determines if the current metric was a compound metric, one
        created with the + operator. """
        return len(self._values) > 1

    def _add_values_dict_into_first(self, compound_metric, other_metric):
        """ Merges the _values dict of two objects of type CDPMetric
        into the first. """
        for key, value in other_metric._values.items():
            compound_metric._values[key] = value

    def _subtract_values_dict_into_first(self, compound_metric, other_metric):
        """ Removes the elements of the _values dict of the second
        object from the first object's _values dict. """
        for key in other_metric._values:
            if compound_metric._values.pop(key, None) is None:
                print "Could not subtract %s metric since it's not in the first operand." % key

    def _show_metric_information(self):
        """ Displays information about this metric so that a user
        can easily identify what metrics are being used. """
        print 'Using metric: ' + self._metric_path

    @abc.abstractmethod
    def compute(self):
        """ Compute the metric. """
        raise NotImplementedError()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
