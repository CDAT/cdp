import os, logging, json
import genutil
import cdat_info
import cdms2
from CDP.base.CDPIO import *

class CDMSDomainsEncoder(json.JSONEncoder):
    pass


class PMPIO(CDPIO, genutil.StringConstructor):
    def __init__(self, root, file_template, file_mask_template=None):
        genutil.StringConstructor.__init__(self, root + '/' + file_template)
        self.target_grid = None
        self.mask = None
        self.target_mask = None
        self.file_mask_template = file_mask_template
        self.root = root

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
                logging.error('Could not create output directory: %s' % dir_path)
                print 'Could not create output directory: %s' % dir_path

        if extension.lower() == 'json':
            f = open(file_name, 'w')
            #data_dict['metrics_git_sha1'] = pcmdi_metrics.__git_sha1__
            data_dict['uvcdat_version'] = cdat_info.get_version()
            json.dump(data_dict, f, cls=CDMSDomainsEncoder, *args, **kwargs)
            f.close()
            logging.info('Results saved to a %s file: %s' % (extension, file_name))
        elif extension.lower() in ['asc', 'ascii', 'txt']:
            f = open(file_name, 'w')
            for key in data_dict.keys():
                f.write('%s %s\n' % (key, data_dict[key]))
            f.close()
            logging.info('Results saved to a %s file: %s' % (extension, file_name))
        elif extension.lower() == 'nc':
            f = cdms2.open(file_name, 'w')
            f.write(data_dict, *args, **kwargs)
            #f.metrics_git_sha1 = pcmdi_metrics.__git_sha1__
            f.uvcdat_version = cdat_info.get_version()
            f.close()
            logging.info('Results saved to a %s file: %s' % (extension, file_name))
        else:
            logging.error('Unknown extension: %s' % extension)
            raise RuntimeError('Unknown extension: %s' % extension)

thing = PMPIO('root', 'sdfmosmdf')
thing.write({})
