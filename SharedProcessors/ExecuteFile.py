#!/usr/bin/python
#
# Copyright 2020 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2020-05-31.
#
# Execute a file.
# MSBuild.exe [Optionen] [Projektdatei]
# MSBuild MyApp.csproj -t:Clean -p:Configuration=Debug;TargetFrameworkVersion=v3.5

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["ExecuteFile"]


class ExecuteFile(Processor):
    description = "Run an executable file (with arguments) (in a given directory)."
    input_variables = {
        "exe_file": {
            "required": True,
            "description": "Full path to the file to execute, required",
        },
        "exe_folder": {
            "required": False,
            "description": "Path to the dir, where the file should be executed",
        },
        "cmdline_args": {
            "required": False,
            "description": "(Array of) argument(s) to the command line",
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

        exe_file = self.env.get('exe_file')
        cmd = self.env.get('exe_file')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)

        cmd = [exe_file.encode('utf-8')]
        # cmd = [exe_file]

        if "exe_folder" in self.env:
            exe_folder = self.env.get('exe_folder')
            self.output("Executing in: %s" % exe_folder)
            if not os.path.isdir(exe_folder):			        
                os.mkdir(exe_folder)
            os.chdir(exe_folder)

        if "cmdline_args" in self.env:
            # if recipe writer gave us a single string instead of a list of strings,
            # convert it to a list of strings
            if isinstance(self.env["cmdline_args"], basestring):
                self.env["cmdline_args"] = [self.env["cmdline_args"]]

            for arg_cmnd in self.env["cmdline_args"]:
                cmd.extend([arg_cmnd.encode('utf-8')])
                # print >> sys.stdout, "cmd %s" % cmd

        print("cmdline %s" % (' '.join(cmd)), file=sys.stdout)
        # print >> sys.stdout, "run_folder %s" % os.getcwd()
        try:
            if verbosity > 1:
                #Output = subprocess.check_output(cmd)
                #Output = subprocess.Popen(' '.join(cmd))
                Output = subprocess.check_output(' '.join(cmd))
            else:
                #Output = subprocess.check_output(cmd)
                Output = subprocess.Popen(' '.join(cmd))
        except:
            if ignore_errors != 'True':
                raise
                print("Execution result %s" % Output, file=sys.stdout)

if __name__ == '__main__':
    processor = ExecuteFile()
    processor.execute_shell()
