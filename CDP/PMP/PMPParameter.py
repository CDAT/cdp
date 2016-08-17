from CDP.base.CDPParameter import *
import logging

class PMPParameter(CDPParameter):
    def __init__(self):
        #Metrics run identification
        self.case_id = ''
        self.model_versions = []
        self.period = ''
        self.realization = ''

        #
        self.vars = []
        self.ref = []
        self.target_grid = ''

        self.regrid_tool = ''
        self.regrid_method = ''
        self.regrid_tool_ocn = ''
        self.regrid_method_ocn = 'linear'

        self.save_mod_clims = None
        self.regions_specs = {}
        self.regions = {}
        self.custom_keys = {}

        self.filename_template = ''
        self.surface_type_land_fraction_filename_template = ''
        self.generate_surface_type_land_fraction = None

        self.mod_data_path = ''
        self.obs_data_path = ''
        self.metrics_output_path = ''
        self.model_clims_interpolated_output = ''
        self.filename_output_template = ''

        self.custom_observations = ''

    def check_vars(self):
        if type(self.vars) is list:
            raise TypeError("var is wrong type. It must be a list.")

        vars_2d_atmos = ['clt','hfss','pr','prw','psl','rlut','rlutcs',
            'rsdt','rsut','rsutcs','tas','tauu','tauv','ts','uas','vas']
        vars_3d_atmos = ['hur','hus','huss','ta','ua','va','zg']
        #TODO ask someone if the height can be any value, or only these values
        vars_3d_atmos_with_heights = ['hus_850','ta_850','ta_200','ua_850',
            'ua_200','va_850','va_200','zg_500']
        vars_2d_ocean = ['sos', 'tos', 'zos']
        vars_non_std = ['rlwcrf','rswcrf']

        for variable in self.vars:
            if (variable not in vars_2d_atmos) or (variable not in vars_3d_atmos)\
                or (variable not in vars_2d_ocean) or (variable not in vars_non_std)\
                or (variable not in vars_3d_atmos_with_heights):
                    raise ValueError("var does not have a valid value.")

    def check_values(self):
        #check that all of the variables in __init__() have a valid value
        self.check_vars()
