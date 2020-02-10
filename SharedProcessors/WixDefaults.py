#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-04-06.
# Based on WinInstallerExtractor by Matt Hansen
#
# Set up a build environment. 
# Create folders, copy needed files from repository and/or previous build.
# Output needs work. Goal would be to return the exitcode/errorlevel.
# 20190401 Nick Heim: PrevVerFiles is untested!

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["WixDefaults"]


class WixDefaults(Processor):
    description = "Create version and default property files for the next WIX-build."
    input_variables = {
        "build_dir": {
            "required": True,
            "description": "Path to the build_dir, required",
        },
        "build_ver": {
            "required": True,
            "description": "Version string, that we are using to build the package, required",
        },
        "org_ver": {
            "required": False,
            "description": "Original version string",
        },
        "prop_file": {
            "required": False,
            "description": "XMLfile, containing additional build properties.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the run.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):

        build_dir = self.env.get('build_dir')
        build_ver = self.env.get('build_ver')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 5)

        self.output("Working on: %s" % build_dir)
        sharedproc_dir = os.path.dirname(os.path.realpath(__file__))
        ps_script = os.path.join(sharedproc_dir, 'WixDefaults.ps1')
        powershell = "C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        # Call the powershell script with its arguments.
        cmd = [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
            ps_script,
            build_dir,
            build_ver,]

        if "org_ver" in self.env:
            org_ver = self.env.get('org_ver')
            cmd.extend(['-org_ver', org_ver])

        if "prop_file" in self.env:
            prop_file = self.env.get('prop_file')
            cmd.extend(['-prop_file', prop_file])

			# print >> sys.stdout, "cmdline %s" % cmd
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
                print(line)
            if "Buildversion:" in line:
                archiveVersion = line.split()[-1]
                continue
        
        #self.env['build_ver'] = archiveVersion.encode('ascii', 'ignore')
        #self.output("New build_ver: %s" % (self.env['build_ver']))

if __name__ == '__main__':
    processor = WixDefaults()
    processor.execute_shell()
