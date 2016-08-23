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

    def run_diags(self):
        for var_long_name in self.parameter.vars:
            var_name_split = var_long_name.split('_')
            self.calculate_level(var_name_split)

            self.var = var_name_split[0]

    def export(self):
        pass
