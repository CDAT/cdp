import cdutil
from CDP.PMP.PMPDriver import *
from CDP.PMP.PMPParameter import *

parameter = PMPParameter()
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

driver = PMPDriver(parameter)
driver.run()
