#!/usr/bin/python
#
# Copyright 2020 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-18.
# Started as MozillaOmniUpdate.
#
# Update the omnni.ja JAR-archive in Mozilla products.
# As a start only Firefox extensions as features is implemented
# Needs some work around error handling.
#
#
# The parts of this file, which are used to deoptimize and optimize the omni.ja file
# are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# 20210522 Nick Heim: Python v3 changes. Partly taken from: https://github.com/Stebalien/firefox-tweak
# 20210530 Nick Heim: Extended to MozillaAddonIntegrator for functions see the code.
    

import os
import shutil
import sys
import subprocess
import json
import re

from autopkglib import Processor, ProcessorError
import struct

__all__ = ["MozillaAddonIntegrator"]

local_file_header = [
    ("signature", "uint32"),
    ("min_version", "uint16"),
    ("general_flag", "uint16"),
    ("compression", "uint16"),
    ("lastmod_time", "uint16"),
    ("lastmod_date", "uint16"),
    ("crc32", "uint32"),
    ("compressed_size", "uint32"),
    ("uncompressed_size", "uint32"),
    ("filename_size", "uint16"),
    ("extra_field_size", "uint16"),
    ("filename", "filename_size"),
    ("extra_field", "extra_field_size"),
    ("data", "compressed_size")
]

cdir_entry = [
    ("signature", "uint32"),
    ("creator_version", "uint16"),
    ("min_version", "uint16"),
    ("general_flag", "uint16"),
    ("compression", "uint16"),
    ("lastmod_time", "uint16"),
    ("lastmod_date", "uint16"),
    ("crc32", "uint32"),
    ("compressed_size", "uint32"),
    ("uncompressed_size", "uint32"),
    ("filename_size", "uint16"),
    ("extrafield_size", "uint16"),
    ("filecomment_size", "uint16"),
    ("disknum", "uint16"),
    ("internal_attr", "uint16"),
    ("external_attr", "uint32"),
    ("offset", "uint32"),
    ("filename", "filename_size"),
    ("extrafield", "extrafield_size"),
    ("filecomment", "filecomment_size"),
]

cdir_end = [
    ("signature", "uint32"),
    ("disk_num", "uint16"),
    ("cdir_disk", "uint16"),
    ("disk_entries", "uint16"),
    ("cdir_entries", "uint16"),
    ("cdir_size", "uint32"),
    ("cdir_offset", "uint32"),
    ("comment_size", "uint16"),
]

type_mapping = { "uint32":"I", "uint16":"H"}

def format_struct (format):
    string_fields = {}
    fmt = "<"
    for (name,value) in iter(format):
        try:
            fmt += type_mapping[value][0]
        except KeyError:
            string_fields[name] = value
    return (fmt, string_fields)

def size_of(format):
    return struct.calcsize(format_struct(format)[0])

class MyStruct:
    def __init__(self, format, string_fields):
        self.__dict__["struct_members"] = {}
        self.__dict__["format"] = format
        self.__dict__["string_fields"] = string_fields

    def addMember(self, name, value):
        self.__dict__["struct_members"][name] = value

    def __getattr__(self, item):
        try:
            return self.__dict__["struct_members"][item]
        except:
            pass
        print("no %s" % item)
        print(self.__dict__["struct_members"])
        raise AttributeError

    def __setattr__(self, item, value):
        if item in self.__dict__["struct_members"]:
            self.__dict__["struct_members"][item] = value
        else:
            raise AttributeError

    def pack(self):
        extra_data = b""
        values = []
        string_fields = self.__dict__["string_fields"]
        struct_members = self.__dict__["struct_members"]
        format = self.__dict__["format"]
        for (name,_) in format:
            if name in string_fields:
                value = struct_members[name]
                if isinstance(value, str):
                    value = value.encode("utf-8")
                extra_data = extra_data + value
            else:
                values.append(struct_members[name]);
        return struct.pack(format_struct(format)[0], *values) + extra_data
   
ENDSIG = 0x06054b50

def assert_true(cond, msg):
    if not cond:
        raise Exception(msg)
        exit(1)

