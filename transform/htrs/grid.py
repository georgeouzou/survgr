import struct, math

import numpy

class GridInfo(object):
	# rows, columns, resolution, first_cell_coords
	header_struct = struct.Struct('I I d d d')
	
	def __init__(self, file):
		file.seek(0) # go to beginning
		header = file.read(GridInfo.header_struct.size)	
		data = GridInfo.header_struct.unpack(header)
		file.seek(0)
					
		self.rows = data[0] # number of rows
		self.cols = data[1] # number of columns
		self.res = data[2] # resolution
		self.min_x = data[3] # minimum x value
		self.min_y = data[4] # minimum y value
		
class GridFile(object):

	def __init__(self, name, dtype='f,f'):
		with open(name) as f:
			self.info = GridInfo(f)
			self.dtype = dtype
			shape = (self.info.rows, self.info.cols)
			
			#TODO ADD MAPPING INSTEAD OF LOADING THE WHOLE FILE
			#self._map = numpy.memmap(f, dtype='f,f', mode='r',
				#offset=GridInfo.header_struct.size, shape=shape)

			f.seek(self.info.header_struct.size)
			self._map = numpy.fromfile(f, dtype=self.dtype).reshape(shape)


	def interpolate(self, x, y):
		# raises IndexError if out of bounds
		# normalized coordinates (float row column)

		norm_x = (x-self.info.min_x) / self.info.res
		norm_y = (y-self.info.min_y) / self.info.res
		
		# rj	ul-----ur
 		# 	    |  pt  |
		# ri	ll----lr 

		ri = int(math.floor(norm_y))
		rj = int(math.ceil(norm_y))
		ci = int(math.floor(norm_x))
		cj = int(math.ceil(norm_x))
		

		cell = (self._map[ri,ci], self._map[rj,ci], self._map[rj,cj], self._map[ri,cj])
		
		norm_x -= ci # normalized cell coordinates [0-1]
		norm_y -= ri
		
		# bilinear interpolation
		num_values = len(cell[0]) # how many values does the cell contain?
		value = [0] * num_values
		for i in xrange(num_values):
			# horizontal interpolations
			vh = (cell[2][i]-cell[1][i]) * norm_x + cell[1][i]
			vl = (cell[3][i]-cell[0][i]) * norm_x + cell[0][i]
		
			# vertical interpolation
			value[i] =  (vh-vl) * norm_y + vl
		
		return value