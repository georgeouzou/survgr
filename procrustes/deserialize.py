import numpy as np
from . import fit

def from_session_data(session_data):
    source_coords = np.array(session_data["input_coords"]["cs_source"]["reference_coords"])
    target_coords = np.array(session_data["input_coords"]["cs_target"]["reference_coords"])
    transformation_type = fit.TransformationType(session_data["transformation"]["type"])
    rescor_type = fit.ResidualCorrectionType(session_data["residual_correction"]["type"])

    tr = None
    if transformation_type == fit.TransformationType.Similarity:
        tr = fit.SimilarityTransformation2D(source_coords, target_coords)
    elif transformation_type == fit.TransformationType.Affine:
        tr = fit.AffineTransformation2D(source_coords, target_coords)
    elif transformation_type == fit.TransformationType.Polynomial:
        tr = fit.PolynomialTransformation2D(source_coords, target_coords)

    if rescor_type == fit.ResidualCorrectionType.Hausbrandt:
        tr = fit.HausbrandtCorrection(source_coords, target_coords, tr)
    elif rescor_type == fit.ResidualCorrectionType.Collocation:
        cov_func_type = session_data["residual_correction"]["collocation"]["covariance"]["function_type"]
        collocation_noise = session_data["residual_correction"]["collocation"]["noise"]
        tr = fit.Collocation(source_coords, target_coords, tr, cov_func_type, collocation_noise)

    return tr
