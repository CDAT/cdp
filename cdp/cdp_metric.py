from __future__ import print_function

import abc
import sys
import cdp._cache


class CDPMetric(object, metaclass=abc.ABCMeta):
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

    def __init__(self, metric_name=None):
        #  metric_info: information displayed when the metric is used.
        # _values: dictionary of the computed values. This allows for compound metrics.
        self.metric_info = None
        if metric_name is None:
            metric_name = sys.modules[self.__class__.__module__].__file__  # gets the path of the file
            metric_name = metric_name.split('/')[-1].split('.')[0]  # get the 'filename' from /path/to/filename.py
        self._values = {metric_name: self}

    def __call__(self, *args, **kwargs):
        self._show_metric_information()
        if self._is_compound():
            # Remove the 'cdp_metric' key from the _values because 
            # it's just a key with a blank value created when there's a compound metric
            self._values.pop('cdp_metric')
            # loop through and calculate all of the metrics
            for key, value in list(self._values.items()):
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
        compound_metric = CompoundMetric()
        self._add_values_dict_into_first(compound_metric, self)
        self._add_values_dict_into_first(compound_metric, other)
        return compound_metric

    def __sub__(self, other):
        class CompoundMetric(CDPMetric):
            def compute(self):
                pass
        if not self._is_compound():
            raise TypeError('First operand must be a CompoundMetric')
        compound_metric = CompoundMetric()
        self._add_values_dict_into_first(compound_metric, self)
        self._subtract_values_dict_into_first(compound_metric, other)
        return compound_metric

    def _is_compound(self):
        """Determines if the current metric was a compound metric, one
        created with the + operator."""
        return len(self._values) > 1

    def _add_values_dict_into_first(self, compound_metric, other_metric):
        """Merges the _values dict of two objects of type CDPMetric
        into the first."""
        for key, value in list(other_metric._values.items()):
            compound_metric._values[key] = value

    def _subtract_values_dict_into_first(self, compound_metric, other_metric):
        """Removes the elements of the _values dict of the second
        object from the first object's _values dict."""
        for key in other_metric._values:
            if compound_metric._values.pop(key, None) is None:
                print("Could not subtract {} metric since it's not in the first operand.".format(key))

    def _show_metric_information(self):
        """Displays information about this metric so that a user
        can easily identify what metrics are being used."""
        if self.metric_info:
            print(self.metric_info)

    def set_metric_info(self, info):
        """Sets a message to be displayed everytime 
        a metric is called. Useful for debugging."""
        self.metric_info = info

    @abc.abstractmethod
    def compute(self):
        """Compute the metric."""
        raise NotImplementedError()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