class BinaryBlob:
    def __init__(self, f):
       self.data = open(f, "rb").read()
       self.offset = 0
       self.length = len(self.data)

    def readAt(self, pos, length):
        self.offset = pos + length
        return self.data[pos:self.offset]

    def read_struct (self, format, offset = None):
        if offset == None:
            offset = self.offset
        (fstr, string_fields) = format_struct(format)
        size = struct.calcsize(fstr)
        data = self.readAt(offset, size)
        ret = struct.unpack(fstr, data)
        retstruct = MyStruct(format, string_fields)
        i = 0
        for (name,_) in iter(format):
            member_desc = None
            if not name in string_fields:
                member_data = ret[i]
                i = i + 1
            else:
                # zip has data fields which are described by other struct fields, this does 
                # additional reads to fill em in
                member_desc = string_fields[name]
                member_data = self.readAt(self.offset, retstruct.__getattr__(member_desc))
            retstruct.addMember(name, member_data)
        # sanity check serialization code
        data = self.readAt(offset, self.offset - offset)
        out_data = retstruct.pack()
        assert_true(out_data == data, "Serialization fail %d !=%d"% (len(out_data), len(data)))
        return retstruct

def optimizejar(jar, outjar, inlog = None):
    if inlog is not None:
        inlog = open(inlog).read().rstrip()
        # in the case of an empty log still move the index forward
        if len(inlog) == 0:
            inlog = []
        else:
            inlog = inlog.split("\n")
    outlog = []
    jarblob = BinaryBlob(jar)
    dirend = jarblob.read_struct(cdir_end, jarblob.length - size_of(cdir_end))
    assert_true(dirend.signature == ENDSIG, "no signature in the end");
    cdir_offset = dirend.cdir_offset
    readahead = 0
    if inlog is None and cdir_offset == 4:
        readahead = struct.unpack("<I", jarblob.readAt(0, 4))[0]
        print("%s: startup data ends at byte %d" % (outjar, readahead));

    total_stripped = 0;
    jarblob.offset = cdir_offset
    central_directory = []
    for i in range(0, dirend.cdir_entries):
        entry = jarblob.read_struct(cdir_entry)
        if entry.filename[-1:] == "/":
            total_stripped += len(entry.pack())
        else:
            total_stripped += entry.extrafield_size
        central_directory.append(entry)
        
    reordered_count = 0
    if inlog is not None:
        dup_guard = set()
        for ordered_name in inlog:
            if ordered_name in dup_guard:
                continue
            else:
                dup_guard.add(ordered_name)
            found = False
            for i in range(reordered_count, len(central_directory)):
                if central_directory[i].filename.decode() == ordered_name:
                    # swap the cdir entries
                    tmp = central_directory[i]
                    central_directory[i] = central_directory[reordered_count]
                    central_directory[reordered_count] = tmp
                    reordered_count = reordered_count + 1
                    found = True
                    break
            if not found:
                print( "Can't find '%s' in %s" % (ordered_name, jar))

    outfd = open(outjar, "wb")
    out_offset = 0
    if inlog is not None:
        # have to put central directory at offset 4 cos 0 confuses some tools.
        # This also lets us specify how many entries should be preread
        dirend.cdir_offset = 4
        # make room for central dir + end of dir + 4 extra bytes at front
        out_offset = dirend.cdir_offset + dirend.cdir_size + size_of(cdir_end) - total_stripped
        outfd.seek(out_offset)

    cdir_data = b""
    written_count = 0
    crc_mapping = {}
    dups_found = 0
    dupe_bytes = 0
    # store number of bytes suggested for readahead
    for entry in central_directory:
        # read in the header twice..first for comparison, second time for convenience when writing out
        jarfile = jarblob.read_struct(local_file_header, entry.offset)
        assert_true(jarfile.filename == entry.filename, "Directory/Localheader mismatch")

        # drop directory entries
        if entry.filename[-1:] == "/":
            total_stripped += len(jarfile.pack())
            dirend.cdir_entries -= 1
            continue
        # drop extra field data
        else:
            total_stripped += jarfile.extra_field_size;
        entry.extrafield = jarfile.extra_field = ""
        entry.extrafield_size = jarfile.extra_field_size = 0
        # January 1st, 2010
        entry.lastmod_date = jarfile.lastmod_date = ((2010 - 1980) << 9) | (1 << 5) | 1
        entry.lastmod_time = jarfile.lastmod_time = 0
        data = jarfile.pack()
        outfd.write(data)
        old_entry_offset = entry.offset
        entry.offset = out_offset
        out_offset = out_offset + len(data)
        entry_data = entry.pack()
        cdir_data += entry_data
        expected_len = entry.filename_size + entry.extrafield_size + entry.filecomment_size
        assert_true(len(entry_data) != expected_len,
                    "%s entry size - expected:%d got:%d" % (entry.filename, len(entry_data), expected_len))
        written_count += 1

        if entry.crc32 in crc_mapping:
            dups_found += 1
            dupe_bytes += entry.compressed_size + len(data) + len(entry_data)
            print("%s\n\tis a duplicate of\n%s\n---"%(entry.filename, crc_mapping[entry.crc32]))
        else:
            crc_mapping[entry.crc32] = entry.filename;
        if inlog is not None:
            if written_count == reordered_count:
                readahead = out_offset
                print("%s: startup data ends at byte %d"%( outjar, readahead));
            elif written_count < reordered_count:
                pass
                #print("%s @ %d" % (entry.filename, out_offset))
        elif readahead >= old_entry_offset + len(data):
            outlog.append(entry.filename)
            reordered_count += 1

    if inlog is None:
        dirend.cdir_offset = out_offset

    if dups_found > 0:
        print("WARNING: Found %d duplicate files taking %d bytes"%(dups_found, dupe_bytes))

    dirend.cdir_size = len(cdir_data)
    dirend.disk_entries = dirend.cdir_entries
    dirend_data = dirend.pack()
    assert_true(size_of(cdir_end) == len(dirend_data), "Failed to serialize directory end correctly. Serialized size;%d, expected:%d"%(len(dirend_data), size_of(cdir_end)));

    outfd.seek(dirend.cdir_offset)
    assert_true(len(cdir_data) == dirend.cdir_size, "Failed to serialize central directory correctly. Serialized size;%d, expected:%d expected-size:%d" % (len(cdir_data), dirend.cdir_size, dirend.cdir_size - len(cdir_data)));
    outfd.write(cdir_data)
    outfd.write(dirend_data)

    # for ordered jars the central directory is written in the begining of the file, so a second central-directory
    # entry has to be written in the end of the file
    if inlog is not None:
        outfd.seek(0)
        outfd.write(struct.pack("<I", readahead));
        outfd.seek(out_offset)
        outfd.write(dirend_data)

    print("Stripped %d bytes" % total_stripped)
                                                                               
    print("%s %d/%d in %s" % (("Ordered" if inlog is not None else "Deoptimized"),
                              reordered_count, len(central_directory), outjar))
    outfd.close()
    return outlog

        
