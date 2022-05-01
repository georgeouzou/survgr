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
	transformation_type = forms.ChoiceField(
		choices=[
			(TransformationType.Similarity.value, 'Ομοιότητας'),
			(TransformationType.Affine.value, 'Αφινικός'),
			(TransformationType.Polynomial.value, 'Πολυωνυμικός'),
		],
		initial = TransformationType.Similarity.value,
		label = 'Μετασχηματισμός',
		widget=forms.RadioSelect(
			attrs={'class': 'btn-check', 'autocomplete': 'off'},
		)
	)
	residual_correction_type = forms.ChoiceField(
		choices=[
			(ResidualCorrectionType.NoCorrection.value, 'Χωρίς Μοντελοποίηση'),
			(ResidualCorrectionType.Collocation.value, 'Σημειακή Προσαρμογή'),
			(ResidualCorrectionType.Hausbrandt.value, 'Διόρθωση Hausbrandt'),
		],
		initial = ResidualCorrectionType.NoCorrection.value,
		label = 'Μοντελοποίηση Yπολοίπων Μετασχηματισμού',
		widget=forms.RadioSelect(
			attrs={'class': 'btn-check', 'autocomplete': 'off'},
		)
	)
	cov_function_type = forms.ChoiceField(
		choices=[
			(CovarianceFunctionType.CardinalSine.value, 'Sinc'),
			(CovarianceFunctionType.Gaussian.value, 'Gauss'),
			(CovarianceFunctionType.Exponential.value, 'Exp'),
			(CovarianceFunctionType.Spline.value, 'Spline'),
		],
		initial = CovarianceFunctionType.CardinalSine.value,
		label = 'Covariance Function Type',
		widget=forms.RadioSelect(
			attrs={'class': 'btn-check', 'autocomplete': 'off'},
		)
	)
