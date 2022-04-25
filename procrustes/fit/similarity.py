import math
import enum
import numpy as np

class SimilarityTransformation2D:

	class CoordComponent(enum.Enum):
		X = 0
		Y = 1

	def __init__(self, source_coords, target_coords):
		assert(source_coords.shape[1] == 2) # x,y
		assert(target_coords.shape[1] == 2) # x,y
		assert(target_coords.shape[0] == target_coords.shape[0])

		self.source_coords = source_coords
		self.target_coords = target_coords
		self.num_coords = source_coords.shape[0]
		self.fitted_params = self._fit()

	def get_parameters(self):
		return self.fitted_params

	def _compute_A_matrix(self, coords):
		num_xy = self.num_coords

		Ai0 = np.concatenate([
				np.ones((num_xy,1)),
				np.zeros((num_xy,1)),
				coords[:, 0].reshape(num_xy,1),
				coords[:, 1].reshape(num_xy,1),
			],
			axis=1)

		Ai1 = np.concatenate([
				np.zeros((num_xy,1)),
				np.ones((num_xy,1)),
				coords[:, 1].reshape(num_xy,1),
				-1.0*coords[:, 0].reshape(num_xy,1),
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

		fitted_params = np.linalg.inv(A.transpose() @ A) @ (A.transpose() @ L)
		fitted_params = fitted_params.flatten()
		Tx = fitted_params[0]
		Ty = fitted_params[1]
		c = fitted_params[2]
		d = fitted_params[3]
		Tx = Tx - c*source_centroid[0] - d*source_centroid[1]
		Ty = Ty + d*source_centroid[0] - c*source_centroid[1]
		return np.array([Tx, Ty, c, d])

	def __call__(self, coords):
		assert(coords.shape[1] == 2) # x,y
		num_coords = coords.shape[0]
		A = self._compute_A_matrix(coords)
		x = A @ self.fitted_params.reshape(4, 1)
		return np.concatenate([x[0:num_coords], x[num_coords:2*num_coords]], axis=1)
