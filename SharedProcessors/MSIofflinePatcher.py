#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-04-12.
#
# Needs 'WiMkCab2.vbs' from the Installer SDK to be in the TOOLS_DIR.
# Depends on the 'WiX Toolset SDK' in DTF_PATH.
# Apply a patch file to an MSI offline or compact (rebuild) an MSI-file.
# Compress an uncompressed MSI installation into a CAB-file and embed it into the MSI-file, if necessary.
# Create folders, copy needed files from repository and/or previous build.
# Output needs work. Goal would be to return the exitcode/errorlevel.
# 20190520 Nick Heim: Changed the creation of "new_msi_path" right before patching.
#					Check explicitly for "embed_cab" and "new_packcode" for boolean 'True'
#					Added the cab_dir variable to explicit set the location of the new cabfile.
# 20190522 Nick Heim: Added the checkbool function to handle flag/bool checking more loosely.
# 20190702 Nick Heim: Added the compress only function (no patching). Bugfix on 'checkbool'
# 20190815 Nick Heim: Added the compact function.
# 20190823 Nick Heim: Fixed the patching function.
# 20210517 Nick Heim: Python v3 changes

import os
import sys
import shutil
import subprocess
import msilib
import time
import argparse

from autopkglib import Processor, ProcessorError


__all__ = ["MSIofflinePatcher"]

def get_bit(value, n):
    return ((value >> n & 1) != 0)

def set_bit(value, n):
    return value | (1 << n)

def clear_bit(value, n):
    return value & ~(1 << n)

#https://stackoverflow.com/questions/21044992/how-to-close-msi-db-opened-by-python-msilib
# This results in creating this (sub-) functions
def msi_suminfo_set(filepath, propery, value):
    # global db
    db = msilib.OpenDatabase(filepath, msilib.MSIDBOPEN_DIRECT)
    summaryinformation = db.GetSummaryInformation(1)
    summaryinformation.SetProperty(propery, value)
    summaryinformation.Persist()
    # end of msi_suminfo_set()

def msi_suminfo_get(filepath, propery, type):
    # global db
    db = msilib.OpenDatabase(filepath, msilib.MSIDBOPEN_READONLY)
    summaryinformation = db.GetSummaryInformation(1)
    if type == 'int':
        value = int(summaryinformation.GetProperty(propery))
    else:
        value = summaryinformation.GetProperty(propery)
    return value
    # end of msi_suminfo_get()

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
	
