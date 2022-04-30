from django import forms
from .fit import TransformationType, ResidualCorrectionType, CovarianceFunctionType

class ReferencePointsForm(forms.Form):
	reference_points = forms.FileField(
		label='Reference Points',
		widget=forms.FileInput(
			attrs={'class': 'form-control'},
		)
	)
	validation_points = forms.FileField(
		label='Validation Points',
		required=False,
		widget=forms.FileInput(
			attrs={'class': 'form-control'},
		)
	)
	transformation_type = forms.ChoiceField(
		choices=[
			(TransformationType.Similarity.value, TransformationType.Similarity.name),
			(TransformationType.Affine.value, TransformationType.Affine.name),
			(TransformationType.Polynomial.value, TransformationType.Polynomial.name),
		],
		initial = TransformationType.Similarity.value,
		label = 'Transformation Type',
		widget=forms.RadioSelect(
			attrs={'class': 'btn-check'},
		)
	)
	residual_correction_type = forms.ChoiceField(
		choices=[
			(ResidualCorrectionType.NoCorrection.value, 'None'),
			(ResidualCorrectionType.Collocation.value, ResidualCorrectionType.Collocation.name),
			(ResidualCorrectionType.Hausbrandt.value, ResidualCorrectionType.Hausbrandt.name),
		],
		initial = ResidualCorrectionType.NoCorrection.value,
		label = 'Residual Correction Type',
		widget=forms.RadioSelect(
			attrs={'class': 'btn-check'},
		)
	)
	cov_function_type = forms.ChoiceField(
		choices=[
			(CovarianceFunctionType.CardinalSine.value, 'Cardinal Sine'),
			(CovarianceFunctionType.Gaussian.value, CovarianceFunctionType.Gaussian.name),
			(CovarianceFunctionType.Exponential.value, CovarianceFunctionType.Exponential.name),
			(CovarianceFunctionType.Spline.value, CovarianceFunctionType.Spline.name),
		],
		initial = CovarianceFunctionType.CardinalSine.value,
		label = 'Covariance Function Type',
		widget=forms.RadioSelect(
			attrs={'class': 'btn-check'},
		)
	)
