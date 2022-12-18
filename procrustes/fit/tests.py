from django.test import TestCase
from pyproj.transformer import Transformer
from . import SimilarityTransformation2D, PolynomialTransformation2D, AffineTransformation2D
from . import HausbrandtCorrection
import numpy as np
import math

class Transformation2DTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		hatt = np.array([
			[-2053.94, -1260.15],
			[-1967.90, -1392.66],
			[-2160.13, -1378.92],
			[-1628.33, -1596.61],
			[-2113.55, -1546.32],
			[-1753.39, -1610.69],
			[-2072.28, -1280.96],
			[-1678.26, -1769.90],
			[-1896.61, -1794.73],
			[-1836.68, -1550.86],
			[-1453.61, -1688.15],
			[-1923.54, -1574.84],
		])

		tm3 = np.array([
			[159888.702, 736744.476],
			[159973.964, 736611.664],
			[159781.925, 736626.378],
			[160312.523, 736406.113],
			[159827.647, 736458.800],
			[160187.401, 736392.744],
			[159870.290, 736723.760],
			[160261.670, 736233.160],
			[160043.120, 736209.400],
			[160104.330, 736452.960],
			[160486.760, 736313.740],
			[160017.500, 736429.370],
		])

		pipe = Transformer.from_pipeline('''
			+proj=pipeline
			+step +inv +proj=aeqd +lat_0=40.65 +lon_0=-0.45 +x_0=0  +y_0=0 +ellps=bessel +pm=athens +units=m
			+step +proj=tmerc +lat_0=34 +lon_0=0 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +units=m
		''')

		tm3_approx = pipe.transform(hatt[:, 0], hatt[:, 1])
		tm3_approx = np.array(tm3_approx).transpose()

		cls.hatt = hatt
		cls.tm3_approx = tm3_approx
		cls.tm3 = tm3

	def is_near(self, a, b, how_near):
		self.assertLessEqual(abs(a-b), how_near)

class SimilarityTransformation2DTest(Transformation2DTest):

	def test_fit_tm3_approx_tm3(self):
		t = SimilarityTransformation2D(self.tm3_approx, self.tm3)
		Tx, Ty, c, d = t.get_parameters()

		rotation = math.atan(d/c)
		scale = math.sqrt(c*c+d*d)
		rotation = math.degrees(rotation)*3600.0 #convert to sec
		scale = (1.0-scale)*1000000 #convert to ppm,

		self.is_near(Tx, 162.5810, 0.001)
		self.is_near(Ty, 187.9988, 0.001)
		self.is_near(rotation,-32.62638, 0.0001)
		self.is_near(scale, 282.301, 0.001)

	def test_fit_hatt_tm3(self):
		t = SimilarityTransformation2D(self.hatt, self.tm3)
		transformed = t(self.hatt)
		self.assertTrue(np.all(np.less(self.tm3-transformed, np.ones(transformed.shape))))

	def test_rank_deficiency(self):
		t = SimilarityTransformation2D(self.hatt[0:1, :], self.tm3[0:1, :]) # 2 xy, 4 params
		self.assertTrue(t.rank_deficiency == True)
		t = SimilarityTransformation2D(self.hatt[0:2, :], self.tm3[0:2, :]) # 4 xy, 4 params
		self.assertTrue(t.rank_deficiency == False)

	def test_errors(self):
		with self.assertRaises(AssertionError):
			t = SimilarityTransformation2D(self.hatt[0:4,:], self.tm3[0:5,:])

