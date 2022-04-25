import numpy as np

class PolynomialTransformation2D:

	def __init__(self, source_coords, target_coords):
		assert(source_coords.shape[1] == 2) # x,y
		assert(target_coords.shape[1] == 2) # x,y
		assert(target_coords.shape[0] == source_coords.shape[0])

		self.source_coords = source_coords
		self.source_centroid = np.mean(source_coords, axis=0)
		self.target_coords = target_coords
		self.num_coords = source_coords.shape[0]
		self.fitted_params = self._fit()

	def get_parameters(self):
		return self.fitted_params

	def _compute_A_matrix(self, coords):
		num_xy = self.num_coords
		x = coords[:, 0].reshape(num_xy, 1)
		y = coords[:, 1].reshape(num_xy, 1)

		Ai0 = np.concatenate([
				np.ones((num_xy, 1)), # a0
				x, # a1*x
				y, # a2*y
				x*x, # a3 x^2
				y*y, # a4 y^2
				x*y, # a5*x*y
				np.zeros((num_xy, 6)),
			],
			axis=1)

		Ai1 = np.concatenate([
				np.zeros((num_xy, 6)),
				np.ones((num_xy, 1)), # b
				x, # b1*x
				y, # b2*y
				x*x, # b3 x^2
				y*y, # b4 y^2
				x*y, # b5*x*y
			],
			axis=1)

		A = np.concatenate([Ai0, Ai1], axis=0)
		return A

	def _fit(self):
		num_coords = self.num_coords
		centered_source_coords = self.source_coords-self.source_centroid

		L = np.concatenate([self.target_coords[:, 0], self.target_coords[:, 1]]).reshape(num_coords*2, 1)
		A = self._compute_A_matrix(centered_source_coords)

		fitted_params = np.linalg.inv(A.transpose() @ A) @ (A.transpose() @ L)
		fitted_params = fitted_params.flatten()
		return fitted_params

	def __call__(self, coords):
		assert(coords.shape[1] == 2) # x,y
		num_coords = coords.shape[0]

		centered_coords = coords-self.source_centroid
		A = self._compute_A_matrix(centered_coords)
		x = A @ self.fitted_params.reshape(12, 1)
		return np.concatenate([x[0:num_coords], x[num_coords:2*num_coords]], axis=1)
