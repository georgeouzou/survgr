import numpy as np
from scipy import spatial

# residuals in cm

class HausbrandtCorrection:

	def __init__(self, source_coords, target_coords, initial_transf):
		assert(source_coords.shape[1] == 2)
		assert(target_coords.shape[1] == 2)

		residuals = target_coords-initial_transf(source_coords)
		residuals *= 100.0 # to cm

		self.source_coords = source_coords # maybe we dont need to store these
		self.residuals = residuals
		self.initial_transf = initial_transf

	def __call__(self, coords):
		assert(coords.shape[1] == 2)
		# coords are in meters

		D = spatial.distance.cdist(coords, self.source_coords, metric='sqeuclidean')
		D = np.maximum(D, 10e-6) # minimum distance^2 between points: 1 mm ^ 2
		# weights are computed as 1/d^2, but lets normalize weights (distances) to km^2 for better numerical stability
		weights = 10e6 / D

		sum_w = np.sum(weights, axis=1).reshape(weights.shape[0], 1)
		delta = weights @ self.residuals
		delta /= sum_w # divide both dx and dy by sum_w
		delta /= 100.0 # back to m

		init_coords = self.initial_transf(coords)
		return init_coords+delta
