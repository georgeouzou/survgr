import json

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
	#if request.method == "GET": raise Http404
	#if len(request.body) > 1024 * 250: raise Http404 # 250 kB	

	# first decode json data into a python dict
	# request body is a bytestring and json loads only decodes unicode
	try:
		data = json.loads(request.read().decode("utf-8"))
	except ValueError as e:
		return json_response({'status':'error',
			'message': 'Invalid request: could not parse json data, %s' % str(e)}, status=400)
	
	# secondly get the parameters needed for the transformation and the
	# feature collection that was provided
	try:
		params = data['params']
		features = data['input']['features']
	except KeyError as e:
		return json_response({'status': 'error', 
			'message':'Invalid request: %s is required' % str(e)}, status=400)

	print(params, features)
	# ready transformer based on params 
	horse = WorkHorseTransformer(**params)

	# transform each feature's geometry 
	for feat in features:
		feat['geometry'] = shapely_transform(horse, shape(feat['geometry'])).__geo_interface__

	return json_response({'status':'ok', 
						  'output':{'type':'FeatureCollection', 'features':features}})

# utility
def json_response(data, status=200):
	return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8", status=status)

