#!/usr/bin/env python

import sys
from pprint import pprint
import csv
import codecs
import cStringIO
from copy import deepcopy
from time import sleep
import re

from googleplaces import GooglePlaces, types, lang, GooglePlacesError

YOUR_API_KEY = 'xxx'

google_places = GooglePlaces(YOUR_API_KEY)


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

# # You may prefer to use the text_search API, instead.
# query_result = google_places.nearby_search(
#         location='Zwijdrecht, Nederland', keyword='Winkelcentrum Walburg')
# # If types param contains only 1 item the request to Google Places API
# # will be send as type param to fullfil:
# # http://googlegeodevelopers.blogspot.com.au/2016/02/changes-and-quality-improvements-in_16.html
#
# if query_result.has_attributions:
#     print query_result.html_attributions
#
#
# for place in [query_result.places[0]]:
#     # Returned places from a query are place summaries.
#     print place.name
#     print place.geo_location
#     print place.place_id
#
#     # The following method has to make a further API call.
#     place.get_details()
#     # Referencing any of the attributes below, prior to making a call to
#     # get_details() will raise a googleplaces.GooglePlacesAttributeError.
#     pprint(place.details)  # A dict matching the JSON response from Google.


def get_zip_code(place):
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
        sleep(5)
    return 0

if __name__ == '__main__':
    sys.exit(main())
