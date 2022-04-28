from django import forms
import enum

@enum.unique
class TransformationType(enum.Enum):
	Similarity = 0
	Affine = 1
	Polynomial = 2

@enum.unique
class ResidualCorrectionType(enum.Enum):
	NoCorrection = 0
	Collocation = 1
	Hausbrandt = 2

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

