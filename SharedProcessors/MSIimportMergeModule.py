#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-08-12.
#
# Import a merge module into an MSI-file.
# Prerequisites: Libraries: pythonnet, msl-loadlib, comtypes; DTF_PATH; regsvr32 <Path to>\mergemod64.dll (from Windows SDK x64, mergemod.dll)
# Work to do: This works currently only with MSMs that have files with them. Implement handling for optional file import.
# 210517 Nick Heim: Python v3 changes

import os
import sys
import shutil
import subprocess
import msilib
import time
import argparse
from msl.loadlib import LoadLibrary
from autopkglib import Processor, ProcessorError


__all__ = ["MSIimportMergeModule"]

class MSIimportMergeModule(Processor):
    description = "Import a MergeModule into a MSI file."
    input_variables = {
        "pkg_dir_abs": {
            "required": True,
            "description": "Absolute path to the pkg_dir, required",
        },
        "msi_path": {
            "required": True,
            "description": "Path to the MSI-file, relative to pkg_dir, required",
        },
        "msm_path": {
            "required": True,
            "description": "Path to the MSM-file, relative to pkg_dir, required",
        },
        "msm_feature": {
            "required": True,
            "description": "Feature in the MSI-file to connect the MSM to, required",
        },
        "msm_dir": {
            "required": True,
            "description": "Directory in the MSI-file to install the MSM, required",
        },
        "temp_path": {
            "required": False,
            "description": "Path to store the temporary build files.",
        },
        "log_file_abs": {
            "required": False,
            "description": "Absolute path to the merge log file.",
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
        msm_file = os.path.join(pkg_dir_abs, self.env.get('msm_path'))
        msm_feature = self.env.get('msm_feature')
        msm_dir = self.env.get('msm_dir')
        temp_path = os.path.join(pkg_dir_abs, self.env.get('temp_path', 'temp'))

        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 5)
        #print >> sys.stdout, "pkg_dir_abs %s" % pkg_dir_abs
        self.output("pkg_dir_abs %s" % pkg_dir_abs)

        self.output("Importing: %s" % msm_file)

        # Set single threaded appartement model
        sys.coinit_flags = 2
        MSM = LoadLibrary('MSM.Merge2.1', 'com')
        if "log_file_abs" in self.env:
            log_file_abs = self.env.get('log_file_abs')
            MSM.lib.OpenLog(log_file_abs)
        MSM.lib.OpenDatabase(msi_file)
        MSM.lib.OpenModule(msm_file,0)
        MSM.lib.Merge(msm_feature,msm_dir)
        MSM.lib.CloseModule()
        MSM.lib.CloseDatabase("Commit=True")
        MSM.lib.CloseLog()
        #print >> sys.stdout, "end of merge %s" % msi_file
        self.output("end of merge %s" % msi_file)

        #assembly_path = r"C:\Program Files (x86)\WiX Toolset v3.14\SDK"
        #sys.path.append(assembly_path)
        sys.path.append(self.env['DTF_PATH'])
        import clr
        clr.AddReference("Microsoft.Deployment.WindowsInstaller")
        from Microsoft.Deployment.WindowsInstaller import Database
        from Microsoft.Deployment.WindowsInstaller import Record
        from Microsoft.Deployment.WindowsInstaller import DatabaseOpenMode
        tmode = DatabaseOpenMode.ReadOnly
        WIdb = Database(msm_file, tmode)
        WIview = WIdb.OpenView("SELECT `Name`,`Data` FROM _Streams WHERE `Name`= 'MergeModule.CABinet'",None)
        WIview.Execute()
        cabRec = WIview.Fetch()
        cabRec.GetStream(2, os.path.join(temp_path, "MergeModule.cab"))
        cabRec.Dispose()
        WIview.Dispose()
        WIdb.Dispose()
        #print >> sys.stdout, "end of read cab"
        self.output("end of read cab")
        # Insert a new line into the media table to reflect the new CAB-file.
        tmode = DatabaseOpenMode.Direct
        WIdb = Database(msi_file, tmode)
        mediaIDs = WIdb.ExecuteIntegerQuery("SELECT `DiskId` FROM `Media` ORDER BY `DiskId`",None)
        #print >> sys.stdout, "mediaIDs %s" % mediaIDs
        fileSeqs = WIdb.ExecuteIntegerQuery("SELECT `Sequence` FROM `File` ORDER BY `Sequence`",None)
        #print >> sys.stdout, "fileSeqs %s" % fileSeqs
        mediaCabinet = "Data" + str(max(mediaIDs)+1) + ".cab"
        query = "INSERT INTO `Media` (`DiskId`, `LastSequence`, `DiskPrompt`, `Cabinet`) VALUES (" + str(max(mediaIDs)+1) + "," + str(max(fileSeqs)) + ",'','#" + mediaCabinet + "')"
        #print >> sys.stdout, "media row %s" % query
        WIdb.Execute(query,None)
        #print >> sys.stdout, "end of set media row"	
        #Insert the CAB-file from the merge module into the MSI-file.
        cabRec = Record(1)
        #print >> sys.stdout, "after cabRec"	
        cabRec.SetStream(1, os.path.join(temp_path, "MergeModule.cab"))
        #print >> sys.stdout, "after cabRec.Setstream"
        #self.output("after cabRec.Setstream")
        
        query = "INSERT INTO `_Streams` (`Name`, `Data`) VALUES ('" + mediaCabinet + "', ?)"
        #print >> sys.stdout, "after query2"	
        WIdb.Execute(query, cabRec)
        cabRec.Dispose()
        WIdb.Dispose()		
		
if __name__ == '__main__':
    processor = MSIimportMergeModule()
    processor.execute_shell()
