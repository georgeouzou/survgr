from django import forms
from .fit import TransformationType, ResidualCorrectionType, CovarianceFunctionType

class ReferencePointsForm(forms.Form):
	reference_points = forms.FileField(
		label='Σημεία Αναφοράς',
		widget=forms.FileInput(
			attrs={'class': 'form-control'},
		)
	)
	validation_points = forms.FileField(
		label='Σημεία Επιβεβαίωσης',
		required=False,
		widget=forms.FileInput(
			attrs={'class': 'form-control'},
		)
	)
	points_format = forms.ChoiceField(
		label='Μορφή',
		choices=[
			('id,xs,ys,xt,yt', "id, x, y, x', y'"),
			('xs,ys,xt,yt',    "x, y, x', y'"),
		],
		widget=forms.Select(
			attrs={'class': 'form-select'},
		)
	)
	transformation_type = forms.ChoiceField(
		choices=[
			(TransformationType.Similarity.value, 'Ομοιότητας'),
			(TransformationType.Affine.value, 'Αφινικός'),
			(TransformationType.Polynomial.value, 'Πολυωνυμικός'),
		],
		initial = TransformationType.Similarity.value,
		label = 'Μετασχηματισμός',
		widget=forms.RadioSelect(
			attrs={'class': 'form-check-input', 'autocomplete': 'off'},
		)
	)
	residual_correction_type = forms.ChoiceField(
		choices=[
			(ResidualCorrectionType.NoCorrection.value, 'Χωρίς Μοντελοποίηση'),
			(ResidualCorrectionType.Collocation.value, 'Σημειακή Προσαρμογή'),
			(ResidualCorrectionType.Hausbrandt.value, 'Διόρθωση Hausbrandt'),
		],
		initial = ResidualCorrectionType.NoCorrection.value,
		label = 'Μοντελοποίηση Yπολοίπων',
		widget=forms.RadioSelect(
			attrs={'class': 'form-check-input', 'autocomplete': 'off'},
		)
	)
	cov_function_type = forms.ChoiceField(
		choices=[
			(CovarianceFunctionType.Sinc.value, CovarianceFunctionType.Sinc.name),
			(CovarianceFunctionType.Gaussian.value, CovarianceFunctionType.Gaussian.name),
			(CovarianceFunctionType.Exponential.value, CovarianceFunctionType.Exponential.name),
			(CovarianceFunctionType.Spline.value, CovarianceFunctionType.Spline.name),
		],
		initial = CovarianceFunctionType.Sinc.value,
		label = 'Συνάρτηση Συμμεταβλητότητας',
		widget=forms.RadioSelect(
			attrs={'class': 'form-check-input', 'autocomplete': 'off'},
		)
	)
