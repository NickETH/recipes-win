#!/usr/bin/env python

from __future__ import absolute_import

import re
from xml.dom.minidom import parseString

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["VMwareToolsURLProvider"]

FUSION_URL_BASE = 'https://softwareupdate.vmware.com/cds/vmw-desktop/'
#DARWIN_TOOLS_URL_APPEND = 'packages/com.vmware.fusion.tools.darwin.zip.tar'
DARWIN_TOOLS_URL_APPEND = 'windows/packages/tools-windows.tar'
DEFAULT_VERSION_SERIES = '16.0.0'

class VMwareToolsURLProvider(URLGetter):
    '''Provides URL to the latest Darwin ISO of the VMware Fusion tools.'''

    input_variables = {
        'VERSION_SERIES': {
            'required': False,
            'description': 'Version of VMware Fusion to target tools of. E.g. "10.0.0". Defaults to "10.0.0"',
            },
    }
    output_variables = {
        'url': {
            'description': 'URL to the latest SourceForge project download'
        }
    }

    def get_url(self, version_series):
        try:
            #fusion_url = FUSION_URL_BASE + '/fusion.xml'
            fusion_url = FUSION_URL_BASE + '/ws-windows.xml'
            fusion_xml = self.download(fusion_url)
        except Exception as e:
            raise ProcessorError('Could not retrieve XML feed %s' % fusion_url)

        #build_re = re.compile(r'^fusion\/([\d\.]+)\/(\d+)\/')
        build_re = re.compile(r'^ws\/([\d\.]+)\/(\d+)\/')

        last_build_no = 0
        last_url_part = None

        fusion_feed = parseString(fusion_xml)

        # loop through the various products and versions in the XML file
        # to find the one we want with the correct version
        for i in  fusion_feed.getElementsByTagName('metadata'):
            productId = i.getElementsByTagName('productId')[0].firstChild.nodeValue
            version = i.getElementsByTagName('version')[0].firstChild.nodeValue
            url = i.getElementsByTagName('url')[0].firstChild.nodeValue
            #self.output('ProdId: %s, Build: %s' % (productId, version))
            if productId == 'ws-windows' and version == version_series:
                self.output('ProdId: %s, Build: %s, URL: %s' % (productId, version, url))
                #self.output('build_ver: %s, build_no: %s, url_part: %s' % (build_ver, build_no, url_part))
                match = build_re.search(url)

                if match:
                    build_ver = match.group(1)
                    build_no = match.group(2)
                    url_part = match.group(0)
                    self.output('build_ver: %s, build_no: %s, url_part: %s' % (build_ver, build_no, url_part))
                    if int(build_no) > int(last_build_no):
                        last_build_no = build_no
                        last_url_part = url_part

        if last_url_part:
            self.output('Version: %s, Build: %s' % (build_ver, build_no))
            return FUSION_URL_BASE + last_url_part + DARWIN_TOOLS_URL_APPEND
        else:
            raise ProcessorError('Could not find suitable version/build')

    def main(self):
        version_series = self.env.get('VERSION_SERIES', DEFAULT_VERSION_SERIES)

        self.env['url'] = self.get_url(version_series)
        self.output('File URL %s' % self.env['url'])
