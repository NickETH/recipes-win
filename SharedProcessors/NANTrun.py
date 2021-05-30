#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-04-03.
# Microsoft.Tools.WindowsInstallerXml.NAntTasks.dll is needed in the Wix bin directory, 
# if the NANT tasks for wix are used.
#
# Run NANT to build or to call a specific command.
# 20210519 Nick Heim: Python v3 changes

import os
import sys
import subprocess
import time

from autopkglib import Processor, ProcessorError


__all__ = ["NANTrun"]


class NANTrun(Processor):
    description = "Run NANT to build or to call a specific command."
    input_variables = {
        "run_folder": {
            "required": True,
            "description": "Path to the Wix build dir, required",
        },
        "build_target": {
            "required": False,
            "description": "Target to run in NANT-file",
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

        run_folder = self.env.get('run_folder')
        build_cmd = self.env.get('build_cmd')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        ts = time.localtime()
        us_date = time.strftime("%Y%m%d%H%M",ts)
        extract_flag = 'l'
        nant_cmd = self.env.get('NANT_PATH')
        sevenzipcmd = self.env.get('7ZIP_PATH')
        toolsdir = self.env.get('TOOLS_DIR')
        autopkglogfile = os.path.join(self.env['AUTOPKG_DIR'], 'log', ('NANT' + us_date + '.log'))

        self.output("Applying: %s" % run_folder)
        os.chdir(run_folder)
        cmd = [nant_cmd]

        if "build_target" in self.env:
            build_target = os.path.splitext(self.env.get('build_target'))[0]
            cmd.extend([build_target])

        cmd.extend(['-D:arg.7ZipCmd=' + sevenzipcmd])
        cmd.extend(['-D:arg.ToolsDir=' + toolsdir])
        cmd.extend(['-l:' + autopkglogfile])
        
        #print >> sys.stdout, "cmdline %s" % cmd
        self.output("cmdline: %s" % cmd)
        # print >> sys.stdout, "run_folder %s" % os.getcwd()
        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)

        except:
            if ignore_errors != 'True':
                raise
                #print >> sys.stdout, "Nant run %s" % Output
                self.output("Nant run: %s" % Output)

if __name__ == '__main__':
    processor = NANTrun()
    processor.execute_shell()
