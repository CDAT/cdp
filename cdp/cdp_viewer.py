import os
import stat
from output_viewer.build import build_viewer
from output_viewer.utils import rechmod
from output_viewer.index import OutputIndex, OutputPage, OutputFile, OutputRow, OutputGroup


class OutputViewer(object):
    def __init__(self, path='.', index_name='Results'):
        self.path = os.path.abspath(path)
        self.index = OutputIndex(index_name)
        self.pages = {}
        self.page = None
        self.groups = {}
        self.group = None
        self.rows = {}
        self.row = None

    def add_page(self, name, cols):
        ''' Add a page to the viewer's index. '''
        self.page = OutputPage(name, cols)
        self.pages[name] = self.page
        self.index.addPage(self.page)

    def set_page(self, name):
        ''' Sets the page with the title name as the current page. '''
        if name in self.pages.keys():
            self.page = self.pages[name]
        else:
            raise RuntimeError('There is no page titled: %s' % name)

    def add_group(self, name):
        ''' Add a group to the current page. '''
        if name not in self.groups:
            self.group = OutputGroup(name)
            self.groups[name] = self.group
            self.page.addGroup(self.group)
        else:
            self.group = self.groups[name]

    def set_group(self, name):
        ''' Sets the group with the title name as the current group. '''
        if name in self.groups.keys():
            self.group = self.groups[name]
        else:
            raise RuntimeError('There is no group titled: %s' % name)

    def add_row(self, name):
        ''' Add a row with the title name to the current group. '''
        cols = []
        cols.append(name)

        if self.group is None:
            raise RuntimeError('You must first create a group with add_group()')
        if self.page is not None:
            self.row = OutputRow(name, [])
            self.rows[name] = self.row
            self.page.addRow(self.row, len(self.page.groups)-1)
        else:
            raise RuntimeError('You need to add a page with add_page() before calling add_row()')

    def set_row(self, name):
        ''' Sets the row with the title name as the current row. '''
        if name in self.rows.keys():
            self.row = self.rows[name]
        else:
            raise RuntimeError('There is no row titled: %s' % name)

    def add_cols(self, cols):
        ''' Add multiple string cols to the current row. '''
        self.row.columns.append(cols)

    def add_col(self, col, is_file=False, **kwargs):
        ''' Add a single col to the current row. Set is_file to True if the col is a file path. '''
        if is_file:
            self.row.columns.append(OutputFile(col, **kwargs))
        else:
            self.row.columns.append(col)

    def generate_viewer(self, prompt_user=True):
        ''' Generate the webpage and ask the user if they want to see it. '''
        self.index.toJSON(os.path.join(self.path, "index.json"))

        default_mask = stat.S_IMODE(os.stat(self.path).st_mode)
        rechmod(self.path, default_mask)

        if os.access(self.path, os.W_OK):
            default_mask = stat.S_IMODE(os.stat(self.path).st_mode)  # mode of files to be included
            build_viewer(
                os.path.join(self.path, "index.json"),
                diag_name="My Diagnostics",
                default_mask=default_mask)

        if os.path.exists(os.path.join(self.path, "index.html")):
            if prompt_user:
                print "Viewer HTML generated at {path}/index.html.".format(path=self.path)
                user_promt = "Would you like to open in a browser? y/[n]: "
                should_open = raw_input(user_promt)
                if should_open and should_open.lower()[0] == "y":
                    import webbrowser
                    index_path = os.path.join(self.path, "index.html")
                    url = "file://{path}".format(path=index_path)
                    webbrowser.open(url)
        else:
            raise RuntimeError("Failed to generate the viewer.")
