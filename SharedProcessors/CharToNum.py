#!/usr/bin/python
#
# Copyright 2020 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2020-02-07.
#
# Calculate a number (addition) from a given string
# It gets the value of each char (a/A=1...z/Z=26) and add them.
# Return the number as a string in the output-variable [output_var].
# This can be used to generate a number from an odd formatted version with strings in it.
# See the Fiji download receipt for an example.
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

from autopkglib import Processor, ProcessorError


__all__ = ["CharToNum"]

class CharToNum(Processor):
    '''Calculate a number from a given string (a/A=1...z/Z=26) and return the number'''
    input_variables = {
        "input_var": {
            "required": True,
            "description": "string",
        },
        "output_var":{
            "required": True,
            "description": "string",
        },
    }
    
    output_variables = {
    }
   
    description = __doc__
     
    def main(self):
        inputchar = self.env["input_var"]

        self.output( "inputchar: %s" % inputchar)
        outputnum = 0
        for c in inputchar:
            outputnum = outputnum + (ord(c.upper()) - 64)
        self.env[self.env["output_var"]] = str(outputnum)



if __name__ == "__main__":
    processor = CharToNum()
    processor.execute_shell()