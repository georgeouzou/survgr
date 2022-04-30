import enum

@enum.unique
class TransformationType(enum.Enum):
	Similarity = 0
	Affine = 1
	Polynomial = 2

@enum.unique
class ResidualCorrectionType(enum.Enum):
	NoCorrection = 0
	Collocation = 1
	Hausbrandt = 2

@enum.unique
class CovarianceFunctionType(enum.Enum):
	CardinalSine = 0
	Gaussian = 1
	Exponential = 2
	Spline = 3


