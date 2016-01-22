# -*- coding: utf-8 -*-
from django.test import TestCase

from .models import Hattblock, OKXECoefficient
import hatt2ggrs

class OKXETransformTest(TestCase):

	def setup(self):
		self.coeffs = [370552.68, 0.9997155, 0.0175123, -1.08e-09, 1.63e-09, 2.04e-09,\
		4511927.23, -0.0174755, 0.9996979, -6.50e-10, 5.60e-10, -1.65e-09]

	def test_forward_func(self):
		self.setup()
		x1, y1 = (-16997.09, -14277.15)
		x2, y2 = hatt2ggrs.fwd(self.coeffs, x1, y1)

		self.assertEqual(round(x2,2), 353310.92)
		self.assertEqual(round(y2,2), 4497950.95)

	def test_inverse_func(self):
		self.setup()
		x1, y1 = (353310.92, 4497950.95)
		x2, y2 = hatt2ggrs.inv(self.coeffs, x1, y1)

		self.assertEqual(round(x2,2),-16997.09)
		self.assertEqual(round(y2,2),-14277.15)
	

class HattBlockTest(TestCase):

	def test_coefficients(self):
		hb = Hattblock.objects.get(name='Άθως')
		coeffs = [497146.35, 0.9996218, 0.0004028, -1.70E-010, 2.60E-010, 2.70E-010,\
		 4455299.91, -0.0003894, 0.99961, 1.60E-010, 1.30E-010, -2.70E-010]

		for i,j in zip(coeffs, hb.get_coeffs()):
			self.assertEqual(i, j)

		hb = Hattblock.objects.get(name='Ερυθραί')
		coeffs = [453315.02, 0.9996023, 0.0057615, -2.01E-009, 2.70E-010, -6.00E-011,\
		 4233504.49, -0.005829, 0.9996627, -1.10E-009, 5.10E-010, -2.36E-009]

		for i,j in zip(coeffs, hb.get_coeffs()):
			self.assertEqual(i, j)

		hb = Hattblock.objects.get(name='Ψαχνά')
		coeffs = [453637.6, 0.9996193, 0.0058377, -6.50E-010, 5.90E-010, -1.00E-011,\
		 4288980.93, -0.0058421, 0.9996147, 2.40E-010, -5.10E-010, -1.53E-009]

		for i,j in zip(coeffs, hb.get_coeffs()):
			self.assertEqual(i, j)


