import cdp.cdp_metric

class Sub(cdp.cdp_metric.CDPMetric):
    def compute(self, a, b):
        return a - b
