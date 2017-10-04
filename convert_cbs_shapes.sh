#!/bin/sh
# converts CBS's weird cooordination system to more normal lat lon ones.
# thanks @marrijer
# brew install gdal on a mac
for i in cbs/*.shp; do
  fn=`basename $i .shp`
  ogr2ogr -f "ESRI Shapefile" "cbs/${fn}_norm.shp" "$i" -s_srs EPSG:28992 -t_srs EPSG:4326
done
