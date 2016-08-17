from CDP.base.CDPParameter import *
import logging

class PMPParameter(CDPParameter):
    def __init__(self):
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

    def check_values(self):
        pass
