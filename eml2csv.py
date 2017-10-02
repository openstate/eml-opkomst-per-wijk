#!/usr/bin/env python
import sys
import os
import re
from glob import glob
from pprint import pprint
import codecs
import csv, codecs, cStringIO

from lxml import etree


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

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
            for selection in ruv.xpath('.//eml:Selection[eml:AffiliationIdentifier]', namespaces=namespaces):
                party = u''.join(
                    selection.xpath(
                        './eml:AffiliationIdentifier/eml:RegisteredName//text()',
                        namespaces=namespaces))
                votes = u''.join(selection.xpath('./eml:ValidVotes//text()', namespaces=namespaces))
                result.append([county,buro,post_code,party,votes])
        # pprint(xml)
    return result

def main():
    writer = UnicodeWriter(sys.stdout)
    writer.writerow(["gemeente","stembureau","postcode","partij","stemmen"])
    for file_path in get_file_paths():
        rows = parse_eml_file(file_path)
        writer.writerows(rows)
    return 0

if __name__ == '__main__':
    sys.exit(main())
