#!/usr/bin/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-02-13.
#
# Extracts the .exe or .msi file using the 7z utility.
# Extended version of WinInstallerExtractor.
# Added possibility to specifiy the file(s) to extract.
# Extended by Nick Heim (heim)@ethz.ch) on 2019-03-28.
# Changed the extract dir to an absolute path.
# Added possibility to specifiy recursive (20191121,Hm).
# Added possibility to specifiy archive type (20200118,Hm).
# Added the checkbool function to handle flag/bool checking more loosely (20200207,Hm).
# 20210517 Nick Heim: Python v3 changes

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["SevenZipExtractor"]

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

class SevenZipExtractor(Processor):
    description = "Extracts the Windows archive meta-data using 7z."
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to exe or msi, defaults to %pathname%",
        },
        "preserve_paths": {
            "required": False,
            "description": "eXtract archive with full paths, defaults to 'True'",
        },
        "extract_dir": {
            "required": True,
            "description": "Output path (absolute) for the extracted archive.",
        },
        "extract_file": {
            "required": False,
            "description": "File to extracted or a @listfile.txt.",
        },
        "ignore_pattern": {
            "required": False,
            "description": "Wildcard pattern to ignore files from the archive.",
        },
        "archive_type": {
            "required": False,
            "description": "Specifies the type of archive. See 7-Zip help.",
        },
        "recursive": {
            "required": False,
            "description": "Search the archive recursively, defaults to 'False'",
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
        preserve_paths = self.env.get('preserve_paths', 'True')
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('extract_dir', 'ExtractedInstaller')
        extract_file = self.env.get('extract_file')
        ignore_pattern = self.env.get('ignore_pattern', '')
        archive_type = self.env.get('archive_type', '')
        ignore_errors = self.env.get('ignore_errors', 'False')
        verbosity = self.env.get('verbose', 0)

        # Set extract command
        self.output("preserve_paths v: %s" % preserve_paths)
        extract_flag = 'x' if checkbool(preserve_paths) else 'e'
        self.output("extract_flag n: %s" % extract_flag)

        # sevenzipcmd = "C:\\Program Files\\7-Zip\\7z.exe"
        sevenzipcmd = self.env.get('7ZIP_PATH')
        self.output("Extracting: %s" % exe_path)
        # cmd = [sevenzipcmd, extract_flag, '-y', '-o%s' % extract_path , exe_path]
        cmd = [sevenzipcmd, extract_flag, '-y', '-o%s' % extract_directory , exe_path]

        if extract_file:
            cmd.append('%s' % extract_file)

        if ignore_pattern:
            cmd.append('-x!%s' % ignore_pattern)

        if archive_type:
            cmd.append('-t%s' % archive_type)

        # Set recursive switch
        if "recursive" in self.env:
            recursive = self.env.get('recursive')
            if checkbool(recursive):
                cmd.append('-r')

        # print >> sys.stdout, "7z CL %s" % cmd

        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise

        # self.output("Extracted Archive Path: %s" % extract_path)
        self.output("Extracted Archive Path: %s" % extract_directory)

if __name__ == '__main__':
    processor = SevenZipExtractor()
    processor.execute_shell()
