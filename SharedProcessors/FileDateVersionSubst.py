#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-04-01.
# Based on FileCreator by Per Olofsson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Load a file and search for date and version patterns and actualize them. 

"""Processor that searches for date and version patterns and actualize 'em."""

import os
import re
import time
from autopkglib import Processor, ProcessorError


__all__ = ["FileDateVersionSubst"]


class FileDateVersionSubst(Processor):
    """Search for date and version patterns and actualize 'em."""
    description = __doc__
    input_variables = {
        "file_path": {
            "required": True,
            "description": "Path to a file to create.",
        },
        "new_ver": {
            "required": False,
            "description": "New version string to write.",
        },
        're_pattern': {
            'description': 'Regular expression of version string to replace.',
            'required': True,
        },
    }
    output_variables = {
    }

    def main(self):
        ts = time.localtime()
        us_date = time.strftime("%y%m%d",ts)
        us_date_lng = time.strftime("%Y%m%d",ts)
        file_path = self.env.get('file_path')
        try:
            with open(self.env['file_path'], "r") as fileref:
                content = fileref.read()
            content_new = re.sub('[^0][1-2][0-9][0-1][0-9][0-3][0-9](?=[^\d])', us_date, content, flags = re.M)
            content = content_new
            content_new = re.sub('[2][0][1-2][0-9][0-1][0-9][0-3][0-9](?=[^\d])', us_date_lng, content, flags = re.M)
            if {"new_ver", "re_pattern"}.issubset(self.env):
                new_ver = self.env.get('new_ver')
                re_pattern = self.env.get('re_pattern')
                content = content_new
                content_new = re.sub(re_pattern, new_ver, content, flags = re.M)
            # print >> sys.stdout, "recipe_path %s" % recipe_path
            with open(self.env['file_path'], "w") as fileref:
                fileref.write(content_new)
        except BaseException, err:
            raise ProcessorError("Can't change file at %s: %s"
                                 % (self.env['file_path'], err))

if __name__ == '__main__':
    PROCESSOR = FileDateVersionSubst()
    PROCESSOR.execute_shell()

