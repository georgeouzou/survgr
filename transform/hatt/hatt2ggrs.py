""" 
The functions below transform projected coordinates of a point
between the Old Greek datum and the GGRS87 datum using the
published polynomial coefficients of OKXE (http://www.okxe.gr/el/)
Old Greek datum:
	epsg: (http://spatialreference.org/ref/epsg/4815/)
	projection: Azimuthal Equidistant (Hatt map blocks)
GGRS87 datum:
	epsg: (http://spatialreference.org/ref/epsg/2100/html/)
	projection: Transverse Mercator (TM87)
"""

def fwd(coeffs, x, y):
	""" Transforms projected coordinates from the Old Greek datum to GGRS87.
	Params:
		coeffs (float sequence): the 12 coefficients of the current Hatt map block [A0...B0...]
		x, y (floats): Easting, Northing Hatt coordinates of a point
	Returns:
		(float tuple): Easting, Northing GGRS87 coordinates
	"""
	#
	# | E |   | A0 |   | A1 + A3*x ' A2 + A4*y + A5*x | | x |
	# |   | = |    | + |---------- ' ---------------- | |   |
	# | N |   | B0 |   | B1 + B3*x ' B2 + B4*y + B5*x | | y |
	#
	if len(coeffs) != 12: 
		raise ValueError("Wrong number of hatt coefficients.")
	
	x2 = pow(x,2)
	y2 = pow(y,2)
	xy = x * y
	e = coeffs[0] + coeffs[1]*x + coeffs[2]*y + coeffs[3]*x2 + coeffs[4]*y2 + coeffs[5]*xy
	n = coeffs[6] + coeffs[7]*x + coeffs[8]*y + coeffs[9]*x2 + coeffs[10]*y2 + coeffs[11]*xy
	return (e, n)

def inv(coeffs, x, y):
	""" Transforms projected coordinates from GGRS87 to the Old Greek datum.
	Params:
		coeffs (float sequence): the 12 coefficients of the current Hatt map block [A0...B0...]
		x, y (floats): Easting, Northing GGRS87 coordinates of a point
	Returns:
		(float tuple): Easting, Northing Hatt coordinates
	"""
	#
	# | x |   | A1 + A3*x ' A2 + A4*y + A5*x |-1 | E-A0 |
	# |   | = |---------- ' ---------------- |   | 	    |
	# | y |   | B1 + B3*x ' B2 + B4*y + B5*x |   | N-B0 |
	#
	if len(coeffs) != 12: 
		raise ValueError("Wrong number of hatt coefficients.")
	
	e = x - coeffs[0]
	n = y - coeffs[6]

	x0, y0 = 0, 0

	iters = 0
	convergence = 0.001 # stop when 1 mm
	while iters < 10:
		a = coeffs[1] + coeffs[3]*x0
		b = coeffs[2] + coeffs[4]*y0 + coeffs[5]*x0
		c = coeffs[7] + coeffs[9]*x0
		d = coeffs[8] + coeffs[10]*y0 + coeffs[11]*x0
		
		idet = 1 / (a*d - b*c)
		x = idet * (d*e - b*n)
		y = idet * (a*n - c*e)

		if (abs(x-x0) < convergence) and (abs(y-y0) < convergence):
			return (x, y)
		else:
			x0, y0 = x, y
			iters += 1

	return (0, 0)