class PolynomialTransformation2DTest(Transformation2DTest):

	def test_fit_tm3_approx_tm3(self):
		t = PolynomialTransformation2D(self.tm3_approx, self.tm3)
		transformed = t(self.tm3_approx)
		self.assertTrue(np.all(np.less(self.tm3-transformed, 0.1*np.ones(transformed.shape))))

	def test_fit_hatt_tm3(self):
		t = PolynomialTransformation2D(self.hatt, self.tm3)
		transformed = t(self.hatt)
		self.assertTrue(np.all(np.less(self.tm3-transformed, 0.1*np.ones(transformed.shape))))

	def test_rank_deficiency(self):
		t = PolynomialTransformation2D(self.hatt[0:5, :], self.tm3[0:5, :]) # 10 xy, 12 params
		self.assertTrue(t.rank_deficiency == True)
		t = PolynomialTransformation2D(self.hatt[0:6, :], self.tm3[0:6, :]) # 12 xy, 12 params
		self.assertTrue(t.rank_deficiency == False)

	def test_errors(self):
		with self.assertRaises(AssertionError):
			t = PolynomialTransformation2D(self.hatt[0:4,:], self.tm3[0:5,:])

class AffineTransformation2DTest(Transformation2DTest):

	def test_fit_tm3_approx_tm3(self):
		t = AffineTransformation2D(self.tm3_approx, self.tm3)
		Tx, Ty, a1, a2, b1, b2 = t.get_parameters()

		rot_x = -math.atan(b1/a1)
		rot_y = math.atan(a2/b2)
		scale_x = math.sqrt(a1*a1+b1*b1)
		scale_y = math.sqrt(a2*a2+b2*b2)

		rot_x = math.degrees(rot_x)*3600.0 #convert to sec
		rot_y = math.degrees(rot_y)*3600.0 #convert to sec
		scale_x = (1.0-scale_x)*1000000 #convert to ppm,
		scale_y = (1.0-scale_y)*1000000 #convert to ppm,

		self.is_near(Tx, -162.072, 0.001)
		self.is_near(Ty, 329.616, 0.001)
		self.is_near(rot_x, -26.88051, 0.0001)
		self.is_near(rot_y, 44.13099, 0.0001)
		self.is_near(scale_x, -34.448, 0.001)
		self.is_near(scale_y, 468.542, 0.001)

		transformed = t(self.tm3_approx)
		self.assertTrue(np.all(np.less(self.tm3-transformed, 0.1*np.ones(transformed.shape))))

	def test_fit_hatt_tm3(self):
		t = AffineTransformation2D(self.hatt, self.tm3)
		transformed = t(self.hatt)
		self.assertTrue(np.all(np.less(self.tm3-transformed, 0.1*np.ones(transformed.shape))))

	def test_rank_deficiency(self):
		t = AffineTransformation2D(self.hatt[0:2, :], self.tm3[0:2, :]) # 4 xy, 6 params
		self.assertTrue(t.rank_deficiency == True)
		t = AffineTransformation2D(self.hatt[0:3, :], self.tm3[0:3, :]) # 6 xy, 6 params
		self.assertTrue(t.rank_deficiency == False)

	def test_errors(self):
		with self.assertRaises(AssertionError):
			t = AffineTransformation2D(self.hatt[0:4,:], self.tm3[0:5,:])


class HausbrandtCorrectionTest(TestCase):

	def test_correction(self):
		source_coords = np.array([
			[14482.564, 13288.071],
			[8445.162, 20281.612],
			[6187.062, 12491.598],
		])
		target_coords = np.array([
			[5768950.542, 6441593.071],
			[5763055.723, 6448708.668],
			[5760639.634, 6440965.177],
		])
		new_source_coords = np.array([
			[10550.348, 13150.453],
			[8000.671, 16023.344],
			[10591.893, 16627.614],
		])
		new_target_coords = np.array([
			[5765015.893, 6441535.346],
			[5762524.797, 6444459.784],
			[5765128.055, 6445011.369],
		])

		tr = SimilarityTransformation2D(source_coords, target_coords)
		hc = HausbrandtCorrection(source_coords, target_coords, tr)

		self.assertFalse(np.all(
			np.equal(
				np.round(tr(source_coords), 3),
				target_coords
			)
		))

		self.assertTrue(np.all(
			np.equal(
				np.round(hc(source_coords), 3),
				target_coords
			)
		))

		self.assertTrue(np.all(
			np.equal(
				np.round(hc(new_source_coords), 3),
				new_target_coords
			)
		))




