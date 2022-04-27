import math
import numpy as np

class AffineTransformation2D:
	def __init__(self, source_coords, target_coords):
		assert(source_coords.shape[1] == 2) # x,y
		assert(target_coords.shape[1] == 2) # x,y
		assert(target_coords.shape[0] == source_coords.shape[0])

		self.source_coords = source_coords
		self.target_coords = target_coords
		self.num_coords = source_coords.shape[0]
		self.fitted_params, self.rank_deficiency = self._fit()

	def get_parameters(self):
		return self.fitted_params

	def _compute_A_matrix(self, coords):
		num_xy = coords.shape[0]

		Ai0 = np.concatenate([
				np.ones((num_xy,1)),
				np.zeros((num_xy,1)),
				coords[:, 0].reshape(num_xy,1),
				coords[:, 1].reshape(num_xy,1),
				np.zeros((num_xy,2)),
			],
			axis=1)

		Ai1 = np.concatenate([
				np.zeros((num_xy,1)),
				np.ones((num_xy,1)),
				np.zeros((num_xy,2)),
				coords[:, 0].reshape(num_xy,1),
				coords[:, 1].reshape(num_xy,1),
			],
			axis=1)

		A = np.concatenate([Ai0, Ai1], axis=0)
		return A

	def _fit(self):
		source_centroid = np.mean(self.source_coords, axis=0)
		centered_source_coords = self.source_coords - source_centroid

		num_coords = self.num_coords
		L = np.concatenate([self.target_coords[:, 0], self.target_coords[:, 1]]).reshape(num_coords*2, 1)
		A = self._compute_A_matrix(centered_source_coords)

		fitted_params, _, rank, _ = np.linalg.lstsq(A, L, rcond=None)
		fitted_params = fitted_params.flatten()

		Tx, Ty, a1, a2, b1, b2 = fitted_params
		Tx = Tx - a1*source_centroid[0] - a2*source_centroid[1]
		Ty = Ty - b1*source_centroid[0] - b2*source_centroid[1]
		return (np.array([Tx, Ty, a1, a2, b1, b2]), rank < 6)

	def __call__(self, coords):
		assert(coords.shape[1] == 2) # x,y
		num_coords = coords.shape[0]
		A = self._compute_A_matrix(coords)
		x = A @ self.fitted_params.reshape(6, 1)
		return np.concatenate([x[0:num_coords], x[num_coords:2*num_coords]], axis=1)
