#!/usr/bin/env python

from autopkglib import Processor, ProcessorError


__all__ = ["RenameVar"]

class RenameVar(Processor):
    '''Substitute a character from a given string and return the parsed string'''
    input_variables = {
        "input_var": {
            "required": True,
            "description": "string",
        },
        "rename_var":{
            "required": True,
            "description": "string",
        },
    }
    
    output_variables = {
    }
   
    description = __doc__
     
    def main(self):
        self.env[self.env["rename_var"]] = self.env["input_var"]


if __name__ == "__main__":
    processor = RenameVar()
    processor.execute_shell()