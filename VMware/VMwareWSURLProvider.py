#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Justin Rummel
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
# Adapted to Vmware Workstation for Windows. Hm, 20200628

from __future__ import absolute_import, print_function

import gzip
import os
import sys
import re
import collections
from distutils.version import LooseVersion
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from autopkglib import ProcessorError, URLGetter

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin


__all__ = ["VMwareWSURLProvider"]


# variables
# https://softwareupdate.vmware.com/cds/vmw-desktop/vmrc-windows.xml
# https://download3.vmware.com/software/wkst/file/VMware-workstation-full-15.5.6-16341506.exe
VMWARE_BASE_URL = "https://softwareupdate.vmware.com/cds/vmw-desktop/"
VMWARE_BASE_URL_FULL = "https://download3.vmware.com/software/wkst/file/"
WORKSTATION = "ws-windows.xml"
DEFAULT_MAJOR_VERSION = "14"
DEFAULT_VERSION_FlAVOR = "full"


class VMwareWSURLProvider(URLGetter):
    """Processor class."""

    description = "Provides URL to the latest VMware Workstation update release."
    input_variables = {
        "product_name": {
            "required": False,
            "description": "Default is '%s'." % WORKSTATION
        },
        "base_url": {
            "required": False,
            "description": "Default is '%s." % VMWARE_BASE_URL,
        },
        "base_url_full": {
            "required": False,
            "description": "Default is '%s." % VMWARE_BASE_URL_FULL,
        },
        "major_version": {
            "required": False,
            "description": "Default is '%s." % DEFAULT_MAJOR_VERSION,
        },
        "version_flavor": {
            "required": False,
            "description": "Are we targeting the full version of VMWS or the one without the platform ISO files, Default is '%s." % DEFAULT_VERSION_FlAVOR,
        },
    }
    output_variables = {
        "url": {"description": "URL to the latest VMware Workstation update release."},
        "version": {
            "description": "Version to the latest VMware Workstation update release."
        },
    }

    __doc__ = description

    def core_metadata(self, base_url, base_url_full, product_name, major_version, version_flavor):
        """Given a base URL, product name, and major version, produce the
        product download URL and latest version.
        """
        workstation_xml_url = urljoin(base_url, product_name)
        self.output("Fetching workstation.xml from {}".format(workstation_xml_url))
        vsus = self.download(workstation_xml_url, text=True)

        try:
            metaList = ElementTree.fromstring(vsus)
        except ExpatError:
            raise ProcessorError("Unable to parse XML data from string.")

        build_re = re.compile(r"^ws\/(?P<wsver>([\d\.]+))\/(?P<wsbuild>(\d+))\/windows\/core\/metadata")
        search_str = "core"

        versions = {}
        for metadata in metaList:
            version = metadata.find("version")
            url = metadata.find("url")
            #print(r"metadata-url %s" % url.text, file=sys.stdout)
            if major_version == "latest" or major_version == version.text.split(".")[0]:
                if ("core" in (url.text)):
                    # We actually want the URL, instead of the version itself
                    self.output(
                        "Found version: {} with URL: {}".format(version.text, url.text),
                        verbose_level=4,
                    )
                    match = build_re.search(url.text)
                    #print("ws-version  %s" %  match.group('wsver'))
                    if version_flavor == "full":
                        versions[match.group('wsver')] = "VMware-workstation-full-%s-%s.exe" % (match.group('wsver'), match.group('wsbuild'))
                        base_url = base_url_full
                    else:
                        versions[match.group('wsver')] = url.text

        if not versions:
            raise ProcessorError(
                "Could not find any versions for the "
                "major_version '%s'." % major_version
            )
        latest_version_key = sorted(versions.keys(), key=LooseVersion)[-1]
        # print("latest_version_key  %s" %  latest_version_key)
        # print("sorted versions  %s" %  sorted(versions))
		
        self.output(
            "Latest version URL suffix: {}".format(versions[latest_version_key]), verbose_level=2
        )
        full_url = urljoin(base_url, versions[latest_version_key])
        self.output("URL: {}".format(full_url), verbose_level=2)
        download_dir = os.path.join(self.env["RECIPE_CACHE_DIR"], "downloads")
        try:
            os.makedirs(download_dir)
        except os.error:
            # Directory already exists
            pass
        if version_flavor == "full":
            return (
                full_url,
                latest_version_key,
            )
        else:
            temp_file = os.path.join(download_dir, "metadata.xml.gz")
            vLatest = self.download_to_file(full_url, temp_file)
            try:
                with gzip.open(vLatest, "rb") as f:
                    data = f.read()
            except Exception as e:
                raise ProcessorError(e)

            try:
                metadataResponse = ElementTree.fromstring(data)
            except ExpatError:
                raise ProcessorError("Unable to parse XML data from string.")

            relativePath = metadataResponse.find(
                "bulletin/componentList/component/relativePath"
            )
            return (
                full_url.replace("metadata.xml.gz", relativePath.text),
                latest_version_key,
            )

    def main(self):
        """Main process."""

        # Gather input variables
        product_name = self.env.get("product_name", WORKSTATION)
        base_url = self.env.get("base_url", VMWARE_BASE_URL)
        base_url_full = self.env.get("base_url", VMWARE_BASE_URL_FULL)
        major_version = self.env.get("major_version", DEFAULT_MAJOR_VERSION)
        version_flavor = self.env.get("version_flavor", DEFAULT_VERSION_FlAVOR)

        # Look up URL and set output variables
        self.env["url"], self.env["version"] = self.core_metadata(
            base_url, base_url_full, product_name, major_version, version_flavor
        )
        self.output("Found URL: %s" % self.env["url"])
        self.output("Found Version: %s" % self.env["version"])


if __name__ == "__main__":
    processor = VMwareWSURLProvider()
    processor.execute_shell()
