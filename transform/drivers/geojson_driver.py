import geojson
from shapely.ops import transform as shapely_transform
from shapely.geometry import shape
from shapely import speedups
if speedups.available:
	speedups.enable()


def transform(transformer, fp):
	js = geojson.load(fp)
	# check type of geojson 
	if js['type'] == 'Feature':
		js['geometry'] = shapely_transform(transformer, shape(js['geometry'])).__geo_interface__
	elif js['type'] == 'FeatureCollection':
		for feat in js['features']:
			feat['geometry'] = shapely_transform(transformer, shape(feat['geometry'])).__geo_interface__
	elif js['type'] == 'GeometryCollection':
		for i, geom in enumerate(js['geometries']):
			js['geometries'][i] = shapely_transform(transformer, shape(geom)).__geo_interface__
	else: #point, linestring, polygon, multis, geometry collection
		js = shapely_transform(transformer, shape(js)).__geo_interface__

	return js

	