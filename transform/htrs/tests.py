import os
import numpy as np
from django.test import TestCase
from .grid import GridFile

class HTRSGridFileTest(TestCase):

	def setup(self):
		grid_path = os.path.join(os.path.dirname(__file__), "htrs07.grb")
		self.grid = GridFile(grid_path)

	def test_out_of_bounds(self):
		self.setup()
		with self.assertRaises(IndexError):
			self.grid.interpolate(0, 0)

		with self.assertRaises(IndexError):
			self.grid.interpolate(10000000, 10000000)

		with self.assertRaises(IndexError):
			_ = self.grid.interpolate(41600.0-1*2000, 1845619.0-1*2000)

		with self.assertRaises(IndexError):
			_ = self.grid.interpolate(41600.0+421*2000, 1845619.0+407*2000)
		
		with self.assertRaises(IndexError):
			_ = self.grid.interpolate(41600.0-1*2000, 1845619.0+407*2000)

		with self.assertRaises(IndexError):
			_ = self.grid.interpolate(41600.0+421*2000, 1845619.0-1*2000)



	def test_constant_values(self):
		self.setup()
		de, dn = self.grid.interpolate(41600.0, 1845619.0)
		self.assertEqual(round(de, 2), -33.20)
		self.assertEqual(round(dn, 2), -38.75)

		de, dn = self.grid.interpolate(41600.0+2000, 1845619.0)
		self.assertEqual(round(de, 2), -33.14)
		self.assertEqual(round(dn, 2), -37.71)

		de, dn = self.grid.interpolate(41600.0, 1845619.0+2000)
		self.assertEqual(round(de, 2), -32.93)
		self.assertEqual(round(dn, 2), -39.10)

		de, dn = self.grid.interpolate(41600.0+2000, 1845619.0+2000)
		self.assertEqual(round(de, 2), -32.87)
		self.assertEqual(round(dn, 2), -38.06)

		de, dn = self.grid.interpolate(41600.0+420*2000, 1845619.0+406*2000)
		self.assertEqual(round(de, 2), 142.10)
		self.assertEqual(round(dn, 2), -108.27)


	def test_check_htrs_grid(self):
		self.setup()
		# values taken form HEPOS MANUAL for htrs transformation
		# x, y in htrs07-tm07
		x1, y1 = (566446.108, 2529618.096)
		de, dn = self.grid.interpolate(x1, y1)
		self.assertEqual(round(de/100, 3), -0.122)
		self.assertEqual(round(dn/100, 3), -0.184)

		x1, y1 = (566445.986, 2529617.912)
		de, dn = self.grid.interpolate(x1, y1)
		self.assertEqual(round(de/100, 3), -0.122)
		self.assertEqual(round(dn/100, 3), -0.184)

		x1 = [566446.108, 566445.986]
		y1 = [2529618.096, 2529617.912]
		de, dn = self.grid.interpolate(x1, y1)

		self.assertEqual(de.dtype, np.float64)
		self.assertEqual(dn.dtype, np.float64)
		self.assertEqual(round(de[0]/100, 3), -0.122)
		self.assertEqual(round(dn[0]/100, 3), -0.184)
		self.assertEqual(round(de[1]/100, 3), -0.122)
		self.assertEqual(round(dn[1]/100, 3), -0.184)

