import json
import geojson
import pyproj

with open("./hattblocks15.json") as fp:
	js_blocks = json.load(fp)

	old_greek_to_wgs84 = pyproj.transformer.Transformer.from_crs(4815, 4326, always_xy=True)

	features = []
	for b in js_blocks:
		props = {
			'name': b['name'],
			'okxe_id': b['okxe_id'],
			'cy': b['cy'],
			'cx': b['cx'],
		}
		coords = b['geom']['coordinates']
		assert len(coords) == 1
		transformed_coords = list(old_greek_to_wgs84.itransform(coords[0])) # no poly holes, just take the 1st array
		geom = geojson.Polygon([transformed_coords], validate=True, precision=2)
		feature = geojson.Feature(id=b['id'], geometry=geom, properties=props)
		features.append(feature)

	feat_collection = geojson.FeatureCollection(features)

	with open("./hattblocks.min.geojson", "w") as fp_out:
		json.dump(feat_collection, fp_out, ensure_ascii=False)

