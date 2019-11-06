#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-03.
#
# Extracts version info from Windows PE-executable (.exe/.dll) file.


import os
import sys
import subprocess
from win32api import GetFileVersionInfo, LOWORD, HIWORD

from autopkglib import Processor, ProcessorError


__all__ = ["WinPEVersionExtractor"]

def get_version_number (filename):
    try:
        info = GetFileVersionInfo (filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return HIWORD (ms), LOWORD (ms), HIWORD (ls), LOWORD (ls)
    except:
        return 0,0,0,0

class WinPEVersionExtractor(Processor):
    description = "Extracts version info from Windows PE-executable (.exe/.dll) file."
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

        # print ".".join ([str (i) for i in get_version_number (exe_path)])

        try:
            self.env['version'] = ".".join ([str (i) for i in get_version_number (exe_path)])
        except:
            if ignore_errors != 'True':
                raise
     
        self.output("Found Version: %s" % (self.env['version']))

if __name__ == '__main__':
    processor = WinPEVersionExtractor()
    processor.execute_shell()
