#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-17.
# Based on WinInstallerExtractor by Matt Hansen
#
# Apply (a) transform(s) to an MSI-file, using msitran.exe.
# Output needs work. Goal would be to return the exitcode/errorlevel.
# 20210517 Nick Heim: Python v3 changes

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["MSIApplyTransform"]


class MSIApplyTransform(Processor):
    description = "Apply transform(s) to an MSI-file using msitran.exe."
    input_variables = {
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "mst_paths": {
            "required": True,
            "description": "(Array of) Paths to the mst, required",
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

        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        mst_paths = self.env.get('mst_paths', self.env.get('pathname'))
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        extract_flag = 'l'
        self.output("Working on: %s" % msi_path)
        msitran_exe = os.path.join(self.env['TOOLS_DIR'], "msitran.exe")		
        #msitran_exe = "msitran.exe"

        # if recipe writer gave us a single string instead of a list of strings,
        # convert it to a list of strings
        #if isinstance(self.env["mst_paths"], basestring):
        if isinstance(self.env["mst_paths"], str):
            self.env["mst_paths"] = [self.env["mst_paths"]]

        for mst_cmnd in self.env["mst_paths"]:
            cmd = [msitran_exe, '-a', mst_cmnd, msi_path]
            try:
                if verbosity > 1:
                    Output = subprocess.check_output(cmd)
                else:
                    Output = subprocess.check_output(cmd)
            except:
                if ignore_errors != 'True':
                    raise

if __name__ == '__main__':
    processor = MSIApplyTransform()
    processor.execute_shell()
