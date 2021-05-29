#!/usr/bin/python
#
# Copyright 2021 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2021-04-08.
#
# Get the hash of (a) file(s) and insert it into an MSI-file, using pythons msilib.
# File2Hash takes a single value or an array, 
# which has the key of the file in the MSI and the full path to the file.
# 20210409 Nick Heim: Added the feature to clear the version field in the MSI File table.
# 20210515 Nick Heim: Rewritten the calls to get the filehash to make sure the COM-object is loaded.

import os
import sys
import subprocess
import msilib
import win32com.client as win32
from win32com.client import makepy

from autopkglib import Processor, ProcessorError


__all__ = ["MSIAddFileHash"]

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

class MSIAddFileHash(Processor):
    description = "Get the hash of (a) file(s) and insert it into an MSI."
    input_variables = {
        "msi_path": {
            "required": True,
            "description": "Path to the msi, required",
        },
        "File2Hash": {
            "required": True,
            "description": "(Array of) File(s) with key and full path to hash, separated by '|||', required",
        },
        "remove_version_field": {
            "default": False,
            "required": False,
            "description": "Clear the version field of the file in the MSI file table.",
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
        # Generate a static COM proxy from msi.dll with the help of makepy.py
        # See: http://www.philbuckland.com/racing/a/Python/Lib/site-packages/win32com/HTML/GeneratedSupport.html
        win32.gencache.EnsureModule('{000C1092-0000-0000-C000-000000000046}', 1033, 1, 0)
        LCID = 0x409
        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        print >> sys.stdout, "msi_path %s" % msi_path
        File2Hash = self.env.get('File2Hash')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)

        WII = win32.Dispatch('WindowsInstaller.Installer', resultCLSID='{000C1090-0000-0000-C000-000000000046}')
        dbobject = msilib.OpenDatabase(msi_path, msilib.MSIDBOPEN_TRANSACT)

        if "remove_version_field" in self.env:
            remove_version_field = str(self.env.get('remove_version_field'))

        # if recipe writer gave us a single string instead of a list of strings,
        # convert it to a list of strings
        if isinstance(self.env["File2Hash"], basestring):
            self.env["File2Hash"] = [self.env["File2Hash"]]

        for Full_string in self.env["File2Hash"]:
            # print >> sys.stdout, "Full_string %s" % File2Hash
            Full_string_list = Full_string.split('|||')
            MSI_file_key = Full_string_list[0]
            File_full_path = Full_string_list[1]
            #hashresult = WII.FileHash(File_full_path, 0)
            # Syntax gotten with the makepy.py module
            hashresult = WII._oleobj_.InvokeTypes(47, LCID, 1, (9, 0), ((8, 1), (3, 1)),File_full_path, 0)
            hashresult = win32.Dispatch(hashresult, u'FileHash', '{000C1093-0000-0000-C000-000000000046}')
            #print >> sys.stdout, "Hash: %s, %d, %d, %d, %d" % (MSI_file_key, hashresult.IntegerData(1), hashresult.IntegerData(2), hashresult.IntegerData(3), hashresult.IntegerData(4))
            try:
                msilib.add_data(dbobject, "MsiFileHash",
                    [(MSI_file_key, 0, hashresult.IntegerData(1),
                     hashresult.IntegerData(2), hashresult.IntegerData(3),
                     hashresult.IntegerData(4))])
            except OSError, err:
                raise ProcessorError(
                    "Could not apply %s: %s" % (Full_string, err))
            # if remove_version_field == 'True':
            if checkbool(remove_version_field):
                try:
                    SQL_string = "UPDATE `File` SET `File`.`Version`='' WHERE `File`.`File`='{}'".format(MSI_file_key)
                    view = dbobject.OpenView(SQL_string)
                    rec = view.Execute(None)
                    self.output("Applying %s" % SQL_string)
                except OSError, err:
                    raise ProcessorError(
                        "Could not apply %s: %s" % (SQL_string, err))

        dbobject.Commit()

if __name__ == '__main__':
    processor = MSIAddFileHash()
    processor.execute_shell()
