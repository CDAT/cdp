import argparse
import cdutil
from CDP.PMP.PMPDriver import *
from CDP.PMP.PMPParameter import *

parser = argparse.ArgumentParser(
    description='Runs PCMDI Metrics Diagnostics')

parser.add_argument(
    "-p", "--parameters",
    dest="user_parameter_file_path",
    default="",
    help="Path to the user-defined parameter file",
    required=False)

args = parser.parse_args()
parameter = PMPParameter()
if args.user_parameter_file_path is not '':
    parameter.import_user_parameter_file_as_module(args.user_parameter_file_path)

else:
    '''
    #Some vars don't have a 'default' value, and that breaks the code
    #parameter.vars = ['hus','pr']

    parameter.vars = ['ta_85000']
    regions_specs = {"Nino34":
                     {"value": 0.,
                      "domain": cdutil.region.domain(latitude=(-5., 5., "ccb"), longitude=(190., 240., "ccb"))},
                     "NAM": {"value": 0.,
                             "domain": {'latitude': (0., 45.), 'longitude': (210., 310.)},
                             }
                     }
    parameter.regions_specs = regions_specs
    parameter.regions_values = {"terre": 0., }
    '''

    parameter.filename_template = "%(variable)_%(model_version)_Amon_amip_%(realization)_%(period)-clim.nc"
    parameter.case_id = 'simple-test1'
    parameter.model_versions = ['ACCESS1-0']
    parameter.mod_data_path = 'demo/cmip5clims_metrics_package-amip/'
    parameter.obs_data_path = 'demo/obs/'
    parameter.metrics_output_path = './demo/%(case_id)/'
    parameter.ref = ['default']
    #using pr, there is no
    '''regions_specs = {"Nino34":
                     {"value": 0.,
                      "domain": cdutil.region.domain(latitude=(-5., 5., "ccb"), longitude=(190., 240., "ccb"))
                      },
                     "NAM": {"value": 0.,
                             "domain": {'latitude': (0., 45.), 'longitude': (210., 310.)},
                             }
                     }
    parameter.regions_specs = regions_specs'''
    parameter.vars = ['pr']
    parameter.targetGrid = '2.5x2.5'
    parameter.regrid_tool = 'esmf'
    parameter.regrid_method = 'linear'
    parameter.period = '198001-200512'
    parameter.realization = 'r1i1p1'


driver = PMPDriver(parameter)
driver.run()
