import genutil
from CDP.base.CDPIO import *


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

    def write(self):
        pass

thing = PMPIO('root', 'sdfmosmdf')
