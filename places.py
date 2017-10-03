#!/usr/bin/env python

import sys
from pprint import pprint
from copy import deepcopy
from time import sleep
import re

from googleplaces import GooglePlaces, types, lang, GooglePlacesError

from unicode_csv import UnicodeReader, UnicodeWriter

YOUR_API_KEY = 'xxxx'

google_places = GooglePlaces(YOUR_API_KEY)


def get_zip_code(place):
    sleep(1)
    place.get_details()
    # if we do not have an address info then return nothing
    if u'address_components' not in place.details:
        return u'-'

    postcodes = [
        x for x in place.details[u'address_components']
        if u'postal_code' in x[u'types']]
    if len(postcodes) > 0:
        return postcodes[0][u'long_name']
    else:
        return u'-'


def find_voting_place(row):
    result = deepcopy(row)
    try:
        query_result = google_places.nearby_search(
                location=u'%s, Nederland' % (row[0],),
                keyword=re.sub(
                    r'\(postcode:\s*(\d{4})\s*(\w{2})\)',
                    u'', row[1].replace(u'Stembureau ', u'')))
    except ValueError:
        query_result = None
    if query_result and len(query_result.places) > 0:
        place = query_result.places[0]  # always take the top one
        geo = place.geo_location
        result.append(get_zip_code(place))
        result.append(str(geo['lat']))
        result.append(str(geo['lng']))
    else:
        result.append("-")
        result.append("-")
        result.append("-")
    return result


def main():
    reader = UnicodeReader(sys.stdin)
    writer = UnicodeWriter(sys.stdout)
    writer.writerow([
        "gemeente", "stembureau", "postcode", "stemmen", "postcode_google",
        "lat", "lng"])
    for row in reader:
        result = find_voting_place(row)
        writer.writerow(result)
        sleep(1)
    return 0

if __name__ == '__main__':
    sys.exit(main())
