from __future__ import print_function

import unittest
import cdp.cdp_metric


class TestCDPMetric(unittest.TestCase):

    class Add(cdp.cdp_metric.CDPMetric):
        def compute(self, a1, a2):
            return a1 + a2

    class Sub(cdp.cdp_metric.CDPMetric):
        def compute(self, s1, s2):
            return s1 - s2

    def test_init_metric(self):
        try:
            sub = self.Sub()
        except:
            self.fail('Failed to initialize a variable of type Sub, a child type of CDPMetric.')

    def test_compute(self):
        try:
            sub = self.Sub()
            result = sub(2, 1)
            self.assertEquals(result, 1)
        except Exception as err:
            self.fail('Failure during call compute(): %s' % err)

    def test_add(self):
        try:
            sub = TestCDPMetric.Sub('sub')
            add = TestCDPMetric.Add('add')
            new_metric = sub + add
            result = new_metric(2, 1)
            self.assertDictEqual(result, {'add':3, 'sub':1})
        except Exception as err:
            self.fail('Failure during metric addition: %s' % err)

    def test_sub(self):
        try:
            sub = TestCDPMetric.Sub('sub')
            add = TestCDPMetric.Add('add')
            compound_metric = sub + add
            new_metric = compound_metric - sub
            result = new_metric(2, 1)
            self.assertDictEqual(result, {'add':3})
        except Exception as err:
            self.fail('Failure during metric subtraction: %s' % err)


    def test_is_compound(self):
        sub = TestCDPMetric.Sub()
        add = TestCDPMetric.Add()
        compound_metric = sub + add
        self.assertTrue(compound_metric._is_compound())

if __name__ == '__main__':
    unittest.main()
