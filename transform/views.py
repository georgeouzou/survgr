import json
from io import TextIOWrapper

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from shapely.ops import transform as shapely_transform
from shapely.geometry import shape
from shapely import speedups
if speedups.available:
	speedups.enable()

from .hatt.models import Hattblock
from .transform import WorkHorseTransformer, DATUMS, REF_SYS, TransformerError
from .drivers import csv_driver

def index(request):
	q = [{'srid':srid, 'name':rs.name, 'datum': DATUMS[rs.datum_id]}  for srid, rs in REF_SYS.items()]
	return render(request, 'transform/index.html', {'ref_systems':q})

def hattblock_info(request, id):
	try:
		hb = Hattblock.objects.get(id=id)
	except Hattblock.DoesNotExist:
		raise Http404

	hb = {
		'id': hb.id,
		'name': hb.name,
		'center_lon': hb.center_lon,
		'center_lat': hb.center_lat,
		'okxe_coefficients': {c.type: c.value for c in hb.okxecoefficient_set.all()}
	}
	return json_response(hb)

@csrf_exempt
def transform(request):
	
	params = {}
	for n, v in request.POST.items():
		if n in ['from_srid', 'to_srid', 'from_hatt_id', 'to_hatt_id']:
			params[n] = int(v)

	horse = WorkHorseTransformer(**params);

	if request.POST['input_type'] == "csv":
		inp = TextIOWrapper(request.FILES['input'].file, encoding='utf-8')
		out = csv_driver.transform(horse, inp, 
			csv_delimiter=request.POST['csv_delimiter'],
			csv_fields=request.POST['csv_fields'].split(','))

	return HttpResponse(out, content_type='text/plain')


# @csrf_exempt
# def transform(request):
# 	#if request.method == "GET": raise Http404	
# 	# first decode json data into a python dict
# 	# request body is a bytestring and json loads only decodes unicode
# 	try:
# 		geojson = json.loads(request.read().decode("utf-8"))
# 	except ValueError as e:
# 		return json_response({'status':'error',
# 			'message': 'Invalid request: could not parse json data, %s' % str(e)}, status=400)
	
# 	try:
# 		params = geojson['params']
# 		data = geojson['data']
# 		data_type = data['type'].lower()
# 	except:
# 		return json_response({'status': 'error', 
# 			'message':'Invalid request: see documentation for json data format'}, status=400)


# 	# ready transformer based on params 
# 	horse = WorkHorseTransformer(**params)
# 	# secondly get the parameters needed for the transformation and the
# 	# feature collection that was provided
	
# 	# transform each feature's geometry 
# 	for feat in features:
# 		feat['geometry'] = shapely_transform(horse, shape(feat['geometry'])).__geo_interface__

# 	return json_response({'status':'ok', 
# 						  'output':{'type':'FeatureCollection', 'features':features}})

# utility
def json_response(data, status=200):
	return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8", status=status)

