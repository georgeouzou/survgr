import json

from django.test import TestCase

from .transform import WorkHorseTransformer

class TransformAPITest(TestCase):
	def test_transformer_1(self):
		params = {
			'from_srid':1000005,
			'to_srid': 2100
		}
		x = [566446.108]
		y = [2529618.096]
		horse = WorkHorseTransformer(**params)
		horse(x, y)

	def test_transformer_compile(self):
		HATT_SRID = 1000000
		GGRS_SRID = 2100
		with self.assertRaises(ValueError):
			horse = WorkHorseTransformer(from_srid=HATT_SRID)
		with self.assertRaises(ValueError):
			horse = WorkHorseTransformer(to_srid=HATT_SRID)
		with self.assertRaises(ValueError):
			horse = WorkHorseTransformer(from_hatt_id=-10, to_srid=GGRS_SRID)
		with self.assertRaises(ValueError):
			horse = WorkHorseTransformer(from_srid=HATT_SRID, to_srid=GGRS_SRID)
		with self.assertRaises(ValueError):
			horse = WorkHorseTransformer(from_srid=GGRS_SRID, to_srid=HATT_SRID)

		horse = WorkHorseTransformer(from_srid=GGRS_SRID, to_srid=HATT_SRID, to_hatt_id=2)
	
	# def test_transform_features(self):
	# 	params = {
	# 		'from_srid': 1000005, # HTRS07 geocentric
	# 		'to_srid': 2100 # GGRS87/TM87
	# 	}

	# 	data = {
	# 		"type": "FeatureCollection",
	# 		"features": [
	# 		{
	# 			'type':'Feature',
	# 			'geometry':{
	# 				'type':'Point',
	# 				'coordinates':[566446.108, 2529618.096]
	# 			},
	# 			'properties':{'name': 's1'}
	# 		},
	# 		{
	# 			'type':'Feature',
	# 			'geometry':{
	# 				'type':'Linestring',
	# 				'coordinates':[[566446.108, 2529618.096],[566450.555, 2529690.1]]
	# 			},
	# 			'properties':{'name': 's2'}
	# 		},
	# 		{
	# 			'type':'Feature',
	# 			'geometry':{
	# 				'type':'Polygon',
	# 				'coordinates':[[
	# 								[566446.108, 2529618.096],[566450.555, 2529690.1],
	# 								[566458.200, 2529620.100],[566446.108, 2529618.096]
	# 							  ]]
	# 			},
	# 			'properties':{'name': 's3'}
	# 		}]
	# 	}

	# 	response = self.client.post('/transform/api/',
	# 								data=json.dumps({'params':params,'data':data}),
	# 								content_type='application/json')

	# 	self.assertTrue(response.json()['status'] == 'ok')

