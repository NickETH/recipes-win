#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-17.
# Based on WinInstallerExtractor by Matt Hansen
#
# Apply a transform to an MSI-file, using msitran.exe.
# Output needs work. Goal would be to return the exitcode/errorlevel.

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["MSIApplyTransform"]


class MSIApplyTransform(Processor):
    description = "Apply a transform to MSI-file using msitran.exe."
    input_variables = {
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "mst_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {
        "version": {
            "description": "Version of exe found." 
        },
    }

    __doc__ = description

    def main(self):

        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        mst_path = self.env.get('mst_path', self.env.get('pathname'))
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        extract_flag = 'l'

        self.output("Applying: %s" % mst_path)
        cmd = ['msitran.exe', '-a', mst_path, msi_path]

        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)
        except:
            if ignore_errors != 'True':
                raise

        archiveVersion = ""
        for line in Output.split("\n"):
            if verbosity > 2:
                print line
            if "ProductVersion:" in line:
                archiveVersion = line.split()[-1]
                continue
        
        self.env['version'] = archiveVersion.encode('ascii', 'ignore')
        self.output("Found Version: %s" % (self.env['version']))

if __name__ == '__main__':
    processor = MSIApplyTransform()
    processor.execute_shell()
