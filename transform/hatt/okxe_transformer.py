import pyproj

"""
OKXETransformer transforms projected coordinates of a point
between the Old Greek datum and the GGRS87 datum using the
published polynomial coefficients of OKXE
Old Greek datum:
	epsg: (http://spatialreference.org/ref/epsg/4815/)
	projection: Azimuthal Equidistant (Hatt map blocks)
GGRS87 datum:
	epsg: (http://spatialreference.org/ref/epsg/2100/html/)
	projection: Transverse Mercator (TM87)
"""

class OKXETransformer(object):
	'''
	Func object for Old Greek Datum.
	Transforms in place from Hatt ref system to GGRS87 / GG (inverse=False)
	or from GGRS87 / GG to Hatt ref system (inverse=True)
	'''
	def __init__(self, coeffs, inverse):
		self._coeffs = coeffs
		self._inverse = inverse
		A = coeffs[0:6]
		B = coeffs[6:12]
		self._transformer = pyproj.Transformer.from_pipeline('''
			+proj=pipeline
			+step +proj=horner +ellps=bessel +fwd_origin=0.0,0.0 +deg=2 +range=10000000
				+fwd_u={A0},{A1},{A3},{A2},{A5},{A4}
				+fwd_v={B0},{B2},{B4},{B1},{B5},{B3}
			'''.format(
				A0=A[0], A1=A[1], A2=A[2], A3=A[3], A4=A[4], A5=A[5],
				B0=B[0], B1=B[1], B2=B[2], B3=B[3], B4=B[4], B5=B[5]
			))

	def __call__(self, x, y, z=None):
		if (self._inverse):
			return self._transformer.transform(x, y, z, direction=pyproj.enums.TransformDirection.INVERSE)
		else:
			return self._transformer.transform(x, y, z, direction=pyproj.enums.TransformDirection.FORWARD)