#!/usr/bin/env python
import sys
import os
import re
from glob import glob
from pprint import pprint
from copy import deepcopy

from unicode_csv import UnicodeReader, UnicodeWriter


def get_places(places_file):
    places_file = UnicodeReader(open(places_file))
    headers = places_file.next()
    return [dict(zip(headers, r)) for r in places_file]


def find_place_by_postcode(places, postcode, source_field=u'postcode'):
    candidate_places = [
        p for p in places if
        p[source_field] == postcode]
    if len(candidate_places) > 0:
        return candidate_places[0]


def main():
    if len(sys.argv) < 3:
        print >>sys.stderr, "Usage: merge.py <file1> <file2>"
        return 1
    places = get_places(sys.argv[2])
    election_file = UnicodeReader(open(sys.argv[1]))
    headers = election_file.next()

    writer = UnicodeWriter(sys.stdout)
    writer.writerow([
        "gemeente", "stembureau", "postcode", "stemmen", "postcode_google",
        "lat", "lng", "stembureau2017", "lat2017", "lon2017"])

    for row in election_file:
        result = dict(zip(headers, row))
        place = None
        if result[u'postcode'] != u'-':
            place = find_place_by_postcode(
                places, re.sub(r'\s+', u'', result[u'postcode']))
        elif result[u'postcode_google'] != u'':
            place = find_place_by_postcode(
                places, re.sub(r'\s+', u'', result[u'postcode']))
        result_row = deepcopy(row)
        if place is not None:
            result_row.append(place[u'stembureau'])
            result_row.append(place[u'Longitude'])
            result_row.append(place[u'Latitude'])
        else:
            result_row.append(u'-')
            result_row.append(u'-')
            result_row.append(u'-')
        # if result_row[-1] != u'-':
        #     pprint(result_row)
        writer.writerow(result_row)
    return 0

if __name__ == '__main__':
    sys.exit(main())
