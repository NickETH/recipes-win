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
# 20210517 Nick Heim: Python v3 changes

import os
import sys
import subprocess
import string

from autopkglib import Processor, ProcessorError


__all__ = ["CreateNextBuild"]

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

class CreateNextBuild(Processor):
    description = "Create the environment for the next build."
    input_variables = {
        "build_dir": {
            "required": True,
            "description": "Path to the build dir, required",
        },
        "recipe_dir": {
            "required": True,
            "description": "Path to the recipe_dir, required",
        },
        "org_ver": {
            "required": True,
            "description": "Original version string, required",
        },
        "pkg_dir": {
            "required": True,
            "description": "Path to the pkg_dir, if the tag ::VVeerrssiioonn:: is part of, it will be replaced with the normalized version, required",
        },
        "folder_list": {
            "required": True,
            "description": "Path to the folder_list, required",
        },
        "ver_fields": {
            "required": False,
            "description": "Number of version fields divided by periods",
        },
        "create_AS_ver": {
            "default": False,
            "required": False,
            "description": "Bool, Create a version string for an Active Setup",
        },
        "recipe_path": {
            "required": False,
            "description": "Path to the recipe file",
        },
        "BuildFiles": {
            "required": False,
            "description": "Textfile, containing the paths to the additional buildfiles.",
        },
        "recipe_cache_dir": {
            "required": False,
            "description": "Path to the recipe cache dir",
        },
        "PrevVerFiles": {
            "required": False,
            "description": "Textfile, containing the paths to files needed from the previous build.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the run.",
        },
    }
    output_variables = {
        "build_ver": {
            "description": "Normalized version string."
        }
    }

    __doc__ = description

    def main(self):

        build_dir = self.env.get('build_dir')
        recipe_dir = self.env.get('recipe_dir')
        org_ver = self.env.get('org_ver')
        pkg_dir = self.env.get('pkg_dir')
        folder_list = self.env.get('folder_list')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 5)
        #print >> sys.stdout, "org_ver %s" % org_ver
        self.output("org_ver %s" % org_ver)

        self.output("Creating: %s" % pkg_dir)
        sharedproc_dir = os.path.dirname(os.path.realpath(__file__))
        ps_script = os.path.join(sharedproc_dir, 'CreateNextBuild.ps1')
        powershell = "C:\\windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        # Call the powershell script with its arguments.
        cmd = [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
            ps_script,
            build_dir,
            recipe_dir,
            org_ver,
            pkg_dir,
            folder_list,]

        if "ver_fields" in self.env:
            ver_fields = os.path.splitext(self.env.get('ver_fields'))[0]
            cmd.extend(['-ver_fields', ver_fields])

        if "create_AS_ver" in self.env:
            create_AS_ver = self.env.get('create_AS_ver')
            #print >> sys.stdout, "create_AS_ver %s" % create_AS_ver
            self.output("create_AS_ver %s" % create_AS_ver)
            if checkbool(create_AS_ver):
                cmd.extend(['-AS_ver', create_AS_ver])
                #print >> sys.stdout, "cmdline %s" % cmd
                self.output("cmdline %s" % cmd)

        if "recipe_path" in self.env:
            recipe_path = os.path.splitext(self.env.get('recipe_path'))[0]
            cmd.extend(['-recipe_path', recipe_path])

        if {"recipe_path", "BuildFiles"}.issubset(self.env):
            BuildFiles = self.env.get('BuildFiles')
            cmd.extend(['-BuildFiles', os.path.join(recipe_path, BuildFiles)])
            # print >> sys.stdout, "recipe_path %s" % recipe_path
	
        if {"recipe_path", "recipe_cache_dir", "PrevVerFiles"}.issubset(self.env):
            recipe_cache_dir = self.env.get('recipe_cache_dir')
            PrevVerFiles = self.env.get('PrevVerFiles')
            cmd.extend(['-recipe_cache_dir', recipe_cache_dir, '-PrevVerFiles', os.path.join(recipe_path, PrevVerFiles)])
            # cmd.extend(['-PrevVerFiles', PrevVerFiles])

        # print >> sys.stdout, "cmdline %s" % cmd
        try:
            if verbosity > 1:
                #Output = subprocess.check_output(cmd)
                Output = subprocess.getoutput(cmd)
            else:
                #Output = subprocess.check_output(cmd)
                Output = subprocess.getoutput(cmd)
        except:
            if ignore_errors != 'True':
                raise
        #print >> sys.stdout, "cmdline Output %s" % Output
        self.output("cmdline Output %s" % Output)
        #self.env['pkg_dir'] = Output
		
        archiveVersion = ""
        for line in Output.split("\n"):
            if verbosity > 2:
                print(line)
            if "Buildversion:" in line:
                if "ASversion:" in line:
                   lineobj = line.split("|",-1)
                   archiveVersion = lineobj[0].split()[-1]
                   ActiveSetupVersion = lineobj[1].split()[-1]
                   self.env['AS_ver'] = ActiveSetupVersion
                else:
                   archiveVersion = line.split()[-1]
                continue
        
        self.env['build_ver'] = archiveVersion
        self.env['build_new'] = archiveVersion
        self.env['build_ver_short'] = str.replace(archiveVersion,'.','')
        self.output("New build_ver: %s" % (self.env['build_ver']))

if __name__ == '__main__':
    processor = CreateNextBuild()
    processor.execute_shell()
