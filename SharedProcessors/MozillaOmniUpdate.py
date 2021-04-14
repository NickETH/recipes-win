#!/usr/bin/python
#
# Copyright 2020 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-18.
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

#from __future__ import absolute_import
#from __future__ import print_function
import os
import shutil
import sys
import subprocess
import json

from autopkglib import Processor, ProcessorError
import six
import struct

__all__ = ["MozillaOmniUpdate"]

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
        print("no %s" %item)
        print(self.__dict__["struct_members"])
        raise AttributeError

    def __setattr__(self, item, value):
        if item in self.__dict__["struct_members"]:
            self.__dict__["struct_members"][item] = value
        else:
            raise AttributeError

    def pack(self):
        extra_data = ""
        values = []
        string_fields = self.__dict__["string_fields"]
        struct_members = self.__dict__["struct_members"]
        format = self.__dict__["format"]
        for (name,_) in format:
            if name in string_fields:
                extra_data = extra_data + struct_members[name]
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

    jarblob.offset = cdir_offset
    central_directory = []
    for i  in range(0, dirend.cdir_entries):
        entry = jarblob.read_struct(cdir_entry)
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
                if central_directory[i].filename == ordered_name:
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
        out_offset = dirend.cdir_offset + dirend.cdir_size + size_of(cdir_end) 
        outfd.seek(out_offset)

    cdir_data = ""
    written_count = 0
    # store number of bytes suggested for readahead
    for entry in central_directory:
        # read in the header twice..first for comparison, second time for convenience when writing out
        jarfile = jarblob.read_struct(local_file_header, entry.offset)
        assert_true(jarfile.filename == entry.filename, "Directory/Localheader mismatch")
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

    print "%s %d/%d in %s" % (("Ordered" if inlog is not None else "Deoptimized"),
                              reordered_count, len(central_directory), outjar)
    outfd.close()
    return outlog
        
# if len(sys.argv) != 5:
    # print "Usage: --optimize|--deoptimize %s JAR_LOG_DIR IN_JAR_DIR OUT_JAR_DIR" % sys.argv[0]
    # exit(1)

def optimize(JAR_LOG_DIR, IN_JAR_DIR, OUT_JAR_DIR):
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
            print "Warning: Skipping %s, %s doesn't exist" % (logfile, injarfile)
            continue
        logfile = os.path.join(JAR_LOG_DIR, logfile)
        optimizejar(injarfile, outjarfile, logfile)

def deoptimize(JAR_LOG_DIR, IN_JAR_DIR, OUT_JAR_DIR):
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
        open(logfile, "wb").write("\n".join(log))

class MozillaOmniUpdate(Processor):
    description = "Update the omni.ja in Mozilla products."
    input_variables = {
        "install_exe": {
            "required": True,
            "description": "Path to the exe, required",
        },
        "new_features": {
            "required": True,
            "description": "(Array of) extension name(s) to add, required",
        },
        "omni_path": {
            "default": "core\\browser\\omni.ja",
            #"default": "core\\omni.ja",
            "required": False,
            "description": "Internal Path to omni.ja in the exe file, absolute",
        },
        "built_in_addons_path": {
            "default": "chrome\\browser\\content\\browser\\built_in_addons.json",
            #"default": "chrome\\browser\\content\\built_in_addons.json",
            "required": False,
            "description": "Internal Path to built_in_addons.json in the omni.ja file, absolute",
        },
        "temp_path": {
            "required": False,
            "description": "Path to the folder where temporary files are stored, absolute",
        },
        "output_path": {
            "required": True,
            "description": "Path to the folder where the altered files are stored, absolute",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the process.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):

        install_exe = self.env.get('install_exe', self.env.get('pathname'))
        #print >> sys.stdout, "after join"
        #print("install_exe %s" % install_exe, file=sys.stdout)
        print("install_exe %s" % install_exe)
        new_features = self.env.get('new_features')
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('temp_path', 'working_directory')
        omni_path = self.env.get('omni_path')
        built_in_addons_path = self.env.get('built_in_addons_path')
        output_path = self.env.get('output_path', 'working_directory')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)

        if not os.path.exists(extract_directory):
            os.makedirs(extract_directory)

        sevenzipcmd = self.env.get('7ZIP_PATH')
        self.output("Extracting: %s" % install_exe)
        cmd = [sevenzipcmd, 'e', '-y', '-o%s' % extract_directory , install_exe, omni_path]
        #cmd = [sevenzipcmd, 'e', '-y', '-o%s' % extract_directory , install_exe, 'omni.ja']
        print("cmd: %s" % cmd)
        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise

        self.output("Extracted Archive Path: %s" % extract_directory)
        shutil.move(os.path.join(extract_directory, 'omni.ja'), os.path.join(extract_directory, 'omni.jar'))
        deoptimize(extract_directory, extract_directory, extract_directory)
        cmd = [sevenzipcmd, 'x', '-y', '-o%s' % extract_directory, os.path.join(extract_directory, 'omni.jar'), built_in_addons_path]

        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise
        json_file_name = os.path.join(extract_directory, built_in_addons_path)
        with open(json_file_name, "r") as read_file:
            json_data = json.load(read_file)
        json_data_sys = json_data["system"]
        # if recipe writer gave us a single name instead of a list of names,
        # convert it to a list of names
        if isinstance(self.env["new_features"], six.string_types):
            self.env["new_features"] = [self.env["new_features"]]

        for feature_name in self.env["new_features"]:
            # print >> sys.stdout, "SQL_string %s" % new_features
            try:
                json_data_sys.append(unicode(feature_name))
            except OSError as err:
                raise ProcessorError(
                    "Could not append %s: %s" % (feature_name, err))

        with open(json_file_name, 'w') as write_file:
            json.dump(json_data, write_file)
        os.chdir(extract_directory)
        cmd = [sevenzipcmd, 'u', '-y', '-w%s' % extract_directory, os.path.join(extract_directory, 'omni.jar'), built_in_addons_path, '-mm=Copy', '-mx0', '-mtc=off']
        print("cmd: %s" % cmd)
        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise
        optimize(extract_directory, extract_directory, extract_directory)
        #optimize(JAR_LOG_DIR, IN_JAR_DIR, OUT_JAR_DIR)
        dest_file_name = os.path.join(output_path, 'omni.ja')

        shutil.move(os.path.join(extract_directory, 'omni.jar'), dest_file_name)
		
if __name__ == '__main__':
    processor = MozillaOmniUpdate()
    processor.execute_shell()
