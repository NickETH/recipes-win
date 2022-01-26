#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-22.
#
# Extracts a resource from a Wix based setup.exe file using the Dark.exe utility.
# Wix Toolset needs to be installed and in the path.



from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["WixDarkExtractor"]


class WixDarkExtractor(Processor):
    description = "Extracts a resource from a Wix based exe using Dark."
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to the (setup.)exe, defaults to %pathname%",
        },
        "extract_dir": {
            "required": True,
            "description": "Output path (absolute) for the extracted archive.",
        },
        "xtract_file": {
            "required": False,
            "description": "Output filename of the resource to be extracted.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):

        exe_path = self.env.get('exe_path', self.env.get('pathname'))
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('extract_dir', '.')
        ignore_errors = self.env.get('ignore_errors', 'False')
        verbosity = self.env.get('verbose', 0)

        dark_exe = os.path.join(self.env['DTF_PATH'], "..\\bin\\Dark.exe")
        # dark_exe = "Dark.exe"
        cmd = [dark_exe, '-x', extract_directory, exe_path,]

        if {"xtract_file"}.issubset(self.env):
            xtract_file = self.env.get('xtract_file')
            cmd.extend([xtract_file])

        self.output("Working on: %s" % exe_path)

        print("Dark CL %s" % cmd, file=sys.stdout)

        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise

        self.output("Extracted Archive Path: %s" % extract_directory)

if __name__ == '__main__':
    processor = WixDarkExtractor()
    processor.execute_shell()
