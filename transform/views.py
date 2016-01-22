import json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from hatt.models import Hattblock
from transform import WorkHorseTransformer, DATUMS, REF_SYS, TransformerError

def index(request):
	q = [{'srid':srid, 'name':rs.name, 'datum': DATUMS[rs.datum_id]}  for srid, rs in REF_SYS.iteritems()]
	return render(request, 'transform/index.html', {'ref_systems':q})

def hattblock_info(request, id):
	try:
		hb = Hattblock.objects.get(id=id)
	except Hattblock.DoesNotExist:
		return JsonResponse({'error':'Hattblock does not exist.'}, status=404)

	hb = {
		'id': hb.id,
		'name': hb.name,
		'center_lon': hb.center_lon,
		'center_lat': hb.center_lat,
		'okxe_coefficients': {c.type: c.value for c in hb.okxecoefficient_set.all()}
	}
	return HttpResponse(json.dumps(hb, ensure_ascii=False), content_type="application/json; charset=utf-8")
	
@csrf_exempt
def transform(request):
	if request.method == "GET": raise Http404
	if len(request.body) > 1024 * 250: raise Http404 # 250 kB
	
	try:
		data = json.loads(request.body)
	except ValueError:
		return JsonResponse({'error':'Could not parse JSON object.'})

	print 'size of data = %d bytes' % len(request.body)
	del request
	
	params = data['params']
	geometries = data['geometries']
	
	from shapely.ops import transform as shape_transform
	from shapely.geometry import asShape
	
	
	horse = WorkHorseTransformer(**params)

	for i, geom in enumerate(geometries):
		geometries[i] = shape_transform(horse, asShape(geom)).__geo_interface__

	#return JsonResponse({'geometries':geometries, 'log':horse.log()})
	return HttpResponse(json.dumps({'geometries':geometries, 'log':horse.log()}, ensure_ascii=False), content_type="application/json;charset=utf-8")

		
		
		

