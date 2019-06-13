#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-18.
#
# Run an SQL-Command against an MSI-file, using pythons msilib.
# Needs some work around error handling.

import os
import sys
import subprocess
import msilib

from autopkglib import Processor, ProcessorError


__all__ = ["MSIRunSQL"]


class MSIRunSQL(Processor):
    description = "Run an SQL-Command against an MSI-file."
    input_variables = {
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "SQL_command": {
            "required": True,
            "description": "(Array of) SQL command(s) to run, required",
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
        print >> sys.stdout, "msi_path %s" % msi_path
        SQL_command = self.env.get('SQL_command')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        # print >> sys.stdout, "SQL_command %s" % SQL_command
        dbobject = msilib.OpenDatabase(msi_path, msilib.MSIDBOPEN_TRANSACT)

        # if recipe writer gave us a single string instead of a list of strings,
        # convert it to a list of strings
        if isinstance(self.env["SQL_command"], basestring):
            self.env["SQL_command"] = [self.env["SQL_command"]]

        for SQL_string in self.env["SQL_command"]:
            # print >> sys.stdout, "SQL_string %s" % SQL_command
            try:
                view = dbobject.OpenView(SQL_string)
                rec = view.Execute(None)
                self.output("Applying %s" % SQL_string)
            except OSError, err:
                raise ProcessorError(
                    "Could not apply %s: %s" % (SQL_string, err))

        dbobject.Commit()

if __name__ == '__main__':
    processor = MSIRunSQL()
    processor.execute_shell()
