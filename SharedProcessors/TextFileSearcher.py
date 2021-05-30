#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-09.
#
# Searches a text file for a regex pattern and returns it in "match".
#
# Based on URLTextSearcher.py, Copyright 2014 Jesse Peterson
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
#
# 20210527 Nick Heim: Python v3 changes

"""See docstring for TextFileSearcher class"""

import re
import os.path
from autopkglib import Processor, ProcessorError

MATCH_MESSAGE = "Found matching text"
NO_MATCH_MESSAGE = "No match found on URL"

__all__ = ["TextFileSearcher"]


class TextFileSearcher(Processor):
    """Loads a file and performs a regular expression match
    on the text.

    Requires version 1.4."""

    input_variables = {
        "file_to_open": {
            "required": True,
            "description": "The text file that needs to be opened for reading.",
        },
        "re_pattern": {
            "description": "Regular expression (Python) to match against file.",
            "required": True,
        },
        "result_output_var_name": {
            "description": (
                "The name of the output variable that is returned "
                "by the match. If not specified then a default of "
                '"match" will be used.'
            ),
            "required": False,
            "default": "match",
        },
        "re_flags": {
            "description": (
                "Optional array of strings of Python regular "
                "expression flags. E.g. IGNORECASE."
            ),
            "required": False,
        },
    }
    output_variables = {
        "result_output_var_name": {
            "description": (
                "First matched sub-pattern from input found on the fetched "
                "file. Note the actual name of variable depends on the input "
                'variable "result_output_var_name" or is assigned a default of '
                '"match."'
            )
        }
    }

    description = __doc__

    def re_search(self, content):
        """Search for re_pattern in content"""
        flag_accumulator = 0
        for flag in self.env.get("re_flags", {}):
            if flag in re.__dict__:
                flag_accumulator += re.__dict__[flag]
        re_pattern = re.compile(self.env["re_pattern"], flags=flag_accumulator)
        match = re_pattern.search(content)

        if not match:
            # raise ProcessorError("No match found in file: {}".format(self.env["file_to_open"]))
            raise ProcessorError(f"{NO_MATCH_MESSAGE}: {self.env['url']}")

        # return the last matched group with the dict of named groups
        return (match.group(match.lastindex or 0), match.groupdict())

    def main(self):
        # Define variables
        output_var_name = self.env["result_output_var_name"]
        file_to_open = self.env.get('file_to_open')
        re_pattern = self.env.get('re_pattern')

        try:            
            # Open, read, and close file
            file = open(file_to_open, 'r')
            contents = file.read()
            file.close()
        except BaseException as err:
            raise ProcessorError("Unable to open the file.")

        # print("content: %s" % contents)
        # Search in content
        groupmatch, groupdict = self.re_search(contents)

        # favor a named group over a normal group match
        if output_var_name not in groupdict.keys():
            groupdict[output_var_name] = groupmatch

        self.output_variables = {}
        for key in groupdict.keys():
            self.env[key] = groupdict[key]
            # self.output("Found matching text ({}): {}".format(key, self.env[key]))
            self.output(f"{MATCH_MESSAGE} ({key}): {self.env[key]}")
            self.output_variables[key] = {
                "description": "Matched regular expression group"
            }


if __name__ == "__main__":
    PROCESSOR = TextFileSearcher()
    PROCESSOR.execute_shell()
