from django.test import TestCase
from pyproj.transformer import Transformer
from . import SimilarityTransformation2D
import numpy as np
import math

class SimilarityTransformation2DTest(TestCase):

	def test_fit(self):
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

		t = SimilarityTransformation2D(tm3_approx, tm3)
		Tx, Ty, c, d = t.get_parameters()

		rotation = math.atan(d/c)
		scale = math.sqrt(c*c+d*d)
		rotation = math.degrees(rotation)*3600.0 #convert to sec
		scale = (1.0-scale)*1000000 #convert to ppm,

		self.assertEqual(round(Tx, 4), 162.5810)
		self.assertEqual(round(Ty, 4), 187.9988)
		self.assertEqual(round(rotation, 5),-32.62638)
		self.assertEqual(round(scale, 3), 282.301)

	def test_errors(self):
		hatt = np.array([
			[-2053.94, -1260.15],
			[-1967.90, -1392.66],
			[-1923.54, -1574.84],
		])

		tm3 = np.array([
			[159888.702, 736744.476],
			[159973.964, 736611.664],
			[159781.925, 736626.378],
			[160312.523, 736406.113],
		])

		with self.assertRaises(AssertionError):
			t = SimilarityTransformation2D(hatt, tm3)
