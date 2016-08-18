from CDP.base.CDPParameter import *
import logging

class PMPParameter(CDPParameter):
    def __init__(self):
        #Metrics run identification
        self.case_id = ''
        self.model_versions = []
        self.period = ''
        self.realization = ''

        self.vars = []
        self.ref = []
        self.target_grid = ''

        self.regrid_tool = ''
        self.regrid_method = ''
        self.regrid_tool_ocn = ''
        self.regrid_method_ocn = ''

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
        if (type(self.vars) is not list) and (type(self.vars) is not tuple):
            raise TypeError("vars is the wrong type. It must be a list or tuple.")

        vars_2d_atmos = ['clt','hfss','pr','prw','psl','rlut','rlutcs',
            'rsdt','rsut','rsutcs','tas','tauu','tauv','ts','uas','vas']
        vars_3d_atmos = ['hur','hus','huss','ta','ua','va','zg']
        vars_2d_ocean = ['sos', 'tos', 'zos']
        vars_non_std = ['rlwcrf','rswcrf']

        for variable in self.vars:
            if (variable not in vars_2d_atmos) or (variable not in vars_3d_atmos)\
                or (variable not in vars_2d_ocean) or (variable not in vars_non_std)\
                or (variable not in vars_3d_atmos_with_heights):
                    logging.warning("%s might not be a valid value in vars." % variable)

    def check_ref(self):
        if (type(self.ref) is not list) and (type(self.ref) is not tuple):
            raise TypeError("ref is the wrong type. It must be a list or tuple.")

        ref_values = ['default','all','alternate','ref3']
        for r in self.ref:
            if r not in ref_values:
                logging.warning("%s might not be a valid value in ref." % r)

    def check_target_grid(self):
        #TODO add checking to see if type is cdms grid type as well
        if type(self.target_grid) is not str:
                raise TypeError("target_grid is the wrong type. It must be a string.")

        target_grid_values = ['2.5x2.5']
        if self.target_grid not in target_grid_values:
                logging.warning("%s might not be a valid value in target_grid." % self.target_grid)

    
    def check_values(self):
        #check that all of the variables in __init__() have a valid value
        self.check_vars()
        self.check_ref()
