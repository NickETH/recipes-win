#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-01.
#
# Extracts a resource from a setup.exe file using the ResourceHacker utility.



import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["ResourceExtractor"]


class ResourceExtractor(Processor):
    description = "Extracts a resource from a Windows exe using ResourceHacker."
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to the (setup.)exe, defaults to %pathname%",
        },
        "extract_dir": {
            "required": True,
            "description": "Output path (absolute) for the extracted archive.",
        },
        "extract_file": {
            "required": True,
            "description": "Output filename of the resource to be extracted.",
        },
        "extract_cmd": {
            "required": True,
            "description": "Resource to extract (e.g. 'BIN,123,').",
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

        exe_path = self.env.get('exe_path', self.env.get('pathname'))
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('extract_dir', 'ExtractedInstaller')
        extract_file = self.env.get('extract_file')
        extract_string = self.env.get('extract_cmd').strip('\"')
        self.output("Extract string: %s" % extract_string)
        ignore_errors = self.env.get('ignore_errors', 'False')
        verbosity = self.env.get('verbose', 0)

        reshacker_exe = os.path.join(self.env['TOOLS_DIR'], "ResourceHacker.exe")		
        self.output("Working on: %s" % exe_path)
        cmd = [reshacker_exe, '-open', exe_path, '-action', 'extract', '-mask', extract_string, '-save', (os.path.join(extract_directory, extract_file))]

        # print >> sys.stdout, "Reshacker CL %s" % cmd

        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise

        self.output("Extracted Archive Path: %s" % extract_directory)

if __name__ == '__main__':
    processor = ResourceExtractor()
    processor.execute_shell()
