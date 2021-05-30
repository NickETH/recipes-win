#!/usr/bin/python
#
# Copyright 2019 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2019-03-17.
# Based on WinInstallerExtractor by Matt Hansen
#
# Returns date and time in variables.

import os
import sys
import subprocess
import time

from autopkglib import Processor, ProcessorError


__all__ = ["DateTimeStamps"]


class DateTimeStamps(Processor):
    description = "Returns date and time in variables."
    input_variables = {
    }
    output_variables = {
        "us_date": {
            "description": "Actual date in US style.",
        },
        "year": {
            "description": "Actual year.",
        },
        "month": {
            "description": "Actual month.",
        },
        "day": {
            "description": "Actual day.",
        },
        "time": {
            "description": "Actual time."
        },
    }

    __doc__ = description

    def main(self):

        ts = time.localtime()
        self.env['us_date'] = time.strftime("%Y%m%d",ts)
        self.env['year'] = time.strftime("%Y",ts)
        self.env['month'] = time.strftime("%m",ts)
        self.env['day'] = time.strftime("%d",ts)
        self.env['time'] = time.strftime("%H:%M:%S",ts)
        self.output("Variables for date, year, month, day, time set")

if __name__ == '__main__':
    processor = DateTimeStamps()
    processor.execute_shell()
