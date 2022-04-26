from django import forms
import enum

@enum.unique
class TransformationType(enum.Enum):
	Similarity = 0
	Affine = 1
	Polynomial = 2


class ReferencePointsForm(forms.Form):
	points = forms.FileField(
		label='Reference Points',
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
		label = 'Transformation Type',
		widget=forms.Select(
			attrs={'class': 'form-control'},
		)
	)
