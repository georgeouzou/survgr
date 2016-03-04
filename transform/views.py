import json
from io import TextIOWrapper

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .hatt.models import Hattblock
from .transform import WorkHorseTransformer, DATUMS, REF_SYS
from .drivers import csv_driver, geojson_driver

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

	# TODO: Add exception support
	try:
		horse = WorkHorseTransformer(**params);
	except ValueError as e:
		return HttpResponse(str(e), status=404)

	try:
		input_type = request.POST['input_type']
		inp = TextIOWrapper(request.FILES['input'].file, encoding='utf-8')
		if input_type == "csv":
			out = csv_driver.transform(horse, inp, 
				delimiter=request.POST['csv_delimiter'],
				fieldnames=request.POST['csv_fields'])
			return HttpResponse(out, content_type='text/plain;charset=utf-8')
		elif input_type == "geojson":
			out = geojson_driver.transform(horse, inp)
			return HttpResponse(out, content_type='text/plain;charset=utf-8')
	except Exception:
		return HttpResponse('Bad data', status=404)


# utility
def json_response(data, status=200):
	return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8", status=status)

