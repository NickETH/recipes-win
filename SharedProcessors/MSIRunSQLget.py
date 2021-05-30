#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-18.
# Based on WinInstallerExtractor by Matt Hansen
#
# Run an SQL-Command against an MSI-file, using pythons msilib.
# Basic processor to read an arbitrary value from an MSI-file.
# 20210517 Nick Heim: Python v3 changes

import os
import sys
import subprocess
import msilib

from autopkglib import Processor, ProcessorError


__all__ = ["MSIRunSQLget"]


class MSIRunSQLget(Processor):
    description = "Run an SQL-Command SELECT against an MSI-file."
    input_variables = {
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "SQL_command": {
            "required": True,
            "description": "SQL command to run, required",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {
        "msi_value": {
            "description": "Value from the SQL run."
        },
    }

    __doc__ = description

    def main(self):

        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        SQL_command = self.env.get('SQL_command')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        tool_vbs = os.path.join(self.env['TOOLS_DIR'], "WiRunSQL.vbs")
        self.output("Applying: %s" % SQL_command)
        dbobject = msilib.OpenDatabase(msi_path, msilib.MSIDBOPEN_READONLY)
        view = dbobject.OpenView(SQL_command)
        view.Execute(None)
        rec = view.Fetch()
        msi_value = rec.GetString(1)
        #print >> sys.stdout, "Property Value %s" % msi_value
        self.output("Property Value: %s" % msi_value)

        # dbobject.Commit()
        self.env['msi_value'] = msi_value

if __name__ == '__main__':
    processor = MSIRunSQLget()
    processor.execute_shell()
