import math
import itertools
from dataclasses import dataclass
import numpy as np
from scipy import optimize
from scipy.interpolate import UnivariateSpline
from .types import CovarianceFunctionType

# for numerical stability
# coords in m
# distances in km
# covariances in cm^2
# signals in cm

# References
# ----------
# 1) Ampatzidis, Dimitrios & Melachroinos, Stavros. (2017).
# The connection of an old geodetic datum with a new one using Least Squares Collocation: The Greek case.
# Contribution to Geophysics and Geodesy. 47. 2017. 10.1515/congeo-2017-0003.
#
# 2) You, Rey-Jer & Hwang, Hwa-Wei. (2006).
# Coordinate Transformation between Two Geodetic Datums of Taiwan by Least-Squares Collocation.
# Journal of Surveying Engineering-asce - J SURV ENG-ASCE. 132. 10.1061/(ASCE)0733-9453(2006)132:2(64).
#
# 3) Edward M. Mikhail & F. Ackermann (1976)
# Observations and Least Squares

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
			d /= 1000.0 # to km
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
			d /= 1000.0 # to km
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
	# input: distances in km
	# output: covariances in cm^2

	def __init__(self, distance_intervals, empirical_cov, func_type):
		if func_type == CovarianceFunctionType.CardinalSine:
			self._func = self._init_sinc(distance_intervals, empirical_cov)
		elif func_type == CovarianceFunctionType.Gaussian:
			self._func = self._init_gaussian(distance_intervals, empirical_cov)
		elif func_type == CovarianceFunctionType.Exponential:
			self._func = self._init_exp(distance_intervals, empirical_cov)
		else:
			self._func = self._init_spline(distance_intervals, empirical_cov)

		self.distance_intervals =  distance_intervals
		self.empirical_cov = empirical_cov
		self.fitted_cov = self._func(distance_intervals)

	def _init_sinc(self, distance_intervals, empirical_cov):
		C0 = empirical_cov[0]
		func = lambda x, k: C0*(k/x) * np.sin(x/k)
		popt, _ = optimize.curve_fit(func, distance_intervals, empirical_cov)
		fitted = lambda x: func(x, *popt)
		return fitted

	def _init_gaussian(self, distance_intervals, empirical_cov):
		C0 = empirical_cov[0]
		func = lambda x, k: C0*np.exp(-np.power(k, 2)*np.power(x, 2))
		popt, _ = optimize.curve_fit(func, distance_intervals, empirical_cov)
		fitted = lambda x: func(x, *popt)
		return fitted

	def _init_exp(self, distance_intervals, empirical_cov):
		C0 = empirical_cov[0]
		func = lambda x, k: C0*np.exp(-x*k)
		popt, _ = optimize.curve_fit(func, distance_intervals, empirical_cov)
		fitted = lambda x: func(x, *popt)
		return fitted

	def _init_spline(self, distance_intervals, empirical_cov):
		fitted = UnivariateSpline(distance_intervals, empirical_cov, s=100.0, ext='const')
		return fitted

	def __call__(self, dist):
		return self._func(dist)

class Collocation:

	def __init__(self, source_coords, target_coords, initial_transf, cov_function_type):
		assert(source_coords.shape[1] == 2)
		assert(target_coords.shape[1] == 2)

		signals = target_coords-initial_transf(source_coords)
		signals *= 100 # residuals to cm
		signal_mean_avg = np.mean(signals) # in cm
		signals -= signal_mean_avg

		self.source_coords = source_coords # maybe we dont need to store these
		self.signals = signals
		self.signal_mean_avg = signal_mean_avg
		self.cov_func = self._fit_empirical_covariance_func(self.signals, self.source_coords, cov_function_type)
		self.initial_transf = initial_transf

	def _fit_empirical_covariance_func(self, signals, coords, cov_function_type):
		pairwise_dists = _compute_paiwise_distances(coords)
		pairwise_dists.sort(key=lambda x: x.dist)

		double_delta = _compute_distance_interval(pairwise_dists)
		delta = double_delta / 2.0
		groups = []
		for k, g in itertools.groupby(pairwise_dists, lambda d: int(d.dist/double_delta)+1 if d.dist != 0.0 else 0):
			groups.append(list(g))

		# for double_delta = 0.2km -> 0, 0.2, 0.4, 0.6
		# distance_intervals will be ~0, 0.1, 0.3, 0.5...
		# clamp 0 to a very small value so that curve will fit on 0.0
		distance_intervals = np.array([max(delta*(2*i-1), 1e-6) for i in range(len(groups))])
		empirical_cov = np.array([_compute_empirical_covariance(g, signals) for g in groups])

		cov_func = CovarianceFunction(distance_intervals, empirical_cov, cov_function_type)
		return cov_func

	def __call__(self, coords):
		assert(coords.shape[1] == 2)

		C0 = self.cov_func.empirical_cov[0]
		Cxx = _compute_covariance_matrix(self.source_coords, self.source_coords, C0, self.cov_func)
		Cyx = _compute_covariance_matrix(coords, self.source_coords, C0, self.cov_func)

		num_signals = self.signals.shape[0]*2
		init_coords = self.initial_transf(coords)
		S = np.concatenate([self.signals[:, 0], self.signals[:, 1]]).reshape(num_signals, 1)
		S = Cyx @ np.linalg.inv(Cxx) @ S
		S += self.signal_mean_avg
		S /= 100.0 # back to meters

		num_xy = coords.shape[0]
		x0 = np.concatenate([init_coords[:, 0], init_coords[:, 1]]).reshape(num_xy*2, 1)
		x = x0 + S
		return np.concatenate([x[0:num_xy], x[num_xy:2*num_xy]], axis=1)
