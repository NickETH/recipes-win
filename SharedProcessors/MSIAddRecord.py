#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-18.
# Based on WinInstallerExtractor by Matt Hansen
#
# Run an SQL-Command against an MSI-file, using WiRunSQL.vbs.
# Output needs work. Goal would be to return the exitcode/errorlevel.

import os
import sys
import subprocess
import HTMLParser
import msilib

from autopkglib import Processor, ProcessorError


__all__ = ["MSIRunSQL"]


class MSIRunSQL(Processor):
    description = "Run an SQL-Command against an MSI-file, using WiRunSQL.vbs."
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
    }

    __doc__ = description

    def main(self):

        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        SQL_command = self.env.get('SQL_command')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        tool_vbs = os.path.join(self.env['TOOLS_DIR'], "WiRunSQL.vbs")
        self.output("Applying: %s" % SQL_command)
        # print >> sys.stdout, "SQL_command ext %s" % SQL_command
        dbobject = msilib.OpenDatabase(msi_path, msilib.MSIDBOPEN_TRANSACT)
        view = dbobject.OpenView(SQL_command)
        rec = view.Execute(None)
        dbobject.Commit()

if __name__ == '__main__':
    processor = MSIRunSQL()
    processor.execute_shell()
