#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-04-06.
#
# Calls AcrobatGUIDPatcher.ps1 to generate an new GUID, based on the version string. 

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["AcrobatGUIDPatcher"]


class AcrobatGUIDPatcher(Processor):
    description = "Generate an new GUID, based on the version string."
    input_variables = {
        "base_GUID": {
            "required": True,
            "description": "GUID of the product's base version, required",
        },
        "new_ver": {
            "required": True,
            "description": "Version string, to patch into the GUID, required",
        },
        "old_hex_ver": {
            "required": True,
            "description": "Old hex version string to exchange, required",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the run.",
        },
    }
    output_variables = {
        "newGUID": {
            "description": "New GUID."
        }
    }

    __doc__ = description

    def main(self):

        base_GUID = self.env.get('base_GUID')
        new_ver = self.env.get('new_ver')
        old_hex_ver = self.env.get('old_hex_ver')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 5)

        self.output("Working on: %s" % base_GUID)
        sharedproc_dir = os.path.dirname(os.path.realpath(__file__))
        ps_script = os.path.join(sharedproc_dir, 'AcrobatGUIDPatcher.ps1')
        powershell = "C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        # Call the powershell script with its arguments.
        cmd = [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
            ps_script,
            base_GUID,
            new_ver,
            old_hex_ver,]

        print >> sys.stdout, "cmdline %s" % cmd
        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)
        except:
            if ignore_errors != 'True':
                raise
        #print >> sys.stdout, "cmdline Output %s" % Output
        #self.env['pkg_dir'] = Output
		
        archiveVersion = ""
        for line in Output.split("\n"):
            if verbosity > 2:
                print line
            if "New GUID:" in line:
                archiveVersion = line.split()[-1]
                continue
        
        self.env['newGUID'] = archiveVersion.encode('ascii', 'ignore')
        self.output("New GUID: %s" % (self.env['newGUID']))

if __name__ == '__main__':
    processor = AcrobatGUIDPatcher()
    processor.execute_shell()
