#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-16.
#
# Adjust an MSI-file, using msidb.exe.
# Output needs work. Goal would be to return the exitcode/errorlevel.

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["MSIDbWorker"]


class MSIDbWorker(Processor):
    description = "Wrapper around msidb.exe to work with an MSI-file."
    input_variables = {
        "mode": {
            "required": True,
            "description": "Mode of working (-e,-i,-m,-a,-r,-t,-j,-k,-x,-w)",
        },
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "workfile": {
            "required": False,
            "description": "Path to the file to work with (stream, storage, msi, transform).",
        },
        "workfolder": {
            "required": False,
            "description": "Path to the folder, where files should be written or read; Or the folder to work with table text files.",
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

        mode = self.env.get('mode',)
        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        mst_paths = self.env.get('mst_paths')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        extract_flag = 'l'
        self.output("Working on: %s" % msi_path)
        msidb_exe = os.path.join(self.env['TOOLS_DIR'], "msidb.exe")

        if mode.lower() in ["-a","-r","-t","-j","-k","-x","-w"]:
            if {"workfolder"}.issubset(self.env):
                workfolder = self.env.get('workfolder')
                os.chdir(workfolder)
            # if recipe writer gave us a single string instead of a list of strings,
            # convert it to a list of strings
            if isinstance(self.env["workfile"], basestring):
                self.env["workfile"] = [self.env["workfile"]]

            for wf_cmnd in self.env["workfile"]:
                cmd = [msidb_exe, '-d', msi_path, mode, wf_cmnd]
                if ('workfolder' in locals()) and (mode.lower() in ["-x","-w"]):
                    if os.path.isfile(os.path.join(workfolder, wf_cmnd)):
                        os.remove(os.path.join(workfolder, wf_cmnd))
                # print >> sys.stdout, "cmd %s" % cmd
                try:
                    if verbosity > 1:
                        #print >> sys.stdout, "verbosity %s" % verbosity
                        Output = subprocess.check_output(cmd)
                    else:
                        Output = subprocess.check_output(cmd)
                except:
                    if ignore_errors != 'True':
                        raise

        if mode.lower() in ["-e","-i"]:
            if {"workfolder"}.issubset(self.env):
                workfolder = self.env.get('workfolder')

            cmd_patch = [msidb_exe, '-d', msi_path, mode, '-f', workfolder]
            try:
                Output = subprocess.check_output(cmd_patch)
            except:
                if ignore_errors != 'True':
                    raise
		
if __name__ == '__main__':
    processor = MSIDbWorker()
    processor.execute_shell()
