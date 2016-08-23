from CDP.base.CDPDriver import *

class PMPDriver(CDPDriver):

    def check_parameter(self):
        #check that all of the variables used from parameter exist
        PMPDriverCheckParameter.check_parameter(self.parameter)


    def calculate_level_from_var_name_split(self, split_name):
        if len(split_name) > 1:
            self.level = float(split_name[-1]) * 100
        else
            self.level = None

    def run_diags(self):
        for var_long_name in self.parameter.vars:
            var_name_split = var_long_name.split('_')
            self.calculate_level(var_name_split)

            self.var = var_name_split[0]

    def export(self):
        pass
