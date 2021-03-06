#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-17.
# Based on WinInstallerExtractor by Matt Hansen
#
# msiinfo "msi" /t "String"
# Output needs work. Goal would be to return the string, if string_sinfo is not supplied
# Alternative could be the msilib SummaryInformation.GetProperty(field) functions.
# 20210517 Nick Heim: Python v3 changes

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["MSIApplySumInfo"]


class MSIApplySumInfo(Processor):
    description = "Apply summary info changes to MSI-file using msiinfo.exe."
    input_variables = {
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "cmnds_sinfo": {
            "required": True,
            "description": "Dict of Suminfo commands to execute. Pairs of key(flag)/string are expected, required",
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
        cmnds_sinfo = self.env.get('cmnds_sinfo', '')
        #print >> sys.stdout, "cmnds_sinfo %s" % cmnds_sinfo
        self.output( "cmnds_sinfo: %s" % cmnds_sinfo)
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        extract_flag = 'l'
        msiinfo_exe = os.path.join(self.env['TOOLS_DIR'], "msiinfo.exe")		

        #for key, value in cmnds_sinfo.items():
        for key, value in list(cmnds_sinfo.items()):
            self.output("Applying: %s" % msi_path)
            cmd = [msiinfo_exe, msi_path, key, value]
            #print >> sys.stdout, "cmd %s %s" % (key, value)
            self.output( "cmd %s %s" % (key, value))
            try:
                if verbosity > 1:
                    Output = subprocess.check_output(cmd)
                else:
                    Output = subprocess.check_output(cmd)
            except OSError as err:
                if ignore_errors != 'True':
                    raise ProcessorError(
                        "Could not apply %s: %s" % (cmd, err))

if __name__ == '__main__':
    processor = MSIApplySumInfo()
    processor.execute_shell()
