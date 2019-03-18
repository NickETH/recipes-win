#!/usr/bin/env python

import re
from autopkglib import Processor, ProcessorError


__all__ = ["TextSubstituer"]

class TextSubstituer(Processor):
    '''Substitute a character from a given string and return the parsed string'''
    input_variables = {
        "input_string": {
            "required": True,
            "description": "string",
        },
        "pattern_replace":{
            "required": True,
            "description": (
                "A dictionary of pattern(s)/replace(s) to be substitute\n"
                "\t pattern:replace\n"),
        },
    }
    
    output_variables = {
       "parsed_string": {
            "required": True,
            "description": "parsed string",
        },
    }
   
    description = __doc__
     
    def main(self):
        self.env["parsed_string"] = self.env["input_string"]
        for entry in self.env["pattern_replace"]:
            self.env["parsed_string"] = re.sub(entry["pattern"],entry["repl"],self.env["parsed_string"])


if __name__ == "__main__":
    processor = TextSubstituer()
    processor.execute_shell()