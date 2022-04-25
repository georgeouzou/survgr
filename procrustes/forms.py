from django import forms

class ReferencePointsForm(forms.Form):
	points = forms.FileField(
		label='Reference Points'
	)
