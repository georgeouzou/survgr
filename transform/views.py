import json
from io import TextIOWrapper

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .hatt.models import Hattblock
from .transform import WorkHorseTransformer, DATUMS, REF_SYS
from .drivers import csv_driver, geojson_driver

def index(request):
	q = [{'srid':srid, 'name':rs.name, 'datum': DATUMS[rs.datum]}  for srid, rs in REF_SYS.items()]
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

	if 'okxe_inverse_type' in request.POST:
		params['okxe_inverse_type'] = request.POST['okxe_inverse_type']

	# TODO: Add better exception support
	try:
		if 'procrustes' in request.FILES:
			params['procrustes'] = json.loads(request.FILES['procrustes'].read())

		transformer = WorkHorseTransformer(**params)
		print(transformer.log_str())

		input_type = request.POST['input_type']
		inp = TextIOWrapper(request.FILES['input'].file, encoding='utf-8')
		if input_type == "csv":
			#decimal degrees need 9 decimals for ~1mm accuracy, meters need 3
			#so xy will either be degrees or meters and z will be meters
			#http://wiki.gis.com/wiki/index.php/Decimal_degrees
			xy_decimals = 9 if transformer.to_refsys.is_longlat() else 3
			z_decimals = 3
			csv_result = csv_driver.transform(transformer, inp,
			    (xy_decimals, xy_decimals, z_decimals),
				fieldnames=request.POST['csv_fields'])
			return json_response({
				"type": "csv",
				"result": csv_result.read(),
				"steps": transformer.transformation_steps,
			})
		elif input_type == "geojson":
			gj_result = geojson_driver.transform(transformer, inp)
			return json_response({
				"type": "geojson",
				"result": gj_result,
				"steps": transformer.transformation_steps,
			})
	except Exception as e:
		return HttpResponse('Bad data', status=404)

# utility
def json_response(data, status=200):
	return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8", status=status)

