import os, sys
import collections
import logging
import json
from CDP.base.CDPDriver import *

class PMPDriver(CDPDriver):

    def check_parameter(self):
        #check that all of the variables used from parameter exist
        PMPDriverCheckParameter.check_parameter(self.parameter)


    def calculate_level(self, var_split_name):
        #There is a height for the variable, ex: hus_850
        if len(var_split_name) > 1:
            self.level = float(var_split_name[-1]) * 100
        else:
            self.level = None

    def load_obs_dic(self):
        json_file_path = os.path.join(os.path.dirname(__file__),
                        'share', 'obs_info_dictionary.json')

        try:
            json_file = open(json_file_path)
        except IOError:
            logging.error('obs dictionary could not be loaded!')
            print 'obs dictionary could not be loaded!'
        except:
            print 'Unexpected error: %s' % sys.exc_info()[0]

        self.obs_dic = json.loads(json_file.read())
        json_file.close()

    def setup_metrics_dictionary():
        self.metrics_dictionary = collections.OrderedDict()

        disclaimer_str = 'ADD DISCLAIMER TEXT SOON'
        self.metrics_dictionary['DISCLAIMER'] = disclaimer_str
        self.metrics_dictionary["RESULTS"] = collections.OrderedDict()

        self.metrics_dictionary["Variable"] = {}
        self.metrics_dictionary["References"] = {}
        self.metrics_dictionary["RegionalMasking"] = {}

        self.metrics_def_dictionary = collections.OrderedDict()


    def run_diags(self):
        for var_long_name in self.parameter.vars:
            self.setup_metrics_dictionary()

            var_name_split = var_long_name.split('_')
            self.calculate_level(var_name_split)

            self.var = var_name_split[0]

    def export(self):
        pass

thing = PMPDriver()
thing.load_obs_dic()
