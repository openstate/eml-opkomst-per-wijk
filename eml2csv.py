#!/usr/bin/env python
import sys
import os
import re
from glob import glob
from pprint import pprint
import codecs

from lxml import etree

from unicode_csv import UnicodeWriter


def get_file_paths():
    """
    Returns counting files
    """
    return glob('./eml/2014/*/Telling*')

def parse_eml_file(file_path):
    """
    Parses an eml file and returns results.
    """
    result = []
    with codecs.open(file_path, 'r', 'utf-8') as in_file:
        content = in_file.read()
        try:
            xml = etree.fromstring(content)
        except Exception as e:
            content = re.sub(r'^\s*\<\?[^\?]*\?\>', '', content)
            xml = etree.fromstring(content)
        # Ugh, we need to know the namespaces. Ugly hack. For som reason
        # etree does not query the default declared namespace, so you have to
        # be explicit.
        namespaces = xml.nsmap
        eml_ns = namespaces[None]
        del namespaces[None]
        namespaces['eml'] = eml_ns

        county = u''.join(
            xml.xpath(
                '//eml:ManagingAuthority/eml:AuthorityIdentifier//text()',
                namespaces=namespaces))
        for ruv in xml.xpath('//eml:ReportingUnitVotes', namespaces=namespaces):
            buro = u''.join(
                ruv.xpath('./eml:ReportingUnitIdentifier//text()', namespaces=namespaces))
            buro_parts = buro.split(' ')
            if 'postcode' in buro:
                m = re.search(r'\(postcode:\s*(\d{4})\s*(\w{2})\)', buro)
                if m is not None:
                    post_code = u'%s %s' % (m.group(1), m.group(2),)
                else:
                    post_code = u'-'
            else:
                post_code = '-'
            total_votes = 0
            for selection in ruv.xpath('.//eml:Selection[eml:AffiliationIdentifier]', namespaces=namespaces):
                party = u''.join(
                    selection.xpath(
                        './eml:AffiliationIdentifier/eml:RegisteredName//text()',
                        namespaces=namespaces))
                try:
                    total_votes += int(
                        u''.join(selection.xpath(
                            './eml:ValidVotes//text()',
                            namespaces=namespaces)))
                except ValueError:
                    pass
            result.append([county, buro, post_code, str(total_votes)])
        # pprint(xml)
    return result


def main():
    writer = UnicodeWriter(sys.stdout)
    writer.writerow(["gemeente","stembureau","postcode","stemmen"])
    for file_path in get_file_paths():
        rows = parse_eml_file(file_path)
        writer.writerows(rows)
    return 0

if __name__ == '__main__':
    sys.exit(main())
