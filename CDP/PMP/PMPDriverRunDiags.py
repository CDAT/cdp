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
                self.metrics_dictionary["Variable"]["level"] = self.level
            else:
                self.level = None

        def load_path_as_file_obj(self, name):
            file_path = os.path.join(os.path.dirname(__file__), 'share', name)
            try:
                opened_file = open(file_path)
            except IOError:
                logging.error('%s could not be loaded!' % file_path)
                print 'IOError: %s could not be loaded!' % file_path

            except:
                logging.error('Unexpected error while opening file: %s' % sys.exc_info()[0])
                print 'Unexpected error while opening file: %s' % sys.exc_info()[0]
            return opened_file

        def load_obs_dic(self):
            obs_json_file = self.load_path_as_file_obj('obs_info_dictionary.json')
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
            disclaimer_file = self.load_path_as_file_obj('disclaimer.txt')
            self.metrics_dictionary['DISCLAIMER'] = disclaimer_file.read()
            disclaimer_file.close()
            self.metrics_dictionary["RESULTS"] = collections.OrderedDict()

            self.metrics_dictionary["Variable"] = {}
            self.metrics_dictionary["References"] = {}
            self.metrics_dictionary["RegionalMasking"] = {}

        def set_grid(self):
            self.grid["RegridMethod"] = self.regrid_method
            self.grid["RegridTool"] = self.regrid_tool
            self.grid["GridName"] = self.parameter.target_grid

        def set_refs(self):
            self.refs = self.parameter.ref
            if isinstance(self.refs, list) and 'all' in [r.lower() for r in self.refs]:
                self.refs = 'all'
            if isinstance(self.refs, (unicode, str)):
                if self.refs.lower() == 'all':
                    refs_list = self.obs_dic[self.var].keys()
                    self.refs = []
                    for r in refs_list:
                        if isinstance(self.obs_dic[self.var][r], (unicode, str)):
                            self.refs.append(r)
                else:
                    self.refs = [self.refs,]

        def set_regions_dic(self):
            self.regions = self.parameter.regions

            self.default_regions = []
            regions_file = self.load_path_as_file_obj('default_regions.py')
            try:
                execfile(regions_file.name)
            except ImportError:
                logging.error('ImportError for cdutil, ignoring for now')
                print 'ImportError for cdutil, ignoring for now'
                #pass
            except:
                logging.error('Unexpected error while running execfile(): %s' % sys.exc_info()[0])
                print 'Unexpected error while running execfile(): %s' % sys.exc_info()[0]

            self.regions_dic = {}

            for var_name_long in self.parameter.vars:
                var = var_name_long.split("_")[0]
                region = self.regions.get(var, self.default_regions)
                if not isinstance(region, (list, tuple)):
                    region = [region, ]
                #None means use the default regions
                if None in region:
                    region.remove(None)
                    for r in self.default_regions:
                        region.insert(0, r)
                self.regions_dic[var] = region


        def set_region_specs(self):
            self.regions_values = {}
            #update default region_values keys with user-defined ones
            self.regions_values.update(self.parameter.regions_values)

            for reg in self.regions_values:
                dic = {"value": self.regions_values[reg]}
                if reg in self.regions_specs:
                    self.regions_specs[reg].update(dic)
                else:
                    self.regions_specs[reg] = dic

            # Update/overwrite default region_specs keys with user ones
            self.regions_specs.update(self.parameter.regions_specs)


        def set_refabbv(self):
            if self.ref[:9] in ['default', 'alternative']:
                self.refabbv = self.ref + 'Reference'
            else:
                self.refabbv = self.ref

        def set_obs_var_ref(self):
            if(isinstance(self.obs_dic[self.var][self.ref], (str, unicode))):
                self.obs_var_ref = self.obs_dic[self.var][self.obs_dic[self.var][self.ref]]
            else:
                self.obs_var_ref = self.obs_dic[self.var][self.ref]
            self.metrics_dictionary["References"][self.ref] = self.obs_var_ref

        def refs_loop(self):
            for ref in self.refs:
                self.ref = ref
                self.set_refabbv()
                self.set_obs_var_ref()


        def regions_loop(self):
            self.set_regions_dic()
            self.set_region_specs()

            for self.region in self.regions_dic[self.var]:
                if isinstance(self.region, basestring):
                    self.region_name = self.region
                    self.region = self.regions_specs.get(
                        self.region_name,
                        self.regions_specs.get(
                        self.region_name.lower()
                        )
                    )
                    self.region['id'] = self.region_name
                elif self.region is None:
                    self.region_name = 'global'
                else:
                    logging.error("Unknown region: %s" % self.region)
                    raise Exception ("Unknown region: %s" % self.region)

                self.metrics_dictionary['RegionalMasking'][self.region_name] = self.region
                self.refs_loop()

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
                self.metrics_dictionary["Variable"]["id"] = self.var

                self.set_regrid_and_realm_from_obs_dic_using_var()

                self.grid = {}
                self.set_grid()

                self.set_refs()

                self.regions_loop()
