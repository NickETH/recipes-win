#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-08-05.
#
# Move files from a source directory(tree) to a destination dir(tee).
# Folders in the tree are automatically created, if missing.
# The file_list file must contain relative paths to files, line by line.
#
# Output needs work. Goal would be to return the exitcode/errorlevel.
# 20210517 Nick Heim: Python v3 changes

"""See docstring for FileMoverFromList class"""

import sys
import os
import shutil
from autopkglib import Processor

__all__ = ["FileMoverFromList"]

class FileMoverFromList(Processor):
    '''Moves files from a source dir to a destination dir.
    filenames must bei provided by a listfile, line by line.'''

    input_variables = {
        "source_dir": {
            "required": True,
            "description": "Path to the Source dir, relative to pkg_dir, required",
        },
        "target_dir": {
            "required": True,
            "description": "Path to the Target dir, relative to pkg_dir, required",
        },
        "file_list": {
            "required": True,
            "description": ("Textfile containing the files to copy, line by line, required"),
        },
    }
    output_variables = {
    }

    description = __doc__

    def main(self):
        source_dir = self.env.get('source_dir')
        target_dir = self.env.get('target_dir')
        file_list = self.env.get('file_list')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if not os.path.isfile(file_list):
            self.output( "file does not exist %s" % file_list)
        with open(file_list, "r") as ifile:
            for file in ifile:
                src_name = os.path.join(source_dir, file.rstrip())
                trg_name = os.path.join(target_dir, file.rstrip())
                trg_path, working_file = os.path.split(trg_name)
                if not os.path.exists(trg_path):
                    os.makedirs(trg_path)
                if os.path.isfile(src_name):
                    shutil.move(src_name, trg_name)
                    self.output(
                        'File %s moved to %s' % (src_name, trg_name))
                else :
                    self.output( "file does not exist %s" % src_name)

if __name__ == '__main__':
    PROCESSOR = FileMoverFromList()
    PROCESSOR.execute_shell()