class MSIofflinePatcher(Processor):
    description = "Apply an patch to an MSI file offline and rebuild the package."
    input_variables = {
        "pkg_dir_abs": {
            "required": True,
            "description": "Absolute path to the pkg_dir, required",
        },
        "msi_path": {
            "required": True,
            "description": "Path to the MSI-file, relative to pkg_dir, required",
        },
        "msp_path": {
            "required": False,
            "description": "Path to the MSP-file, relative to pkg_dir, omit for cabs in or compress only",
        },
        "compact_msi": {
            "default": False,
            "required": False,
            "description": "Compact the MSI-file",
        },
        "adm_msi_path": {
            "required": True,
            "description": "Path to the MSI-file to be patched, relative to pkg_dir, required",
        },
        "new_msi_path": {
            "required": True,
            "description": "Path to the new MSI-file, relative to pkg_dir, required",
        },
        "cab_file": {
            "required": True,
            "description": "Name of the CAB-file to generate.",
        },
        "cab_dir": {
            "required": False,
            "description": "Folder where the CAB-file should be generated, relative to pkg_dir.",
        },
        "embed_cab": {
            "default": False,
            "required": False,
            "description": "Embed the cabinet file in the MSI-file",
        },
        "new_packcode": {
            "default": False,
            "required": False,
            "description": "Set a new packagecode in the MSI-file",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the run.",
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):

        pkg_dir_abs = self.env.get('pkg_dir_abs')
        msi_file = os.path.join(pkg_dir_abs, self.env.get('msi_path'))
        adm_msi_path = os.path.join(pkg_dir_abs, self.env.get('adm_msi_path'))
        new_msi_path = os.path.join(pkg_dir_abs, self.env.get('new_msi_path'))

        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 5)
        #print >> sys.stdout, "pkg_dir_abs %s" % pkg_dir_abs
        self.output("pkg_dir_abs %s" % pkg_dir_abs)

        self.output("Creating: %s" % new_msi_path)
        sharedproc_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = "TARGETDIR=" + (os.path.join(pkg_dir_abs, 'adm'))
        msiexec = "msiexec.exe"
        tool_vbs = os.path.join(self.env['TOOLS_DIR'], "WiMkCab2.vbs")
        cscript_exe ="cscript.exe"

        # Build the msiexec command to generate an admin install
        cmd_admin = [msiexec, '/a', msi_file, target_dir, '/qn',]
        try:
            Output = subprocess.check_output(cmd_admin)
        except:
            if ignore_errors != 'True':
                raise
        if "compact_msi" in self.env:
            compact_msi = self.env.get('compact_msi')
            if checkbool(compact_msi):
                msi_temp = os.path.join(pkg_dir_abs, 'temp')
                if not os.path.isdir(msi_temp):			        
                    os.mkdir(msi_temp)
                #assembly_path = r"C:\Program Files (x86)\WiX Toolset v3.14\SDK"
                sys.path.append(self.env['DTF_PATH'])
                import clr
                clr.AddReference("Microsoft.Deployment.WindowsInstaller")
                from Microsoft.Deployment.WindowsInstaller import Database
                from Microsoft.Deployment.WindowsInstaller import DatabaseOpenMode
                tmode = DatabaseOpenMode.ReadOnly
                try:
                   WIdb = Database(adm_msi_path, tmode)
                   WIdb.ExportAll(msi_temp)
                   WIdb.Dispose()
                except:
                   pass
                #print >> sys.stdout, "end of export"
                self.output("end of export")
                # Create a new MSI-file.
                tmode = DatabaseOpenMode.CreateDirect
                WIdbnew = Database(new_msi_path, tmode)
                WIdbnew.ImportAll(msi_temp)
                WIdbnew.Dispose()
            else:
                shutil.copy(adm_msi_path, new_msi_path)

        if {"msp_path"}.issubset(self.env):
            msp_file = os.path.join(pkg_dir_abs, self.env.get('msp_path'))
            cmd_patch = [msiexec, '/p', msp_file, '/a', new_msi_path, target_dir, '/qn',]
            try:
                Output = subprocess.check_output(cmd_patch)
            except:
                if ignore_errors != 'True':
                    raise
        
        if {"new_msi_path", "cab_file"}.issubset(self.env):
            cab_file = self.env.get('cab_file')
            if ("cab_dir" in self.env):
                os.chdir(os.path.join(pkg_dir_abs, self.env.get('cab_dir')))
            cmd_cabin = [cscript_exe, tool_vbs, new_msi_path, cab_file, '/L', '/C', '/U', ]
            # print >> sys.stdout, "embed_cab %s" % type(self.env.get('embed_cab'))

            if "embed_cab" in self.env:
                embed_cab = self.env.get('embed_cab')
                #print >> sys.stdout, "embed_cab %s" % embed_cab
                self.output("embed_cab %s" % embed_cab)
                if checkbool(embed_cab):
                    cmd_cabin.extend(['/E'])
                    #print >> sys.stdout, "cmdline %s" % cmd_cabin
                    self.output("cmdline: %s" % cmd_cabin)
            try:
                Output = subprocess.check_output(cmd_cabin)
            except:
                if ignore_errors != 'True':
                    raise
    
            # Set the CABS-in flag
		    # See URLDownloader L317
            if checkbool(embed_cab):
                wcount = msi_suminfo_get(new_msi_path, msilib.PID_WORDCOUNT, 'int')
                #print >> sys.stdout, "wcount %s" % wcount
                if not get_bit(wcount, 1):
                    wcount = set_bit(wcount, 1)
                if get_bit(wcount, 2):
                    wcount = clear_bit(wcount, 2)
                #print >> sys.stdout, "wcount %s" % wcount
                self.output("wcount %s" % wcount)
                try:
                    msi_suminfo_set(new_msi_path, msilib.PID_WORDCOUNT, wcount)
                except OSError as err:
                    raise ProcessorError("Can't create %s:" % (err))

        # Set new package GUID
        if "new_packcode" in self.env:
            new_packcode = self.env.get('new_packcode')
            if checkbool(new_packcode):
                new_package_GUID = "{" + msilib.UuidCreate().upper() + "}"
                #print >> sys.stdout, "new_package_GUID %s" % new_package_GUID
                self.output("new_package_GUID %s" % new_package_GUID)
                try:
                    msi_suminfo_set(new_msi_path, msilib.PID_REVNUMBER, new_package_GUID)
                except OSError as err:
                    raise ProcessorError("Can't create %s:" % (err))

        # Remove the adminProperties stream, if there
        dbobj = msilib.OpenDatabase(new_msi_path, msilib.MSIDBOPEN_TRANSACT)
        view = dbobj.OpenView("SELECT `Name` FROM _Streams WHERE `Name` = ?")
        DelRecord = msilib.CreateRecord(2)
        DelRecord.SetString(1, 'AdminProperties')
        view.Execute(DelRecord)
        try:
            DelRecord = view.Fetch()
            view.Modify(msilib.MSIMODIFY_DELETE, DelRecord)
        except:
            pass
        dbobj.Commit()


if __name__ == '__main__':
    processor = MSIofflinePatcher()
    processor.execute_shell()
