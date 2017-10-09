#!/usr/bin/env python
import sys
from pprint import pprint

import fiona
import shapely
import shapely.geometry

from unicode_csv import UnicodeWriter


def get_shapes(shape_file):
    shapes = []
    with fiona.open(sys.argv[1]) as shape_records:
        shapes = [
            (shapely.geometry.asShape(s['geometry']), s['properties'],)
            for s in shape_records]
    return shapes


def main():
    shapes = get_shapes(sys.argv[1])
    writer = UnicodeWriter(sys.stdout)
    writer.writerow([
        'buurt_code', 'buurt_naam', 'wijk_code', 'gem_code',
        'gem_naam'])
    for geom, props in shapes:
        out_row = []
        for fld in [
            u'BU_CODE', u'BU_NAAM', u'WK_CODE',
            u'GM_CODE', u'GM_NAAM'
        ]:
            out_row.append(props[fld])
        writer.writerow(out_row)
    return 0

if __name__ == '__main__':
    sys.exit(main())
