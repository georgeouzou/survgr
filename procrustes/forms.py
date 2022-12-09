from django import forms
from .fit import TransformationType, ResidualCorrectionType, CovarianceFunctionType

class ReferencePointsForm(forms.Form):
	reference_points = forms.FileField(
		label='Σημεία αναφοράς',
        widget=forms.FileInput(
            attrs={'class': 'hidden'}
		),
		required=True,
	)
	transformation_type = forms.ChoiceField(
		choices=[
			(TransformationType.Similarity.value, 'Ομοιότητας'),
			(TransformationType.Affine.value, 'Αφινικός'),
			(TransformationType.Polynomial.value, 'Πολυωνυμικός'),
		],
		initial = TransformationType.Similarity.value,
		label = 'Μετασχηματισμός',
		widget=forms.Select(
			attrs={'class': 'form-control', 'autocomplete': 'off'},
		),
		required=True,
	)
	residual_correction_type = forms.ChoiceField(
		choices=[
			(ResidualCorrectionType.NoCorrection.value, 'Χωρίς μοντελοποίηση'),
			(ResidualCorrectionType.Collocation.value, 'Σημειακή προσαρμογή'),
			(ResidualCorrectionType.Hausbrandt.value, 'Διόρθωση Hausbrandt'),
		],
		initial = ResidualCorrectionType.NoCorrection.value,
		label = 'Μοντελοποίηση υπολοίπων',
		widget=forms.Select(
			attrs={'class': 'form-control', 'autocomplete': 'off'},
		),
		required=True,
	)
	cov_function_type = forms.ChoiceField(
		choices=[
			(CovarianceFunctionType.Sinc.value, CovarianceFunctionType.Sinc.name),
			(CovarianceFunctionType.Gaussian.value, CovarianceFunctionType.Gaussian.name),
			(CovarianceFunctionType.Exponential.value, CovarianceFunctionType.Exponential.name),
			#(CovarianceFunctionType.Spline.value, CovarianceFunctionType.Spline.name),
		],
		initial = CovarianceFunctionType.Sinc.value,
		label = 'Συνάρτηση συμμεταβλητότητας',
		widget=forms.Select(
			attrs={'class': 'form-control', 'autocomplete': 'off'},
		),
		required=False,
	)
	collocation_noise = forms.IntegerField(
        max_value=1000, #mm
        min_value=0,
		label='Προαιρετικός θόρυβος υπολοίπων σε mm',
		initial=0,
		widget=forms.NumberInput(
			attrs={'class': 'form-control', 'autocomplete': 'off'},
		),
		required=False
    )
