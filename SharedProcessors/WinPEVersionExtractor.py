#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-03.
#
# Extracts version info from Windows PE-executable (.exe/.dll) file.
# 20210121 Nick Heim: Added the checkbool function to handle flag/bool checking more loosely.
#                     Added the option to get the product version.
# 20210519 Nick Heim: Python v3 changes

# pywin32 is required. Install: pip install pywin32

import os
import sys
import subprocess
from win32api import GetFileVersionInfo, LOWORD, HIWORD

from autopkglib import Processor, ProcessorError


__all__ = ["WinPEVersionExtractor"]

#https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def checkbool(v):
    # makes checking a bool argument a lot easier...
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    # end of checkbool()

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
        "product_version": {
            "required": False,
            "description": "Set this flag to get the product version instead of the file version.",
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

        if "product_version" in self.env:
            product_version = self.env.get('product_version')
            if checkbool(product_version):
                try:
                    lang, codepage = GetFileVersionInfo(exe_path, '\\VarFileInfo\\Translation')[0]
                    #strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, 'ProductVersion')
                    strInfoPath = '\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, 'ProductVersion')
                    #self.env['version'] = GetFileVersionInfo(exe_path, strInfoPath).encode('ascii', 'ignore')
                    self.env['version'] = GetFileVersionInfo(exe_path, strInfoPath)
                except:
                    if ignore_errors != 'True':
                        raise
            else:						
                try:
                    self.env['version'] = str(".".join ([str (i) for i in get_version_number (exe_path)]))
                except:
                    if ignore_errors != 'True':
                        raise
        else:						
            try:
                self.env['version'] = str(".".join ([str (i) for i in get_version_number (exe_path)]))
            except:
                if ignore_errors != 'True':
                    raise
						
        self.output("Found Version: %s" % (self.env['version']))

if __name__ == '__main__':
    processor = WinPEVersionExtractor()
    processor.execute_shell()
