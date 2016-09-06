import os
import logging
import json
import genutil
import cdat_info
import cdms2
from CDP.base.CDPIO import *


class CDMSDomainsEncoder(json.JSONEncoder):
    def default(self, o):
        components = o.components()[0].kargs
        args = '.'.join(
            ['%s=%s' % (key, val) for key, val in components.iteritems()]
        )
        return {o.id: 'cdutil.region.domain(%s)' % args}


class PMPIO(CDPIO, genutil.StringConstructor):
    def __init__(self, root, file_template, file_mask_template=None):
        genutil.StringConstructor.__init__(self, root + '/' + file_template)
        self.target_grid = None
        self.mask = None
        self.target_mask = None
        self.file_mask_template = file_mask_template
        self.root = root
        self.setup_cdms2()

    def read(self):
        pass

    def __call__(self):
        return os.path.abspath(genutil.StringConstructor.__call__(self))

    def write(self, data_dict, extension='json', *args, **kwargs):
        file_name = os.path.abspath(self()) + '.' + extension
        dir_path = os.path.split(file_name)[0]

        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except:
                logging.error(
                    'Could not create output directory: %s' % dir_path)
                print 'Could not create output directory: %s' % dir_path

        if extension.lower() == 'json':
            f = open(file_name, 'w')
            # data_dict['metrics_git_sha1'] = pcmdi_metrics.__git_sha1__
            data_dict['uvcdat_version'] = cdat_info.get_version()
            json.dump(data_dict, f, cls=CDMSDomainsEncoder, *args, **kwargs)
            f.close()

        elif extension.lower() in ['asc', 'ascii', 'txt']:
            f = open(file_name, 'w')
            for key in data_dict.keys():
                f.write('%s %s\n' % (key, data_dict[key]))
            f.close()

        elif extension.lower() == 'nc':
            f = cdms2.open(file_name, 'w')
            f.write(data_dict, *args, **kwargs)
            # f.metrics_git_sha1 = pcmdi_metrics.__git_sha1__
            f.uvcdat_version = cdat_info.get_version()
            f.close()

        else:
            logging.error('Unknown extension: %s' % extension)
            raise RuntimeError('Unknown extension: %s' % extension)

        logging.info('Results saved to a %s file: %s' % (extension, file_name))

    def set_target_grid(self, target, regrid_tool='esmf',
                        regrid_method='linear'):
        self.regrid_tool = regrid_tool
        self.regrid_method = regrid_method
        if target == '2.5x2.5':
            self.target_grid = cdms2.createUniformGrid(
                -88.875, 72, 2.5, 0, 144, 2.5
            )
            self.target_grid_name = target
        elif cdms2.isGrid(target):
            self.target_grid = target
            self.target_grid_name = target
        else:
            logging.error('Unknown grid: %s' % target)
            raise RuntimeError('Unknown grid: %s' % target)

    def setup_cdms2(self):
        cdms2.setNetcdfShuffleFlag(0)  # Argument is either 0 or 1
        cdms2.setNetcdfDeflateFlag(0)  # Argument is either 0 or 1
        cdms2.setNetcdfDeflateLevelFlag(0)  # Argument is int between 0 and 9
