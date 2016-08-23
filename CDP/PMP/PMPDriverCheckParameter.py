from CDP.PMP.PMPParameter import *
import logging

class PMPDriverCheckParameter(object):

    def __init__(self, parameter):
        self.parameter = parameter

    def check_this_var_in_parameter(self, var_to_check_name):
        if hasattr(self.parameter, var_to_check_name) == False:
            logging.error("%s is not in the parameter file!" % var_to_check_name)
            raise AttributeError("%s is not in the parameter file!" % var_to_check_name)

    def check_parameter(self):
        #Just check that all of the parameters use exist in the parameter object
        #The validity for each option was already checked by the parameter itself
        vars_to_check = ['case_id', 'model_versions', 'period', 'realization',
                        'vars', 'ref', 'target_grid', 'regrid_tool',
                        'regrid_method', 'regrid_tool_ocn', 'regrid_method_ocn',
                        'save_mod_clims', 'regions_specs', 'regions', 'custom_keys',
                        'filename_template', 'generate_surface_type_land_fraction',
                        'surface_type_land_fraction_filename_template',
                        'mod_data_path', 'obs_data_path', 'metrics_output_path',
                        'model_clims_interpolated_output', 'filename_output_template',
                        'custom_observations_path']
        for var in vars_to_check:
            self.check_this_var_in_parameter(var)
