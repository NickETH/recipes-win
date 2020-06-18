#!/usr/bin/python
#
# Copyright 2020 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2020-05-31.
#
# Execute a file.
# With the "elevated" flag, it is possible to run commands that would otherwise raise an elevation popup.
# This function needs the AutoPkg Taskrunner utility, which is only available from v2.x

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import time
import subprocess
# import ctypes
import _winreg

from autopkglib import Processor, ProcessorError


__all__ = ["ExecuteFile"]

#https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def checkbool(v):
    # makes checking a bool argument a lot easier...
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    # end of checkbool()

def reg_read(path, root=_winreg.HKEY_CURRENT_USER):
    path, name = os.path.split(path)
    with _winreg.OpenKey(root, path) as key:
        return _winreg.QueryValueEx(key, name)[0]

def reg_write(path, value, root=_winreg.HKEY_CURRENT_USER):
    path, name = os.path.split(path)
    with _winreg.OpenKey(root, path, 0, _winreg.KEY_WRITE) as key:
        _winreg.SetValueEx(key, name, 0, _winreg.REG_SZ, value)

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
        "run_elevated": {
            "default": False,
            "required": False,
            "description": "Run the EXE with elevated priviliges",
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

        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)
        exe_file = self.env.get('exe_file')
        print("exe_file: %s" % exe_file)
        cmd = [exe_file.encode('utf-8')]

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

            cmd_args = [''.encode('utf-8')]
            for arg_cmnd in self.env["cmdline_args"]:
                cmd_args.extend([arg_cmnd.encode('utf-8')])
                print("cmd_args: %s" % cmd_args)

        if "run_elevated" in self.env:
            run_elevated = self.env.get('run_elevated')
            print("run_elevated: %s" % run_elevated)
            if checkbool(run_elevated):
                try:
                    comnd_value = ''.join(cmd) + '~~~' + (' '.join(cmd_args)).lstrip()
                    taskrunnerpath = 'Software\AutoPkg\TaskRunner\Command'
                    print("TaskRunnerCommand: %s" % comnd_value)
                    reg_write(taskrunnerpath, comnd_value)
                except BaseException as err:
                    raise ProcessorError(
                        "Can't write command to %s: %s" % (taskrunnerpath, err)
                    )
                while (reg_read(taskrunnerpath) != "0"):
                    time.sleep(5)

            else:
                print("cmdline %s" % (' '.join(cmd + cmd_args)), file=sys.stdout)
                try:
                    if verbosity > 1:
                        Output = subprocess.check_output(' '.join(cmd + cmd_args))

                    else:
                        Output = subprocess.check_output(' '.join(cmd + cmd_args))
                except:
                    if ignore_errors != 'True':
                        raise
                        print("Execution result %s" % Output, file=sys.stdout)

if __name__ == '__main__':
    processor = ExecuteFile()
    processor.execute_shell()
