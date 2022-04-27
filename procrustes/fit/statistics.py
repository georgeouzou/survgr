import numpy as np

class ResidualStatistics():
	def __init__(self, source_coords, target_coords, transformation):
		assert(source_coords.shape[0] == target_coords.shape[0])
		assert(source_coords.shape[1] == 2)
		assert(target_coords.shape[1] == 2)

		residuals = target_coords - transformation(source_coords)

		self.min = np.min(residuals)
		self.max = np.max(residuals)
		self.mean = np.mean(residuals)
		self.std = np.std(residuals)
