import os
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
        dx, dy = grid.interpolate(x1, y1)
        self.assertEqual(round(dx/100, 3), -0.122)
        self.assertEqual(round(dy/100, 3), -0.184)

        x1, y1 = (566445.986, 2529617.912)
        dx, dy = grid.interpolate(x1, y1)
        self.assertEqual(round(dx/100, 3), -0.122)
        self.assertEqual(round(dy/100, 3), -0.184)
