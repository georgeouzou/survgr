import json
import io
import csv
from dataclasses import dataclass
import numpy as np
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ReferencePointsForm
from .fit import *

@dataclass
class Point:
    id: str
    is_ref: bool
    x_src: float
    y_src: float
    x_dst: float
    y_dst: float

# utility
def json_response(data, status=200):
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8", status=status)

def index(request):
    form = ReferencePointsForm()
    return render(request, 'procrustes/index.html', {'form': form})

def _read_points(fp):
    dialect = csv.Sniffer().sniff(fp.readline(), delimiters=";, \t")
    fp.seek(0)

    if dialect.delimiter in [' ', '\t']:
        sep = '\s+'
    else:
        sep = dialect.delimiter

    field_names = ['id', 'is_ref', 'x_src', 'y_src', 'x_dst', 'y_dst']
    field_dtype = {
        field_names[0]: str,
        field_names[1]: str,
        field_names[2]: float,
        field_names[3]: float,
        field_names[4]: float,
        field_names[5]: float,
    }
    df = pd.read_csv(fp,
        sep=sep,
        names=field_names,
        dtype=field_dtype,
        index_col=field_names[0],
        skipinitialspace=True,
        skip_blank_lines=True,
        decimal='.')

    if df.isna().values.any():
        raise ValueError('missing values')

    pts = [
        Point(
            index,
            row['is_ref'] == 'R',
            row['x_src'],
            row['y_src'],
            row['x_dst'],
            row['y_dst']
        )
        for index, row in df.iterrows()
    ]
    return pts

def execute(request):
    if request.method == 'POST':
        form_data = ReferencePointsForm(request.POST, request.FILES)
        if form_data.is_valid():

            f = io.TextIOWrapper(
                form_data.cleaned_data['reference_points'], encoding='utf-8')
            pts = _read_points(f)

            source_coords = np.array([(pt.x_src, pt.y_src) for pt in
                filter(lambda pt: pt.is_ref, pts)])
            target_coords = np.array([(pt.x_dst, pt.y_dst) for pt in
                filter(lambda pt: pt.is_ref, pts)])
            val_source_coords = np.array([(pt.x_src, pt.y_src) for pt in
                filter(lambda pt: not pt.is_ref, pts)])
            val_target_coords = np.array([(pt.x_dst, pt.y_dst) for pt in
                filter(lambda pt: not pt.is_ref, pts)])

            transf_type = TransformationType(
                int(form_data.cleaned_data['transformation_type']))
            if transf_type == TransformationType.Similarity:
                tr = SimilarityTransformation2D(source_coords, target_coords)
            elif transf_type == TransformationType.Affine:
                tr = AffineTransformation2D(source_coords, target_coords)
            else:
                tr = PolynomialTransformation2D(source_coords, target_coords)

            tr_stats = ResidualStatistics(source_coords, target_coords, tr)

            rescor_type = ResidualCorrectionType(
                int(form_data.cleaned_data['residual_correction_type']))
            has_residual_correction = rescor_type != ResidualCorrectionType.NoCorrection

            if rescor_type == ResidualCorrectionType.Collocation:
                cov_function_type = CovarianceFunctionType(
                    int(form_data.cleaned_data['cov_function_type']))
                collocation_noise_mm = float(form_data.cleaned_data['collocation_noise']);
                rescor = Collocation(
                    source_coords, target_coords, tr, cov_function_type, collocation_noise_mm)
            elif rescor_type == ResidualCorrectionType.Hausbrandt:
                rescor = HausbrandtCorrection(source_coords, target_coords, tr)

            has_validation = val_source_coords.size > 0 and val_target_coords.size > 0
            if has_validation:
                val_stats = ResidualStatistics(
                    val_source_coords, val_target_coords, tr)
                if has_residual_correction:
                    val_stats_rescor = ResidualStatistics(
                        val_source_coords, val_target_coords, rescor)

            result = {
                "version": '1.0',
                "input_coords": {
                    "units": "meters",
                    "cs_source": {
                        "reference_coords": source_coords.tolist(),
                        "validation_coords": val_source_coords.tolist(),
                    },
                    "cs_target": {
                        "reference_coords": target_coords.tolist(),
                        "validation_coords": val_target_coords.tolist(),
                    },
                },
                "transformation": {
                    "type": transf_type.value,
                    "fitted_parameters": tr.get_parameters().tolist(),
                    "reference_statistics": tr_stats.__dict__
                },
                "residual_correction": {
                    "type": rescor_type.value,
                }
            }

            if has_residual_correction and rescor_type == ResidualCorrectionType.Collocation:
                collocation = rescor
                result["residual_correction"]["collocation"] = {
                    "covariance": {
                        "function_type": collocation.cov_func.type.value,  # CovarianceFunctionType
                        "distance_intervals": collocation.cov_func.distance_intervals.tolist(),
                        "empirical": collocation.cov_func.empirical_cov.tolist(),
                        "fitted": collocation.cov_func.fitted_cov.tolist(),
                    },
                    "noise": collocation_noise_mm,
                }

            if has_validation:
                result["transformation"]["validation_statistics"] = val_stats.__dict__
                if has_residual_correction:
                    result["residual_correction"]["validation_statistics"] = val_stats_rescor.__dict__

            return json_response(result)

    return index(request)
