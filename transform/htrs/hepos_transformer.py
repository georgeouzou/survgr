import os
import pyproj
from .grid import GridFile

class HeposTransformer(object):
	'''
	Func object for HTRS07 Datum.
	Transforms in place from HTRS / TM07 to GGRS87 / GG (inverse=False)
	or from GGRS87 / GG to HTRS / TM07 (inverse=True)
	'''
	grid_path = os.path.join(os.path.dirname(__file__), "htrs07.grb")

	def __init__(self, inverse):
		# grid containing the shifts de, dn in cm
		self._grid = GridFile(self.grid_path)
		self._inverse = inverse
		# extended better ggrs - htrs 7 param. transformation provided by Hepos service
		self._htrs_to_ggrs_approx = pyproj.Transformer.from_pipeline(
			'''
			+proj=pipeline
			+step +inv +proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=-2000000 +ellps=GRS80 +units=m
			+step +proj=cart
			+step +proj=helmert +convention=coordinate_frame
				+x=203.437 +y=-73.461 +z=-243.594
				+rx=-0.170 +ry=-0.060 +rz=-0.151 +s=-0.294
			+step +inv +proj=cart
			+step +proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +units=m
			''')

	def __call__(self, x, y, z=None):
		grid = self._grid
		if self._inverse: #ggrs -> htrs
			# first apply the approximate tranformation
			h_xyz = self._htrs_to_ggrs_approx.transform(x, y, z, direction=pyproj.enums.TransformDirection.INVERSE)
			h_x, h_y = h_xyz[0], h_xyz[1]
			# we need to interpolate with htrs coords
			de, dn = grid.interpolate(h_x, h_y)
			h_x -= de / 100.0
			h_y -= dn / 100.0
			return h_xyz

		else: # htrs -> ggrs
			# first apply the approximate transformation
			g_xyz = self._htrs_to_ggrs_approx.transform(x, y, z, direction=pyproj.enums.TransformDirection.FORWARD)
			# then apply shift correction
			g_x, g_y = g_xyz[0], g_xyz[1]
			#again we need to interpolate with htrs coords
			de, dn = grid.interpolate(x, y)
			g_x += de / 100.0
			g_y += dn / 100.0
			return g_xyz
