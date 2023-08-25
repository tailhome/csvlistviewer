""" Data model for csv file viewer application. """

import sys
import os
import csv
from csvlistview import ListRow
from PIL import Image
import tkinter as tk

class ListModel:
    def __init__(self, display_rows = 10, image_directory = None):
        """ Only instance variable initialization. """
        self.display_rows = display_rows
        self.image_directory = image_directory
        self.lines = None
        self.indexes = None
        self.current_pos = 0
        self.path_list = None
        self.path_indexes = None
        self.selected_path = None
        self.imagebase = None   # default - read from current directory

    def read(self, filename):
        """ Read csv file and stores contents to instance variables. """
        try:
            f = open(filename, 'r')
        except OSError as e:
            print(e)
            sys.exit(1)
        else:
            # (re-)initialize members
            self.indexes = []
            self.currnt_pos = 0
            self.selected_path = None
            # initialize members to fill data
            self.path_list = []
            self.lines = []
            self.path_indexes = {}
            path_set = set()
            reader = csv.reader(f, delimiter=',', skipinitialspace=True)
            for i, row in enumerate(reader):
                if len(row) > 0:
                    self.lines.append(tuple(row))
                    dirname = os.path.dirname(row[0])
                    path_set.add(dirname)
                    if dirname in self.path_indexes:
                        self.path_indexes[dirname].append(i)
                    else:
                        self.path_indexes[dirname] = [i]
                else:
                    self.lines.append(()) # empty tuple
                # self.path_indexes will be used by change_path method.
            self.path_list = list(path_set)
            self.path_list.sort()

            if len(self.path_list) <= 0:
                print('csv file does not have valid lines: %s' % (filename), file=sys.stderr)
                sys.exit(1)

    def columns(self):
        """ Returns number of columns of csv file. """
        if self.lines is None:
            return 0
        elif len(self.lines) == 0:
            return 0
        return len(self.lines[0])

    def linecount(self):
        """ Returns number of lines of csv file. """
        if self.lines is None:
            return 0
        return len(self.lines)

    def get_path_list(self):
        """ Returns image path-list. """
        return self.path_list

    def change_path(self, path):
        """ Change selected path of this instance. """
        if path in self.path_list:
            self.current_pos = 0
            self.indexes = self.path_indexes[path]
            self.selected_path = path
            return True
        else:
            return False

    def get_imagesize(self):
        """ Retrieve image-size from first image file. """
        for path in self.path_list:
            for i in range(len(self.path_indexes[path])):
                if self.image_directory is None:
                    filename = self.lines[self.path_indexes[path][i]][0]
                else:
                    filename = os.path.join(self.image_directory, self.lines[self.path_indexes[path][i]][0])
                if os.path.exists(filename):
                    image = Image.open(filename)
                    return image.size

    def get_imagerows(self, pos=-1, imagesize=None):
        """ Retrieve ListRow array with specified conditions in this instance."""
        if self.selected_path is None or len(self.indexes) == 0:
            # unable to create ListRow object
            return None
        if len(self.indexes) <= pos:
            # position is out of range within self.indexes
            return None

        # usually position is not provided, so use like following instead.
        if pos < 0:
            pos = self.current_pos
        rows = []

        # read image file, then create ListRow instance with image and csv file line.
        for i in range(pos, pos + self.display_rows):
            if i >= len(self.indexes):
                break
            if self.image_directory is None:
                filename = self.lines[self.indexes[i]][0]
            else:
                filename = os.path.join(self.image_directory, self.lines[self.indexes[i]][0])
            image = Image.open(filename)
            if imagesize is not None:
                shrinked_image = image.resize(imagesize)
                image = shrinked_image
            row = ListRow(image, self.lines[self.indexes[i]])
            rows.append(row)
        return rows

    def get_position(self):
        """ Get position in selected self.indexes. """
        return self.current_pos

    def get_path_info(self):
        """ Make string for position display, like 0-9/50. """
        start = self.current_pos
        end = self.current_pos + self.display_rows - 1
        total = len(self.path_indexes[self.selected_path])
        if end >= total:
            end = total - 1
        path_info = 'Position: %d - %d / %d' % (start+1, end+1, total)
        return path_info

    def forward(self):
        """ Move forward in this model. """
        if self.selected_path is None or len(self.indexes) == 0:
            return False
        if self.current_pos + self.display_rows >= len(self.indexes):
            # unable to move forward
            return False
        else:
            self.current_pos += self.display_rows
        return True

    def backward(self):
        """ Move backward in this model. """
        if self.selected_path is None or len(self.indexes) == 0:
            return False
        self.current_pos -= self.display_rows
        if self.current_pos < 0:
            self.current_pos = 0
        return True

# if __name__ == '__main__':
#     model = ListModel()
#     model.read('test.csv')
#     print(model.get_path_list())
#     model.change_path('uma')
#     print(model.get_imagerows())
#     model.change_path('ushi')
#     print(model.get_imagerows())
#     model.change_path('tori')
#     print(model.get_imagerows())
