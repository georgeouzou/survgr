import struct, math
import numpy as np

class GridInfo(object):
	# rows, columns, resolution, first_cell_coords
	header_struct = struct.Struct('I I d d d')

	def __init__(self, file):
		header = file.read(GridInfo.header_struct.size)
		data = GridInfo.header_struct.unpack(header)

		self.rows = data[0] # number of rows
		self.cols = data[1] # number of columns
		self.res = data[2] # resolution
		self.min_x = data[3] # minimum x value
		self.min_y = data[4] # minimum y value

class GridFile(object):

	def __init__(self, name):
		# read the header
		with open(name,'rb') as f:
			self.info = GridInfo(f)

		assert self.info.header_struct.size == 32 # bytes

		# memory map the grid for faster lazy access
		shape = (self.info.rows, self.info.cols)
		dtype = [('de', np.float32), ('dn', np.float32)]
		self._map = np.memmap(name, dtype=dtype, mode='r',
			offset=self.info.header_struct.size, shape=shape)

	# returns corrections de, dn in centimeters
	def interpolate(self, x, y):
		# raises IndexError if out of bounds
		x = np.asarray(x)
		y = np.asarray(y)

		pixel_x = (x-self.info.min_x) / self.info.res
		pixel_y = (y-self.info.min_y) / self.info.res

		pixel_x0 = np.floor(pixel_x).astype(int)
		pixel_y0 = np.floor(pixel_y).astype(int)
		pixel_x1 = pixel_x0 + 1
		pixel_y1 = pixel_y0 + 1

		values_ll = self._map[pixel_y0, pixel_x0]
		values_ul = self._map[pixel_y1, pixel_x0]
		values_lr = self._map[pixel_y0, pixel_x1]
		values_ur = self._map[pixel_y1, pixel_x1]

		weight_ll = (pixel_x1-pixel_x) * (pixel_y1-pixel_y)
		weight_ul = (pixel_x1-pixel_x) * (pixel_y-pixel_y0)
		weight_lr = (pixel_x-pixel_x0) * (pixel_y1-pixel_y)
		weight_ur = (pixel_x-pixel_x0) * (pixel_y-pixel_y0)

		dx = weight_ll*values_ll['de'] + weight_ul*values_ul['de'] + weight_lr*values_lr['de'] + weight_ur*values_ur['de']
		dy = weight_ll*values_ll['dn'] + weight_ul*values_ul['dn'] + weight_lr*values_lr['dn'] + weight_ur*values_ur['dn']

		return (dx, dy)