class MozillaAddonIntegrator(Processor):
    description = "Install Extension(s) per computer and alter settings in the omni.ja in Mozilla products."
    input_variables = {
        "application_name": {
            "required": True,
            "description": "Name of the the mozilla app (e.g. Firefox/Thunderbird, required",
        },
        "install_exe": {
            "required": True,
            "description": "Path to the exe of the mozilla app, required",
        },
        "new_extensions": {
            "required": True,
            "description": "(Array of) extension(s) to add, with name, full url to download and Wix-component-group separated by '|||', required",
        },
        "MakeFeatures": {
            "default": False,
            "required": False,
            "description": "Install the extension(s) as features. Default: false",
        },
        "omni_path": {
            "default": "browser\\omni.ja",
            "required": True,
            "description": "Internal Path to omni.ja in the exe file, relative",
        },
        "config_file_path": {
            "default": "chrome\\browser\\content\\browser\\built_in_addons.json",
            #"default": "chrome\\browser\\content\\built_in_addons.json",
            "required": False,
            "description": "Internal Path to built_in_addons.json in the omni.ja file, absolute",
        },
        "temp_path": {
            "required": False,
            "description": "Path to the folder where temporary files are stored, absolute",
        },
        "omni_output_path": {
            "required": False,
            "description": "Path to the folder where the altered omni file is stored, absolute",
        },
        "ext_install_path": {
            "required": True,
            "description": "Path to the folder where the extensions are stored, absolute",
        },
        "app_build_path": {
            "required": True,
            "description": "Path to the folder where the application build takes place, absolute",
        },
        "ext_install_xslt": {
            "required": False,
            "description": "Path to an XSLT file to transform Wix heat output, absolute",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the process.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    def optimize(self, JAR_LOG_DIR, IN_JAR_DIR, OUT_JAR_DIR):
        if not os.path.exists(JAR_LOG_DIR):
            print("No jar logs found in %s. No jars to optimize." % JAR_LOG_DIR)
            exit(0)

        ls = os.listdir(JAR_LOG_DIR)
        for logfile in ls:
            if not logfile.endswith(".jar.log"):
                continue
            injarfile = os.path.join(IN_JAR_DIR, logfile[:-4])
            outjarfile = os.path.join(OUT_JAR_DIR, logfile[:-4]) 
            if not os.path.exists(injarfile):
                #print "Warning: Skipping %s, %s doesn't exist" % (logfile, injarfile)
                self.output("Warning: Skipping %s, %s doesn't exist" % (logfile, injarfile))
                continue
            logfile = os.path.join(JAR_LOG_DIR, logfile)
            optimizejar(injarfile, outjarfile, logfile)

    def deoptimize(self, JAR_LOG_DIR, IN_JAR_DIR, OUT_JAR_DIR):
        if not os.path.exists(JAR_LOG_DIR):
            os.makedirs(JAR_LOG_DIR)

        ls = os.listdir(IN_JAR_DIR)
        for jarfile in ls:
            if not jarfile.endswith(".jar"):
                continue
            injarfile = os.path.join(IN_JAR_DIR, jarfile)
            outjarfile = os.path.join(OUT_JAR_DIR, jarfile) 
            logfile = os.path.join(JAR_LOG_DIR, jarfile + ".log")
            log = optimizejar(injarfile, outjarfile, None)
            open(logfile, "wb").write(b"\n".join(log))
            open(logfile, "wb").write(b"\n".join(log))

    def checkbool(self, v):
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
  
    def zip_file_extract(self, sevenzip_basic, verbosity, zip_file, file_to_extract, extract_dir, mode='e'):
        sz_cmd = [sevenzip_basic, mode, '-y', '-o%s' % extract_dir , zip_file, file_to_extract]
        self.output("zip file extract - sz_cmd: %s" % sz_cmd)
        try:
            if verbosity > 1:
                subprocess.check_call(sz_cmd)
            else:
                subprocess.check_call(sz_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise

    def zip_file_compress(self, sevenzip_basic, verbosity, zip_file, file_to_update, extract_dir, mode='u'):
        sz_cmd = [sevenzip_basic, mode, '-y', '-w%s' % extract_dir, zip_file, file_to_update, '-mm=Copy', '-mx0', '-mtc=off']
        self.output("zip file compress - sz_cmd: %s" % sz_cmd)
        currentDirectory = os.getcwd()
        os.chdir(extract_dir)
        try:
            if verbosity > 1:
                subprocess.check_call(sz_cmd)
            else:
                subprocess.check_call(sz_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise
        os.chdir(currentDirectory)
                
    def extension_install(self, curl_path, ei_sz_cmd, verbosity, new_ext_list, build_dir, extract_dir, install_path, install_type, xslt_file="none"):
        curl_cmd_basic = [
            curl_path,
            "--silent",
            "--show-error",
            "--no-buffer",
            "--dump-header",
            "-",
            #"--speed-time",
            #"30",
            "--location",
            "--url",
        ]
        heat_cmd_basic = [
            os.path.join((os.environ['WIX']), 'bin\\heat.exe'),
            "file",
        ]
        self.output("new_ext_list: %s" % new_ext_list)
        for Full_string in new_ext_list:
            self.output("Full_string: %s" % Full_string)
            Full_string_list = Full_string.split('|||')
            self.output("Full_string_list: %s" % Full_string_list)
            extension_work_name = Full_string_list[0]
            extension_full_url = Full_string_list[1]
            extension_comp_group = Full_string_list[2]
            extension_work_file = os.path.join(extract_dir, extension_work_name)
            curl_cmd = curl_cmd_basic[:]
            self.output("curl_cmd_basic: %s" % curl_cmd_basic)
            self.output("curl_cmd: %s" % curl_cmd)
            curl_cmd.extend([extension_full_url])
            curl_cmd.extend(["--output", extension_work_file])
            self.output("curl_cmd: %s" % curl_cmd)
            text=True
            errors = "ignore" if text else None
            try:
                result = subprocess.run(
                    curl_cmd,
                    shell=False,
                    bufsize=1,
                    capture_output=True,
                    check=True,
                    #text=text,
                    errors=errors,
                )
            except subprocess.CalledProcessError as e:
                raise ProcessorError(e)
            #return result.stdout, result.stderr, result.returncode
            
            self.zip_file_extract(ei_sz_cmd, verbosity, extension_work_file, "manifest.json", extract_dir)
            json_file_name = os.path.join(extract_dir, "manifest.json")
            with open(json_file_name, "r") as read_file:
                json_data = json.load(read_file)
            if 'applications' in json_data.keys():
                extension_install_name = json_data['applications']['gecko']['id'] + ".xpi"
            elif 'browser_specific_settings' in json_data.keys():
                extension_install_name = json_data['browser_specific_settings']['gecko']['id'] + ".xpi"
            else:
                print("Extension name not found in manifest")
            self.output("extension_install_name: %s" % extension_install_name)
            os.remove(json_file_name)
            if not os.path.isdir(install_path):
                os.makedirs(install_path)
            extension_install_path = os.path.join(install_path, extension_install_name)
            shutil.copy(extension_work_file, extension_install_path)
            shutil.copy(os.path.join(build_dir, "Prev_Ver_MozExt_" + extension_work_name + ".wxs"), os.path.join(build_dir, "Snapshot.xml"))
		# <copy
			# file="Prev_Ver_FF${SourceFILE}.wxs"
			# tofile="Snapshot.xml"
			# overwrite="true"
		# />
            heat_cmd = heat_cmd_basic[:]
            heat_cmd.extend([extension_install_path])
            heat_cmd.extend([
                "-gg",
                "-sfrag",
                "-srd",
                "-suid",
            ])
            heat_cmd.extend(["-dr", "EXTENSIONS"])
            heat_cmd.extend(["-cg", extension_comp_group])
            heat_cmd.extend(["-var", "wix.MozExtDir"])
            heat_cmd.extend(["-out", os.path.join(build_dir, "MozExt_" + extension_work_name + ".wxs")])
            if xslt_file != "none":
                heat_cmd.extend(["-t", os.path.join(build_dir, xslt_file)])
            self.output("heat_cmd: %s" % heat_cmd)
            os.chdir(build_dir)
            try:
                result = subprocess.run(
                    heat_cmd,
                    shell=False,
                    bufsize=1,
                    capture_output=True,
                    check=True,
                    text=text,
                    errors=errors,
                )
            except subprocess.CalledProcessError as e:
                raise ProcessorError(e)
            #return result.stdout, result.stderr, result.returncode

        

    def core_extract(self, ce_sz_cmd, verbosity, app_name, core_exe, extract_dir, build_path):
        self.output("Extracting: %s" % core_exe)
        ce_cmd = [ce_sz_cmd, 'x', '-y', '-o%s' % extract_dir , core_exe]
        print("ce_cmd: %s" % ce_cmd)
        try:
            if verbosity > 1:
                subprocess.check_call(ce_cmd)
            else:
                subprocess.check_call(ce_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise
        shutil.move(os.path.join(extract_dir, 'core'), os.path.join(build_path, app_name))

    def enable_side_load(self, esl_sz_cmd, verbosity, app_name, extract_dir, build_path, omni_sub_path, config_file):
        omni_full_path = os.path.join(build_path, app_name, omni_sub_path)
        omni_edit_path = os.path.join(extract_dir, 'omni.jar')
        shutil.move(omni_full_path, omni_edit_path)
        self.deoptimize(extract_dir, extract_dir, extract_dir)
        self.zip_file_extract(esl_sz_cmd, verbosity, omni_edit_path, config_file, extract_dir, mode='x')
        js_file = os.path.join(extract_dir, config_file)
        with open(js_file,"r") as open_js_file:
            js_file_content = open_js_file.read()
        re_pattern = re.compile('MOZ_ALLOW_ADDON_SIDELOAD:\s*.*\s*false')
        match = re_pattern.search(js_file_content)
        new_pattern = match.group().replace('false', 'true')
        js_file_content_new = js_file_content.replace(match.group(), new_pattern)
        with open(js_file,"w") as new_js_file:
            new_js_file.write(js_file_content_new)
        self.zip_file_compress(esl_sz_cmd, verbosity, omni_edit_path, config_file, extract_dir, mode='u')
        self.optimize(extract_dir, extract_dir, extract_dir)
        shutil.move(omni_edit_path, omni_full_path)
        
    def read_json_file(self, json_file):
        with open(json_file, "r") as read_file:
            json_data = json.load(read_file)
        return json_data

    def write_json_file(self, json_file, json_data):
        with open(json_file, 'w') as write_file:
            json.dump(json_data, write_file)

    def main(self):
        application_name = self.env.get('application_name')
        install_exe = self.env.get('install_exe', self.env.get('pathname'))
        #print >> sys.stdout, "after join"
        #print("install_exe %s" % install_exe, file=sys.stdout)
        print("install_exe %s" % install_exe)
        # if recipe writer gave us a single string instead of a list of strings,
        # convert it to a list of strings
        if isinstance(self.env["new_extensions"], str):
            self.env["new_extensions"] = [self.env["new_extensions"]]
        new_extensions_list = self.env.get('new_extensions')
        # Set default for working_directory
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        curl_path = self.env.get('CURL_PATH')
        extract_directory = self.env.get('temp_path', 'working_directory')
        omni_path = self.env.get('omni_path')
        config_file_path = self.env.get('config_file_path')
        omni_output_path = self.env.get('omni_output_path')
        ext_install_path = self.env.get('ext_install_path')
        app_build_path = self.env.get('app_build_path')
        ignore_errors = self.env.get('ignore_errors', True)
        sevenzipcmd = self.env.get('7ZIP_PATH')
        verbosity = self.env.get('verbose', 1)
        if "ext_install_xslt" in self.env:
            ext_install_xslt = str(self.env.get('ext_install_xslt'))
        if "MakeFeatures" in self.env:
            MakeFeatures = str(self.env.get('MakeFeatures'))
        if not self.checkbool(MakeFeatures):
            extension_type_dir = ""
        else:
            extension_type_dir = ""

        if not os.path.exists(extract_directory):
            os.makedirs(extract_directory)

        self.core_extract(sevenzipcmd, verbosity, application_name, install_exe, extract_directory, app_build_path)
        self.extension_install(curl_path, sevenzipcmd, verbosity, new_extensions_list, app_build_path, extract_directory, ext_install_path, MakeFeatures, ext_install_xslt)
        self.enable_side_load(sevenzipcmd, verbosity, application_name, extract_directory, app_build_path, omni_path, config_file_path)

        self.output("Extracting: %s" % install_exe)
        #cmd = [sevenzipcmd, 'e', '-y', '-o%s' % extract_directory , install_exe, omni_path]
        #cmd = [sevenzipcmd, 'e', '-y', '-o%s' % extract_directory , install_exe, 'omni.ja']
        # print("cmd: %s" % cmd)
        # try:
            # if verbosity > 1:
                # subprocess.check_call(cmd)
            # else:
                # subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # except:
            # if ignore_errors != 'True':
                # raise

        # self.output("Extracted Archive Path: %s" % extract_directory)
        # shutil.move(os.path.join(extract_directory, 'omni.ja'), os.path.join(extract_directory, 'omni.jar'))
        # deoptimize(extract_directory, extract_directory, extract_directory)
        # cmd = [sevenzipcmd, 'x', '-y', '-o%s' % extract_directory, os.path.join(extract_directory, 'omni.jar'), built_in_addons_path]

        # try:
            # if verbosity > 1:
                # subprocess.check_call(cmd)
            # else:
                # subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # except:
            # if ignore_errors != 'True':
                # raise
        # json_file_name = os.path.join(extract_directory, built_in_addons_path)
        # with open(json_file_name, "r") as read_file:
            # json_data = json.load(read_file)
        # json_data_sys = json_data["system"]
        # if recipe writer gave us a single name instead of a list of names,
        # convert it to a list of names
        # if isinstance(self.env["new_features"], str):
            # self.env["new_features"] = [self.env["new_features"]]

        # for feature_name in self.env["new_features"]:
            # # print >> sys.stdout, "SQL_string %s" % new_features
            # try:
                # #json_data_sys.append(unicode(feature_name))
                # json_data_sys.append(str(feature_name))
            # except OSError as err:
                # raise ProcessorError(
                    # "Could not append %s: %s" % (feature_name, err))

        # with open(json_file_name, 'w') as write_file:
            # json.dump(json_data, write_file)
        # os.chdir(extract_directory)
        # cmd = [sevenzipcmd, 'u', '-y', '-w%s' % extract_directory, os.path.join(extract_directory, 'omni.jar'), built_in_addons_path, '-mm=Copy', '-mx0', '-mtc=off']
        # print("cmd: %s" % cmd)
        # try:
            # if verbosity > 1:
                # subprocess.check_call(cmd)
            # else:
                # subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # except:
            # if ignore_errors != 'True':
                # raise
        # optimize(extract_directory, extract_directory, extract_directory)
        # #optimize(JAR_LOG_DIR, IN_JAR_DIR, OUT_JAR_DIR)
        # dest_file_name = os.path.join(output_path, 'omni.ja')

        # shutil.move(os.path.join(extract_directory, 'omni.jar'), dest_file_name)
		
if __name__ == '__main__':
    processor = MozillaAddonIntegrator()
    processor.execute_shell()
