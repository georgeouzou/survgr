import os
import numpy as np
from django.test import TestCase
from .grid import GridFile

class HTRSGridFileTest(TestCase):
    
	def test_check_htrs_grid(self):
		grid_path = os.path.join(os.path.dirname(__file__), "htrs07.grb")
		grid = GridFile(grid_path)

        # check bounds
		with self.assertRaises(IndexError):
			grid.interpolate(0, 0)

		with self.assertRaises(IndexError):
			grid.interpolate(10000000, 10000000)

		# values taken form HEPOS MANUAL for htrs transformation
		# x, y in htrs07-tm07
		x1, y1 = (566446.108, 2529618.096)
		de, dn = grid.interpolate(x1, y1)
		self.assertEqual(round(de/100, 3), -0.122)
		self.assertEqual(round(dn/100, 3), -0.184)

		x1, y1 = (566445.986, 2529617.912)
		de, dn = grid.interpolate(x1, y1)
		self.assertEqual(round(de/100, 3), -0.122)
		self.assertEqual(round(dn/100, 3), -0.184)

		x1 = [566446.108, 566445.986]
		y1 = [2529618.096, 2529617.912]
		de, dn = grid.interpolate(x1, y1)

		self.assertEqual(de.dtype, np.float64)
		self.assertEqual(dn.dtype, np.float64)
		self.assertEqual(round(de[0]/100, 3), -0.122)
		self.assertEqual(round(dn[0]/100, 3), -0.184)
		self.assertEqual(round(de[1]/100, 3), -0.122)
		self.assertEqual(round(dn[1]/100, 3), -0.184)
