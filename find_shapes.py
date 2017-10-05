#!/usr/bin/env python
import sys
import os
import re
from pprint import pprint
from copy import deepcopy

import fiona
import shapely
import shapely.geometry

from unicode_csv import UnicodeReader, UnicodeWriter


def get_shapes(shape_file):
    shapes = []
    with fiona.open(sys.argv[1]) as shape_records:
        shapes = [
            (shapely.geometry.asShape(s['geometry']), s['properties'],)
            for s in shape_records]
    return shapes


def main():
    if len(sys.argv) < 6:
        print >>sys.stderr, "Usage: merge.py <shape_file> <lat_field> <lon_field> <lat_fallbck> <lon_fallback>"
        return 1

    reader = UnicodeReader(sys.stdin)
    writer = UnicodeWriter(sys.stdout)
    header = reader.next()
    shapes = get_shapes(sys.argv[1])

    out_header = deepcopy(header)
    out_header += [
        'buurt_code', 'buurt_naam', 'wijk_code', 'wijk_naam', 'gem_code',
        'gem_naam']
    writer.writerow(out_header)

    lat_field = sys.argv[2]
    lon_field = sys.argv[3]
    lat_fb_field = sys.argv[4]
    lon_fb_field = sys.argv[5]

    for row in reader:
        out_row = deepcopy(row)
        data = dict(zip(header, row))
        if (data[lon_field] != u'-') and (data[lat_field] != u''):
            lat = data[lat_field]
            lon = data[lon_field]
        else:
            lat = data[lat_fb_field]
            lon = data[lon_fb_field]
        if (lat != u'-') and (lon != u'-'):
            point = shapely.geometry.Point(float(lat), float(lon))
            for shape, props in shapes:
                if shape.contains(point):
                    for fld in [
                        u'BU_CODE', u'BU_NAAM', u'BU_CODE', u'BU_NAAM',
                        u'GM_CODE', u'GM_NAAM'
                    ]:
                        out_row.append(props[fld])
                    break
        if len(out_row) == len(row):  # if we did not find anything
            out_row += [u'-', u'-', u'-', u'-', u'-', u'-']
        writer.writerow(out_row)

    return 0

if __name__ == '__main__':
    sys.exit(main())
