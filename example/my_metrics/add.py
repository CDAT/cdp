import cdp.cdp_metric

class Add(cdp.cdp_metric.CDPMetric):
    def compute(self, a, b):
        return a + b
