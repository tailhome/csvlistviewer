""" A csv file viewer application. """

import sys
import os
import re
import csv
import argparse
from csvlistview import ListView
from csvlistmodel import ListModel

class CsvListApp:
    def __init__(self):
        """Constructor of this class, with minimum initialization."""
        self.imagesize = None
        self.imagesize_set = None

    def build_argparse(self):
        """Build argument parser for command line."""
        parser = argparse.ArgumentParser(description='csv list viewer')
        parser.add_argument('csvfile') # required=True is not required here.
        parser.add_argument('--imagedir', nargs='?', dest='image_directory',
                            required=False, help='base of image file directory',
                            metavar='./', default='./')
        parser.add_argument('--rows', nargs='?', dest='display_rows',
                            required=False, help='number of rows to be displayed',
                            type=int, metavar='10', default='10')
        parser.add_argument('--geometry', nargs='?', dest='geometry',
                            required=False, help='window extent(i.e. 640x360)',
                            metavar='800x480', default=None)
        parser.add_argument('--height', nargs='?', dest='row_height',
                            required=False, help='row height in displayed list',
                            type=int, metavar='50', default=None)
        parser.add_argument('--columns', nargs='?', dest='columns',required=False,
                            help='string list of column names for list',
                            metavar='filename,label,evaluated', default=None)
        return parser

    def check_argument(self, args):
        """Checks provided arguments."""
        # imagedir
        if args.image_directory is not None:
            if not os.path.isdir(args.image_directory):
                print('Is not a directory: %s' % (args.image_directory), file=sys.stderr)
                return False
        self.image_directory = args.image_directory

        # rows
        if args.display_rows < 3 or args.display_rows > 20:
            print('display rows out of range(must be between 3-20): %d' % (args.display_rows), file=sys.stderr)
            return False
        self.display_rows = args.display_rows

        # geometry
        self.numbers = [800, 600] # default value
        if args.geometry is not None:
            """Checks string format is suited for extent."""
            if not re.fullmatch(r"^(\d+)x(\d+)", args.geometry):
                print('incorrect format (must be WIDTHxHEIGHT): %s' % (args.geometry), file=sys.stderr)
                return False
            result = True
            numbers = []            # [0]:width, [1]:height
            for match in re.finditer(r"\d+", args.geometry):
                numbers.append(int(match.group()))
            if numbers[0] < 400 or numbers[0] > 1024:
                print('out of range(window width (400-1024)): %s' % (args.geometry), file=sys.stderr)
                result = False
            if numbers[1] < 300 or numbers[1] > 1024:
                print('out of range(windows height (300-1024)): %s' % (args.geometry), file=sys.stderr)
                result = False
            if not result:
                return False
            self.numbers = numbers

        # height
        self.row_height = None # default value - accordimg to image size
        if args.row_height is not None:
            if args.row_height < 16 or args.row_height > 240:
                print('out of range(image height (16-240)): %s' % (args.row_height), file=sys.stderr)
                return False
            self.row_height = args.row_height

        # filename
        if os.path.isfile(args.csvfile) is None: # checked by argparse, so
            print('csvfile is not specified', file=sys.stderr)
            return False
        self.model = ListModel(self.display_rows, self.image_directory)
        self.model.read(args.csvfile)
        if self.model.linecount() <= 0:
            print('csv file does not have lines: %s' % (args.csvfile))
            return False

        # columns - checks corresponding between csvfile and co
        self.columns = None
        if args.columns is None:
            columns = []
            for i in range(self.model.columns()):
                columns.append('column%02d' % (i+1))
            self.columns = tuple(columns)
        else:
            if re.fullmatch(r'^((\w+)\,?)+', args.columns) is None:
                print('invalid format for columns: %s' % (args.columns))
                return False
            columns_list = args.columns.split(',')
            if len(columns_list) != self.model.columns():
                print('columns does not match with file: %s / %s' % (args.columns, args.csvfile))
                return False
            self.columns = columns_list
        # all arguments were checked.
        return True

    def get_geometry(self):
        """Retrieve geometry parameter came from argument."""
        if self.numbers is None:
            return None
        else:
            geomstr = '%dx%d' % (self.numbers[0], self.numbers[1])
            return geomstr

    def get_imagesize(self):
        """Retrieve image-size from argument or actual image file."""
        if self.imagesize_set is None:
            if self.row_height is not None:
                # get shrink ratio using row_height and real image height.
                width, height = self.model.get_imagesize()
                if self.row_height - 2 < height: # must be shrinked
                    shrink_ratio = (self.row_height - 2) / height
                    self.imagesize = (int(width * shrink_ratio), self.row_height - 2)
            self.imagesize_set = True
        return self.imagesize   # could be None

    def get_imagewidth(self):
        """Retrieve image-width to adjust column size in view."""
        imagesize = self.get_imagesize()
        width = 0
        if imagesize is None:
            width, height = self.model.get_imagesize()
        else:
            width = imagesize[0]
        retval = int(width + width/10)
        if retval < 120:
            retval = 120
        return retval

    def get_rowheight(self):
        """Retrieve row-height in displayed list(Treeview)."""
        if self.row_height is None:
            width, height = self.model.get_imagesize()
            if height > 38:
                self.row_height = height+2
            else:
                self.row_height = 40
        return self.row_height

    def get_columns(self):
        """Returns column names if those were provied in command line."""
        return self.columns     # could be None

    def launch(self):
        """Application launch code."""
        # get argparser instance
        parser = self.build_argparse()
        # parse arguments
        args = parser.parse_args()
        # check each argument
        if not self.check_argument(args):
            return False
        if self.model is None:
            return False
        path_list = self.model.get_path_list()
        if path_list is None:
            return False
        elif len(path_list) == 0:
            return False
        # launch application with view
        self.view = ListView(self, titletext='csvlistapp')
        self.view.fill_combobox(path_list)
        self.model.change_path(path_list[0])
        self.view.fill_treeview(self.model.get_imagerows(imagesize=self.get_imagesize()))
        self.view.set_status_label(self.model.get_path_info())
        self.view.mainloop()

    def combo_selected(self, combobox):
        """Callback method to have combo-box selection event."""
        def inner(event):
            nonlocal self
            self.model.change_path(combobox.get())
            self.view.fill_treeview(self.model.get_imagerows(imagesize=self.get_imagesize()))
            self.view.set_status_label(self.model.get_path_info())
        return inner

    def backward_cmd_pressed(self):
        """Callback method to have backward-command pressed event."""
        if self.model.backward():
            self.view.fill_treeview(self.model.get_imagerows(imagesize=self.get_imagesize()))
            self.view.set_status_label(self.model.get_path_info())
        else:
            pass

    def forward_cmd_pressed(self):
        """Callback method to have forward-command pressed event."""
        if self.model.forward():
            self.view.fill_treeview(self.model.get_imagerows(imagesize=self.get_imagesize()))
            self.view.set_status_label(self.model.get_path_info())
        else:
            pass

    def treeview_row_selected(self, treeview):
        def inner(event):
            nonlocal self
            self.model.row_selected(treeview.selection())
        return inner

    def treeview_ctrlc_pressed(self, treeview):
        """Callback method to have tree-view have keyboard event of Ctrl-C"""
        def inner(event):
            nonlocal self
            texts = self.model.get_row_text()
            self.view.fill_clipboard(texts)
        return inner

if __name__ == '__main__':
    app = CsvListApp()
    app.launch()
