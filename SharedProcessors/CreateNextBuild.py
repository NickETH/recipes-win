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

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["CreateNextBuild"]


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
        print >> sys.stdout, "org_ver %s" % org_ver

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
        
        self.env['build_ver'] = archiveVersion.encode('ascii', 'ignore')
        self.env['build_new'] = archiveVersion.encode('ascii', 'ignore')		
        self.output("New build_ver: %s" % (self.env['build_ver']))

if __name__ == '__main__':
    processor = CreateNextBuild()
    processor.execute_shell()
