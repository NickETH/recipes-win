#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-04-03.
# Based on WinInstallerExtractor by Matt Hansen
#
# Run NANT to build or to call a specific command.

import os
import sys
import subprocess

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
        extract_flag = 'l'
        nant_cmd = self.env.get('NANT_PATH')

        self.output("Applying: %s" % run_folder)
        os.chdir(run_folder)
        cmd = [nant_cmd]

        if "build_target" in self.env:
            build_target = os.path.splitext(self.env.get('build_target'))[0]
            cmd.extend([build_target])

        cmd.extend(['-l:C:\Tools\AutoPKG.new\log\NANT.log'])
        print >> sys.stdout, "cmdline %s" % cmd
        # print >> sys.stdout, "run_folder %s" % os.getcwd()
        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)

        except:
            if ignore_errors != 'True':
                raise
                print >> sys.stdout, "Nant run %s" % Output

if __name__ == '__main__':
    processor = NANTrun()
    processor.execute_shell()
