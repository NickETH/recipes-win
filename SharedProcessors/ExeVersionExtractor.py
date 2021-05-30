#!/usr/bin/python
#
# Copyright 2017 The Pennsylvania State University.
#
# Created by Rusty Myers (rzm102)@psu.edu) on 2017-06-12.
# Based on WinInstallerExtractor by Matt Hansen
#
# Extracts version info from .exe file using the 7z utility.
# 20190329 Nick Heim: 7z path altered.
# 20190506 Nick Heim: path should be got from the 7ZIP_PATH variable.
# 20210517 Nick Heim: Python v3 changes

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["ExeVersionExtractor"]


class ExeVersionExtractor(Processor):
    description = "Extracts the Windows archive meta-data using 7z."
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to exe or msi, defaults to %pathname%",
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

        exe_path = self.env.get('exe_path', self.env.get('pathname'))
        verbosity = self.env.get('verbose', 0)
        ignore_errors = self.env.get('ignore_errors', True)
        extract_flag = 'l'

        sevenzipcmd = "C:\\Program Files\\7-Zip\\7z.exe"
        self.output("Extracting: %s" % exe_path)
        cmd = [sevenzipcmd, extract_flag, '-y', exe_path]

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
                print(line)
            if "ProductVersion:" in line:
                archiveVersion = line.split()[-1]
                continue
        
        self.env['version'] = archiveVersion.encode('ascii', 'ignore')
        self.output("Found Version: %s" % (self.env['version']))

if __name__ == '__main__':
    processor = ExeVersionExtractor()
    processor.execute_shell()
