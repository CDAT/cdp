import logging
from CDP.PMP.PMPDriver import *
from CDP.PMP.PMPParameter import *

class PMPDriverRunDiags(object):

        def __init__(self, parameter):
            self.parameter = parameter

        def calculate_level(self, var_split_name):
            #There is a height for the variable, ex: hus_850
            if len(var_split_name) > 1:
                self.level = float(var_split_name[-1]) * 100
            else:
                self.level = None

        def load_path_as_file_obj(self, path):
            file_path = os.path.join(os.path.dirname(__file__), path)
            print 'FILEPATH: %s' % file_path
            try:
                opened_file = open(path)
            except IOError:
                logging.error('%s could not be loaded!' % file_path)
            except:
                logging.error('Unexpected error: %s' % sys.exc_info()[0])
                print 'Unexpected error: %s' % sys.exc_info()[0]
            return opened_file

        def load_obs_dic(self):
            obs_json_file = load_path_as_file_obj('share/obs_info_dictionary.json')
            self.obs_dic = json.loads(obs_json_file.read())
            obs_json_file.close()

        def set_regrid_and_realm_from_obs_dic_using_var(self):
            if self.obs_dic[self.var][self.obs_dic[self.var]["default"]]["CMIP_CMOR_TABLE"] == "Omon":
                self.regrid_method = self.parameter.regrid_method_ocn
                self.regrid_tool = self.parameter.regrid_tool_ocn
                self.table_realm = 'Omon'
                self.realm = "ocn"
            else:
                self.regrid_method = self.parameter.regrid_method
                self.regrid_tool = self.parameter.regrid_tool
                self.table_realm = 'Amon'
                self.realm = "atm"


        def setup_metrics_dictionary(self):
            disclaimer_file = load_path_as_file_obj('share/disclaimer.txt')

            self.metrics_dictionary['DISCLAIMER'] = disclaimer_file.read()
            disclaimer_file.close()
            self.metrics_dictionary["RESULTS"] = collections.OrderedDict()

            self.metrics_dictionary["Variable"] = {}
            self.metrics_dictionary["References"] = {}
            self.metrics_dictionary["RegionalMasking"] = {}

        def set_grid(self):
            self.grid["RegridMethod"] = self.regridMethod
            self.grid["RegridTool"] = self.regridTool
            self.grid["GridName"] = self.parameter.targetGrid

        def set_refs(self):
            self.refs = self.parameter.refs
            if isinstance(self.refs, list) and 'all' in [r.lower() for r in self.refs]:
                self.refs = 'all'
            if isinstance(self.refs, (unicode, str)):
                if self.refs.lower() == 'all':
                    refs_list = self.obs_dic[self.var].keys()
                    self.refs = []
                    for r in refs_list:
                        if instance(self.obs_dic[self.var][r], (unicode, str)):
                            self.refs.append(r)
                else:
                    self.refs = [self.refs,]

        def set_regions_dic(self):
            self.regions = self.parameter.regions

            self.default_regions = []
            regions_file = load_path_as_file_obj('share/default_regions.py')
            try:
                execfile(regions_file.name)
            except:
                logging.error('Unexpected error while running execfile(): %s' % sys.exc_info()[0])
                print 'Unexpected error while running execfile(): %s' % sys.exc_info()[0]

            self.regions_dic = {}
            for var_name_long in self.parameter.vars:
                var = var_name_long.split("_")[0]
                region = self.regions.get(var, default_regions)
                if not isinstance(region, (list, tuple)):
                    region = [region, ]
                #None means use the default regions
                if None in region:
                    region.remove(None)
                    for r in self.default_regions:
                        region.insert(0, r)
                self.regions_dic[var] = region

        def regions_loop(self):
            self.set_regions_dic()
            for self.region in self.region_dic[self.var]:
                pass

        def run_diags(self):
            for var_long_name in self.parameter.vars:
                self.metrics_def_dictionary = collections.OrderedDict()
                self.metrics_dictionary = collections.OrderedDict()
                self.setup_metrics_dictionary()

                self.obs_dic = {}
                self.load_obs_dic()

                var_name_split = var_long_name.split('_')
                self.calculate_level(var_name_split)
                self.var = var_name_split[0]

                self.set_regrid_and_realm_from_obs_dic_using_var()

                self.grid = {}
                self.set_grid()

                self.set_refs()

                self.regions_loop()
thing = PMPDriverRunDiags(PMPParameter())
thing.run_diags()
