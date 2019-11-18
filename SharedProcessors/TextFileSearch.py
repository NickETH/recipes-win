#!/usr/bin/env python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-11-09.
#
# Searches a text file for a regex pattern and returns it in "matchstring".
#
# Based on TextFileReader by Zack T (mlbz521)
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

import re
import os.path
from autopkglib import Processor, ProcessorError

__all__ = ["TextFileSearch"]

class TextFileSearch(Processor):

    """This processor reads a text file and looks for a regex pattern and returns the string 
    that matched the pattern.
    """

    input_variables = {
        "file_to_open": {
            "required": True,
            "description": "The text file that needs to be opened for reading.",
        },
        "pattern": {
            "required": True,
            "description": "The regex pattern to look for and return.",
        }
    }
    output_variables = {
        "matchstring": {
            "description": "Returns the string that matched the pattern."
        }
    }

    description = __doc__

    def main(self):

        # Define variables
        file_to_open = self.env.get('file_to_open')
        pattern = self.env.get('pattern')


        # Wrap all other actions in a try/finally so the image is always unmounted.
        try:            
            # Open, read, and close file
            file = open(file_to_open, 'r')
            contents = file.read()
            file.close()

                # Look for a match
            line = re.search(pattern + r'.*', contents)
            match = re.split(pattern, line.group())[1]

            if match:
                self.env["matchstring"] = match
                self.output("matchstring: {}".format(self.env["matchstring"]))

        except BaseException as err:
            raise ProcessorError("Unable to find a match based on the pattern provided.")


if __name__ == "__main__":
    processor = TextFileSearch()
    processor.execute_shell()
