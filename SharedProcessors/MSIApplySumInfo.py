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
# 190506 Nick Heim: This version can have multiple commands! It is NOT compatible with earlier version!

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
'''        "flag_sinfo": {
            "required": True,
            "description": "Suminfo Flag, required",
        },
        "string_sinfo": {
            "required": True,
            "description": "Suminfo String, required",
        },
'''        "ignore_errors": {
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
        print >> sys.stdout, "cmnds_sinfo %s" % cmnds_sinfo
        #flag_sinfo = self.env.get('flag_sinfo', '')
        #string_sinfo = self.env.get('string_sinfo', '')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        extract_flag = 'l'
        msiinfo_exe = os.path.join(self.env['TOOLS_DIR'], "msiinfo.exe")		
        #msiinfo_exe = "msiinfo.exe"

        for key, value in cmnds_sinfo.items():
        #for key, value in cmnds_sinfo:
            self.output("Applying: %s" % msi_path)
            cmd = [msiinfo_exe, msi_path, key, value]
            print >> sys.stdout, "cmd %s %s" % (key, value)
            try:
                if verbosity > 1:
                    Output = subprocess.check_output(cmd)
                else:
                    Output = subprocess.check_output(cmd)
            except OSError, err:
                if ignore_errors != 'True':
                    raise ProcessorError(
                        "Could not apply %s: %s" % (cmd, err))

        '''
        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)
        except:
            if ignore_errors != 'True':
                raise
        #Array example JSS-Importer
		# https://github.com/grahampugh/JSSImporter/blob/master/JSSImporter.py 547
        keys = self.env.get('plist_keys')
        for key, value in request.items():
        for SQL_string in self.env["SQL_command"]:
            # print >> sys.stdout, "SQL_string %s" % SQL_command
            try:
                view = dbobject.OpenView(SQL_string)
                rec = view.Execute(None)
                self.output("Applying %s" % SQL_string)
            except OSError, err:
                raise ProcessorError(
                    "Could not apply %s: %s" % (SQL_string, err))
'''
if __name__ == '__main__':
    processor = MSIApplySumInfo()
    processor.execute_shell()
