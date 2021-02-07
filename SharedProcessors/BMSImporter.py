#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-04-26.
#
# Import a new application into BMS (baramundi management system).
# Depends on the powershell script BMSImporter.ps1.
# Calls the BMS REST API to create a new application.
# Copies the files to the destination network shares.
# Extended with port/CM-entry, ApplicationFile and Dependencies, 20200523, Hm
# Patch subprocess to take unicode, https://bugs.python.org/issue1759845, https://pypi.org/project/subprocessww/, 20200626, Hm
# Extended with UseBBT-option and explicit options for uninstall, 20210207, Hm
# Todo: Generic read function for optional parameter processing with for statement and value types

import os
import sys
import subprocessww
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["BMSImporter"]


class BMSImporter(Processor):
    description = "Import a new application into BMS."
    input_variables = {
        "bms_serverurl": {
            "required": True,
            "description": "URL of the BMS server, required",
        },
        "bms_serverport": {
            "required": False,
            "description": "Port of the BMS bConnect service, Defaults to: 443",
        },
        "bms_CM_entry": {
            "required": True,
            "description": "Name of the object in the credential manager, required",
        },
        "bms_username": {
            "required": True,
            "description": "Username to log into the BMS bconnect API, required",
        },
        "bms_app_name": {
            "required": True,
            "description": "Application name in BMS, required",
        },
        "bms_app_vendor": {
            "required": True,
            "description": "Application vendor name in BMS, required",
        },
        "bms_app_parentid": {
            "required": True,
            "description": "GUID of the Parent OU in BMS, required",
        },
        "bms_app_version": {
            "required": True,
            "description": "Application version in BMS, required",
        },
        "bms_app_valid4os": {
            "required": True,
            "description": "Valid OS for the application in BMS, required",
        },
        "bms_app_seccont": {
            "required": True,
            "description": "Application's security context in BMS, required",
        },
        "bms_app_installcmd": {
            "required": True,
            "description": "Application install command line in BMS, required",
        },
        "bms_app_installparm": {
            "required": False,
            "description": "Application install parameters in BMS.",
        },
        "bms_app_iopt_rebootbhv": {
            "required": False,
            "description": "Application install option <reboot behaviour> in BMS.",
        },
        "bms_app_iopt_usebbt": {
            "required": False,
            "description": "Application install option <support bbt> in BMS.",
		},
        "bms_app_iopt_copylocal": {
            "required": False,
            "description": "Application install option <copy locally> in BMS.",
        },
        "bms_app_iopt_reinstall": {
            "required": False,
            "description": "Application install option <Reinstallation allowed> in BMS.",
        },
        "bms_app_iopt_target": {
            "required": False,
            "description": "Application install option <target> in BMS.",
        },
        "bms_app_comment": {
            "required": False,
            "description": "Application comment in BMS.",
        },
        "bms_app_conschecks": {
            "required": False,
            "description": "Application consistency check in BMS.",
        },
        "bms_app_uninstcmd": {
            "required": False,
            "description": "Application uninstall command line in BMS.",
        },
        "bms_app_uninstparm": {
            "required": False,
            "description": "Application uninstall parameters in BMS.",
        },
        "bms_app_uopt_rebootbhv": {
            "required": False,
            "description": "Application uninstall option <reboot behaviour> in BMS.",
        },
        "bms_app_uopt_usebbt": {
            "required": False,
            "description": "Application uninstall option <support bbt> in BMS.",
		},
        "bms_app_localfilecopy": {
            "required": False,
            "description": "File to copy locally.",
        },
        "bms_app_dependencies": {
            "required": False,
            "description": "(Array of) 'Name~~~Version' of a dependency.",
        },
        "inst_file_src_dest": {
            "required": False,
            "description": "Application install file(s) to copy to the DIP-Share, use wildcards for multiple objects.",
        },
        "read_file_src_dest": {
            "required": False,
            "description": "Application readme and/or create-log file(s) to copy to the DIP-Share, use wildcards for multiple objects.",
        },
        "bms_imp_logfile": {
            "required": False,
            "description": "Path to a logfile for exensive logging of the importer.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the run.",
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):

        bms_serverurl = self.env.get('bms_serverurl')
        bms_serverport = self.env.get('bms_serverport', "443")
        bms_CM_entry = self.env.get('bms_CM_entry')
        bms_username = self.env.get('bms_username')
        bms_app_name = self.env.get('bms_app_name')
        bms_app_vendor = self.env.get('bms_app_vendor')
        bms_app_parentid = self.env.get('bms_app_parentid')
        bms_app_version = self.env.get('bms_app_version')
        bms_app_valid4os = self.env.get('bms_app_valid4os')
        bms_app_seccont = self.env.get('bms_app_seccont')
        bms_app_installcmd = self.env.get('bms_app_installcmd')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 5)
        print >> sys.stdout, "bms_app_name %s" % bms_app_name

        self.output("Creating: %s" % bms_app_name)
        sharedproc_dir = os.path.dirname(os.path.realpath(__file__))
        ps_script = os.path.join(sharedproc_dir, 'BMSImporter.ps1')
        powershell = "C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        # Call the powershell script with its arguments.
        cmd = [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
            ps_script,
            bms_serverurl,
            bms_serverport,
            bms_CM_entry,
            bms_username,
            bms_app_name,
            bms_app_vendor,
            bms_app_parentid,
            bms_app_version,
            bms_app_valid4os,
            bms_app_seccont,
            bms_app_installcmd,]

        if "bms_app_installparm" in self.env:
            bms_app_installparm = self.env.get('bms_app_installparm')
            cmd.extend(['-bms_app_installparm', bms_app_installparm])

        if "bms_app_iopt_rebootbhv" in self.env:
            bms_app_iopt_rebootbhv = self.env.get('bms_app_iopt_rebootbhv')
            cmd.extend(['-bms_app_iopt_rebootbhv', bms_app_iopt_rebootbhv])

        if "bms_app_iopt_usebbt" in self.env:
            bms_app_iopt_usebbt = self.env.get('bms_app_iopt_usebbt')
            cmd.extend(['-bms_app_iopt_usebbt', bms_app_iopt_usebbt])

        if "bms_app_iopt_copylocal" in self.env:
            bms_app_iopt_copylocal = self.env.get('bms_app_iopt_copylocal')
            cmd.extend(['-bms_app_iopt_copylocal', bms_app_iopt_copylocal])

        if "bms_app_iopt_reinstall" in self.env:
            bms_app_iopt_reinstall = self.env.get('bms_app_iopt_reinstall')
            cmd.extend(['-bms_app_iopt_reinstall', bms_app_iopt_reinstall])

        if "bms_app_iopt_target" in self.env:
            bms_app_iopt_target = self.env.get('bms_app_iopt_target')
            cmd.extend(['-bms_app_iopt_target', bms_app_iopt_target])

        if "bms_app_comment" in self.env:
            bms_app_comment = self.env.get('bms_app_comment')
            cmd.extend(['-bms_app_comment', bms_app_comment])

        if "bms_app_category" in self.env:
            bms_app_category = self.env.get('bms_app_category')
            cmd.extend(['-bms_app_category', bms_app_category])

        if "bms_app_conschecks" in self.env:
            bms_app_conschecks = self.env.get('bms_app_conschecks')
            cmd.extend(['-bms_app_conschecks', bms_app_conschecks])

        if "bms_app_uninstcmd" in self.env:
            bms_app_uninstcmd = self.env.get('bms_app_uninstcmd')
            cmd.extend(['-bms_app_uninstcmd', bms_app_uninstcmd])

        if "bms_app_uninstparm" in self.env:
            bms_app_uninstparm = self.env.get('bms_app_uninstparm')
            cmd.extend(['-bms_app_uninstparm', bms_app_uninstparm])

        if "bms_app_uopt_rebootbhv" in self.env:
            bms_app_uopt_rebootbhv = self.env.get('bms_app_uopt_rebootbhv')
            cmd.extend(['-bms_app_uopt_rebootbhv', bms_app_uopt_rebootbhv])

        if "bms_app_uopt_usebbt" in self.env:
            bms_app_uopt_usebbt = self.env.get('bms_app_uopt_usebbt')
            cmd.extend(['-bms_app_uopt_usebbt', bms_app_uopt_usebbt])

        if "bms_app_localfilecopy" in self.env:
            bms_app_localfilecopy = self.env.get('bms_app_localfilecopy')
            cmd.extend(['-bms_app_localfilecopy', bms_app_localfilecopy])

        if "bms_app_dependencies" in self.env:
            bms_app_dependencies = self.env.get('bms_app_dependencies')
            # if recipe writer gave us a single string instead of a list of strings,
            # convert it to a list of strings
            if isinstance(self.env["bms_app_dependencies"], basestring):
                self.env["bms_app_dependencies"] = [self.env["bms_app_dependencies"]]

            cmd_string = ""
            for app_ver_entry in self.env["bms_app_dependencies"]:
                cmd_string += app_ver_entry + '|||'
			
            cmd.extend(['-bms_app_dependencies', cmd_string])

        if "inst_file_src_dest" in self.env:
            inst_file_src_dest = self.env.get('inst_file_src_dest')
            cmd.extend(['-inst_file_src_dest', inst_file_src_dest])

        if "read_file_src_dest" in self.env:
            read_file_src_dest = self.env.get('read_file_src_dest')
            cmd.extend(['-read_file_src_dest', read_file_src_dest])

        if "bms_imp_logfile" in self.env:
            bms_imp_logfile = self.env.get('bms_imp_logfile')
            cmd.extend(['-bms_imp_logfile', bms_imp_logfile])

        #print("cmdline %s" % cmd)
        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)

            else:
                Output = subprocess.check_output(cmd)

        except:
            if ignore_errors != 'True':
                raise
        print >> sys.stdout, "cmdline Output %s" % Output
        #self.env['pkg_dir'] = Output
		
        archiveVersion = ""
        for line in Output.split("\n"):
            if verbosity > 2:
                print line
            if "Buildversion:" in line:
                archiveVersion = line.split()[-1]
                continue

if __name__ == '__main__':
    processor = BMSImporter()
    processor.execute_shell()
