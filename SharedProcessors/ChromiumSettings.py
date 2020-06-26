#!/usr/bin/python
#
# Copyright 2020 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2020-06-26.
#
# Alter the preference string in Chromium (MSI) installers (tested with Google Chrome and MS Edge MSI installers).
#

#from __future__ import absolute_import
#from __future__ import print_function
from __future__ import unicode_literals
import os
import shutil
import sys
import subprocess
import json
from urllib import unquote, urlencode, quote, quote_plus

from autopkglib import Processor, ProcessorError
import six
import struct

__all__ = ["ChromiumSettings"]


class ChromiumSettings(Processor):
    description = "Create a preference string for Chromium based browsers."
    input_variables = {
        "product_GUID": {
            "required": False,
            "description": "The product GUID, if needed in the preferences.",
        },
        "new_settings": {
            "required": True,
            "description": "Dict of setting(s) to add, required",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the process.",
        },
    }
    output_variables = {
        "chrm_settings_url": {
            "description": "Url-encoded string of settings."
        },
    }

    __doc__ = description

    def main(self):

        new_settings = self.env.get('new_settings')
        #print("new_settings %s" % new_settings)

        if "product_GUID" in self.env:
            product_GUID = self.env.get('product_GUID')
            product_GUID_nobrace = product_GUID.strip(u'{}')
            print("product_GUID_nobrace %s" % product_GUID_nobrace)
            msi_prod_id = {"msi_product_id": product_GUID_nobrace}
            new_settings['distribution'].update(msi_prod_id)

        #print("new_settings %s" % new_settings)
        json_new_settings = json.dumps(new_settings, separators=(',',':'))
        url_json_new_settings = quote(json_new_settings, safe="")
        #print("url_json_new_settings %s" % url_json_new_settings)



        self.env['chrm_settings_url'] = url_json_new_settings
		
if __name__ == '__main__':
    processor = ChromiumSettings()
    processor.execute_shell()
