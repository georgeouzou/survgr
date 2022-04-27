import math
import itertools
from dataclasses import dataclass
import numpy as np
from scipy import optimize

@dataclass
class PairwiseDistance:
	p0_idx: int
	p1_idx: int
	dist:   float

def _compute_paiwise_distances(coords):
	assert(coords.shape[1] == 2) # Nx2 matrix
	num_xy = coords.shape[0]
	dists = []
	for i in range(coords.shape[0]):
		for j in range(coords.shape[0]):
			if i > j:
				continue
			p0 = coords[i]
			p1 = coords[j]
			d = np.linalg.norm(p1-p0)
			dists.append(PairwiseDistance(i, j, d))
	return dists

def _compute_empirical_covariance(local_dists, signals):
	assert(signals.shape[1] == 2) # Nx2 matrix

	C0 = 0.0
	mk = len(local_dists)*2 # how many signals we add, one per x and y
	for k in range(len(local_dists)):
		d = local_dists[k]
		lx0 = signals[d.p0_idx][0]
		ly0 = signals[d.p0_idx][1]
		lx1 = signals[d.p1_idx][0]
		ly1 = signals[d.p1_idx][1]
		C0 += lx0*lx1 + ly0*ly1

	C0 = C0 / mk
	return C0

def _compute_covariance_matrix(new_coords, ref_coords, C0, cov_func):
	assert(new_coords.shape[1] == 2)
	assert(ref_coords.shape[1] == 2)

	num_new_xy = new_coords.shape[0]
	num_ref_xy = ref_coords.shape[0]

	C = np.zeros((num_new_xy, num_ref_xy))
	for i in range(num_new_xy):
		for j in range(num_ref_xy):
			p0 = new_coords[i]
			p1 = ref_coords[j]
			d = np.linalg.norm(p1-p0)
			if d == 0.0:
				C[i][j] = C0
			else:
				C[i][j] = cov_func(d)

	C = np.concatenate([
		np.concatenate([C, np.zeros((num_new_xy,num_ref_xy))], axis=1),
		np.concatenate([np.zeros((num_new_xy,num_ref_xy)), C], axis=1),
	], axis=0)

	return C

def _compute_distance_interval(dists):
	x = np.array([d.dist for d in dists])
	std = np.std(x) # find deviation of distances for example 561 meters
	r = 10**math.floor(math.log10(std)) # r is 100 in the case of 561
	double_delta = math.floor(std/r)*r  # so floor(561/100)*100 = 5 * 100 = 500 meters
	return double_delta

class CovarianceFunction:

	def __init__(self, distance_intervals, empirical_cov):
		C0 = empirical_cov[0]
		sinc_func = lambda x, k: C0*(k/x) * np.sin(x/k)
		popt, _ = optimize.curve_fit(sinc_func, distance_intervals, empirical_cov)
		fitted_sinc = lambda x: sinc_func(x, *popt)

		self.distance_intervals =  distance_intervals
		self.empirical_cov = empirical_cov
		self.fitted_cov = fitted_sinc(distance_intervals)
		self._func = fitted_sinc

	def __call__(self, dist):
		return self._func(dist)

class Collocation:

	def __init__(self, source_coords, target_coords, initial_transf):
		assert(source_coords.shape[1] == 2)
		assert(target_coords.shape[1] == 2)

		self.source_coords = source_coords # maybe we dont need to store these
		self.signals = target_coords-initial_transf(source_coords) # residuals
		self.cov_func = self._fit_empirical_covariance_func(self.signals, self.source_coords)
		self.initial_transf = initial_transf

	def _fit_empirical_covariance_func(self, signals, coords):
		pairwise_dists = _compute_paiwise_distances(coords)
		pairwise_dists.sort(key=lambda x: x.dist)

		double_delta = _compute_distance_interval(pairwise_dists)
		delta = double_delta / 2.0
		groups = []
		for k, g in itertools.groupby(pairwise_dists, lambda d: int(d.dist/double_delta)+1 if d.dist != 0.0 else 0):
			groups.append(list(g))

		# for double_delta = 200 -> 0, 200, 400, 600
		# distance_intervals will be 100, 300, 500...
		# clamp 0 to a small value so that curve will have a solution on 0
		distance_intervals = np.array([max(delta*(2*i-1), 0.0001) for i in range(len(groups))])
		empirical_covs = np.array([_compute_empirical_covariance(g, signals) for g in groups])

		cov_func = CovarianceFunction(distance_intervals, empirical_covs)
		return cov_func

	def __call__(self, coords):
		assert(coords.shape[1] == 2)
		num_xy = coords.shape[0]

		C0 = self.cov_func.empirical_cov[0]
		Cxx = _compute_covariance_matrix(self.source_coords, self.source_coords, C0, self.cov_func)
		Cyx = _compute_covariance_matrix(coords, self.source_coords, C0, self.cov_func)

		num_signals = self.signals.shape[0]*2
		init_coords = self.initial_transf(coords)
		S = np.concatenate([self.signals[:, 0], self.signals[:, 1]]).reshape(num_signals, 1)
		x0 = np.concatenate([init_coords[:, 0], init_coords[:, 1]]).reshape(num_xy*2, 1)
		x = x0 + Cyx @ np.linalg.inv(Cxx) @ S

		return np.concatenate([x[0:num_xy], x[num_xy:2*num_xy]], axis=1)
