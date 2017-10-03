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


def get_score(name1, name2):
    parts1 = re.split(r'\s+', name1)
    parts2 = re.split(r'\s+', name2)
    intersection = list(set(parts1) & set(parts2))
    union = list(set(parts1) | set(parts2))
    return float(len(intersection))/float(len(union))


def find_place_by_muni_and_name(places, muni, name):
    candidate_places = [p for p in places if p[u'plaats'] == muni]
    clean_name = re.sub(
        r'^Stembureau\s+', u'',
        re.sub(r'\(postcode:\s*(\d{4})\s*(\w{2})\)', u'',  name))
    place = None
    max_score = 0.0
    for p in candidate_places:
        score = get_score(p['stembureau'], clean_name)
        if (score > 0.0) and (score > max_score):
            place = p
            max_score = score
    return place


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
        if place is None:
            place = find_place_by_muni_and_name(
                places, result[u'gemeente'], result[u'stembureau'])
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
