import json
import io
import csv
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ReferencePointsForm, TransformationType
from . import fit

# utility
def json_response(data, status=200):
	return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8", status=status)

def index(request):
	form = ReferencePointsForm()
	return render(request, 'procrustes/index.html', { 'form': form })

def _read_reference_points(fp):
	fieldnames = ['id', 'sx', 'sy', 'tx', 'ty']
	reader = csv.DictReader(fp, fieldnames=fieldnames, delimiter=' ', skipinitialspace=True)
	data = np.array([(float(p['sx']), float(p['sy']), float(p['tx']), float(p['ty'])) for p in reader])
	source_coords = data[:, 0:2]
	target_coords = data[:, 2:4]
	return (source_coords, target_coords)

def upload_reference(request):
	if request.method == 'POST':
		form_data = ReferencePointsForm(request.POST, request.FILES)
		if form_data.is_valid():
			f = io.TextIOWrapper(form_data.cleaned_data['points'], encoding='utf-8')
			source_coords, target_coords = _read_reference_points(f)

			transf_type = TransformationType(int(form_data.cleaned_data['transformation_type']))
			if transf_type == TransformationType.Similarity:
				tr = fit.SimilarityTransformation2D(source_coords, target_coords)
			elif transf_type == TransformationType.Affine:
				tr = fit.AffineTransformation2D(source_coords, target_coords)
			else:
				tr = fit.PolynomialTransformation2D(source_coords, target_coords)

			transformed_coords = tr(source_coords)

			result = {
				"input": {
					"cs_source": {
						"coords": source_coords.tolist(),
						"units": "meters",
					},
					"cs_target": {
						"coords": target_coords.tolist(),
						"units": "meters",
					},
				},
				"output": {
					"cs_transformed": {
						"coords": transformed_coords.tolist(),
						"units": "meters",
					},
					"fitted_params": tr.get_parameters().tolist(),
				},
				"transformation_type": transf_type.name,
				"residual_fitting": "none",
			}
			return json_response(result)

	return index(request)
