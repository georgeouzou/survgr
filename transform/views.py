import json

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

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

from shapely.ops import transform as shapely_transform
from shapely.geometry import shape
from shapely import speedups
if speedups.available:
	speedups.enable()


@csrf_exempt
def transform(request):
	#if request.method == "GET": raise Http404
	#if len(request.body) > 1024 * 250: raise Http404 # 250 kB	
	try:
		data = json.loads(request.body)
	except ValueError as e:
		return json_response({
				'status':'fail',
				'data':{ 'data': str(e) }
			}, status=400)

	try:
		params = data['params']
		features = data['input']
	except KeyError as e:
		return json_response({
				'status': 'fail',
				'data':{'%f  is required' % e[0]}
			}, status=400)

	# # compile transformer
	horse = WorkHorseTransformer(**params)

	for i, feat in enumerate(features):
		shapely_geometry = shape(feat['geometry']) # map to shapely object
		shapely_geometry = shapely_transform(horse, shapely_geometry) # transform feature geometry 
		feat['geometry'] = shapely_geometry.__geo_interface__ # convert to dictionary geojson interface

	return json_response({'features':features})

# utility
def json_response(data, status=200):
	return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8", status=status)	

