import json
import io
import csv
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ReferencePointsForm
from .fit import *

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
			f = io.TextIOWrapper(form_data.cleaned_data['reference_points'], encoding='utf-8')
			source_coords, target_coords = _read_reference_points(f)

			transf_type = TransformationType(int(form_data.cleaned_data['transformation_type']))
			if transf_type == TransformationType.Similarity:
				tr = SimilarityTransformation2D(source_coords, target_coords)
			elif transf_type == TransformationType.Affine:
				tr = AffineTransformation2D(source_coords, target_coords)
			else:
				tr = PolynomialTransformation2D(source_coords, target_coords)

			tr_stats = ResidualStatistics(source_coords, target_coords, tr)

			rescor_type = ResidualCorrectionType(int(form_data.cleaned_data['residual_correction_type']))
			has_residual_correction = rescor_type != ResidualCorrectionType.NoCorrection
			if rescor_type == ResidualCorrectionType.Collocation:
				cov_function_type = CovarianceFunctionType(int(form_data.cleaned_data['cov_function_type']))
				rescor = Collocation(source_coords, target_coords, tr, cov_function_type)

			has_validation = form_data.cleaned_data['validation_points'] is not None
			if has_validation:
				f = io.TextIOWrapper(form_data.cleaned_data['validation_points'], encoding='utf-8')
				val_source_coords, val_target_coords = _read_reference_points(f)
				val_stats = ResidualStatistics(val_source_coords, val_target_coords, tr)
				if has_residual_correction:
					val_stats_rescor = ResidualStatistics(val_source_coords, val_target_coords, rescor)
			else:
				validation_statistics = None

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
				"transformation": {
					"type": transf_type.name,
					"fitted_parameters": tr.get_parameters().tolist(),
					"statistics": tr_stats.__dict__,
				},
			}

			if has_residual_correction:
				collocation = rescor
				result["collocation"] = {
					"distance_intervals": collocation.cov_func.distance_intervals.tolist(),
					"empirical_cov": collocation.cov_func.empirical_cov.tolist(),
					"fitted_cov": collocation.cov_func.fitted_cov.tolist(),
				}

			if has_validation:
				result["transformation"]["validation_statistics"] = val_stats.__dict__
				if has_residual_correction:
					result["collocation"]["validation_statistics"] = val_stats_rescor.__dict__

			return json_response(result)

	return index(request)
