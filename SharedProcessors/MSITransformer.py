#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-16.
#
# Apply (a) or generate (g) transform(s) to/from an MSI-file(s), using msitran.exe.
# Output needs work. Goal would be to return the exitcode/errorlevel.

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["MSITransformer"]


class MSITransformer(Processor):
    description = "Generate or Apply transform(s) to/from (an) MSI-file(s) using msitran.exe."
    input_variables = {
        "mode": {
            "required": False,
            "description": "Mode of working -a/-g (Apply/Generate), defaults to '-a'",
        },
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "msi_path_new": {
            "required": False,
            "description": "Path to the new changed msi, when generating an MST.",
        },
        "mst_paths": {
            "required": True,
            "description": "(Array of) path(s) to the mst (on Apply) or output mst, when generating, required",
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

        mode = self.env.get('mode', '-a')
        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        #msi_path_new = self.env.get('msi_path_new')
        mst_paths = self.env.get('mst_paths')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        extract_flag = 'l'
        self.output("Working on: %s" % msi_path)
        msitran_exe = os.path.join(self.env['TOOLS_DIR'], "msitran.exe")		
        #msitran_exe = "msitran.exe"

        if mode.lower().startswith('-a'):
            # if recipe writer gave us a single string instead of a list of strings,
            # convert it to a list of strings
            if isinstance(self.env["mst_paths"], basestring):
                self.env["mst_paths"] = [self.env["mst_paths"]]

            for mst_cmnd in self.env["mst_paths"]:
                cmd = [msitran_exe, '-a', mst_cmnd, msi_path]
                # print >> sys.stdout, "cmd %s" % cmd
                try:
                    if verbosity > 1:
                        Output = subprocess.check_output(cmd)
                    else:
                        Output = subprocess.check_output(cmd)
                except:
                    if ignore_errors != 'True':
                        raise

        elif mode.lower().startswith('-g'):
            if {"msi_path_new"}.issubset(self.env):
                msi_path_new = self.env.get('msi_path_new')

            cmd = [msitran_exe, '-g', msi_path, msi_path_new, mst_paths]
            try:
                Output = subprocess.check_output(cmd)
            except:
                if ignore_errors != 'True':
                    raise
		
if __name__ == '__main__':
    processor = MSITransformer()
    processor.execute_shell()
