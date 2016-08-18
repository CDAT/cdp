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

    def check_str_seq_in_str_list(self, str_sequence, str_sequence_name, str_vars_list):
        if type(str_sequence) is not list and type(str_sequence) is not tuple:
            raise TypeError("%s is the wrong type. It must be a list or tuple." % str_sequence_name)

        for str_var in str_sequence:
            if str_var not in str_vars_list:
                logging.warning("%s might not be a valid value in %s." % (str_var, str_sequence_name))


    def check_str_var_in_str_list(self, str_var, str_var_name, str_vars_list):
        if type(str_var) is not str:
                raise TypeError("%s is the wrong type. It must be a string." % str_vars_list)

        if str_var not in str_vars_list:
                logging.warning("%s might not be a valid value in %s." % (str_var, str_var_name))


    def check_vars(self):
        vars_2d_atmos = ['clt','hfss','pr','prw','psl','rlut','rlutcs',
            'rsdt','rsut','rsutcs','tas','tauu','tauv','ts','uas','vas']
        vars_3d_atmos = ['hur','hus','huss','ta','ua','va','zg']
        vars_2d_ocean = ['sos', 'tos', 'zos']
        vars_non_std = ['rlwcrf','rswcrf']
        vars_values = vars_2d_atmos + vars_3d_atmos + vars_2d_ocean + vars_non_std

        self.check_str_seq_in_str_list(self.vars, 'vars', vars_values)


    def check_ref(self):
        ref_values = ['default','all','alternate','ref3']
        self.check_str_seq_in_str_list(self.ref, 'ref', ref_values)


    def check_target_grid(self):
        self.check_str_var_in_str_list(self.target_grid, 'target_grid', ['2.5x2.5'])


    def check_regrid_tool(self):
        self.check_str_var_in_str_list(self.regrid_tool, 'regrid_tool', ['regrid2','esmf'])

    def check_regrid_method(self):
        self.check_str_var_in_str_list(self.regrid_method, 'regrid_method', ['linear','conservative'])

    def check_regrid_tool_ocn(self):
        self.check_str_var_in_str_list(self.regrid_tool_ocn, 'regrid_tool_ocn', ['regrid2','esmf'])

    def check_regrid_method_ocn(self):
        self.check_str_var_in_str_list(self.regrid_method_ocn, 'regrid_method_ocn', ['linear','conservative'])

    def check_save_mod_clims(self):
        if self.save_mod_clims is None:
            raise ValueError("save_mod_clims cannot be None. It must be either True or False.")


    def check_values(self):
        #check that all of the variables in __init__() have a valid value
        self.check_vars()
        self.check_ref()
        self.check_target_grid()
        self.check_regrid_tool()
