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
    def __init__(self, coeffs, inverse, iterative_inverse=True):
        self._coeffs = coeffs
        self._inverse = inverse
        A = coeffs[0:6]
        B = coeffs[6:12]
        if iterative_inverse:
            self._transformer = pyproj.Transformer.from_pipeline('''
                +proj=pipeline
                +step +proj=horner +ellps=bessel +deg=2 +range=10000000
                    +fwd_origin=0.0,0.0
                    +fwd_u={A0},{A1},{A3},{A2},{A5},{A4}
                    +fwd_v={B0},{B2},{B4},{B1},{B5},{B3}
                '''.format(
                    A0=A[0], A1=A[1], A2=A[2], A3=A[3], A4=A[4], A5=A[5],
                    B0=B[0], B1=B[1], B2=B[2], B3=B[3], B4=B[4], B5=B[5],
                ))
        else:
            C = coeffs[12:17]
            D = coeffs[17:22]
            self._transformer = pyproj.Transformer.from_pipeline('''
                +proj=pipeline
                +step +proj=horner +ellps=bessel +deg=2 +range=10000000
                    +fwd_origin=0.0,0.0
                    +fwd_u={A0},{A1},{A3},{A2},{A5},{A4}
                    +fwd_v={B0},{B2},{B4},{B1},{B5},{B3}
                    +inv_origin={A0},{B0}
                    +inv_u=0.0,{C1},{C3},{C2},{C5},{C4}
                    +inv_v=0.0,{D2},{D4},{D1},{D5},{D3}
                '''.format(
                    A0=A[0], A1=A[1], A2=A[2], A3=A[3], A4=A[4], A5=A[5],
                    B0=B[0], B1=B[1], B2=B[2], B3=B[3], B4=B[4], B5=B[5],
                    C1=C[0], C2=C[1], C3=C[2], C4=C[3], C5=C[4],
                    D1=D[0], D2=D[1], D3=D[2], D4=D[3], D5=D[4]
                ))

    def __call__(self, x, y, z=None):
        if (self._inverse):
            return self._transformer.transform(x, y, z, direction=pyproj.enums.TransformDirection.INVERSE)
        else:
            return self._transformer.transform(x, y, z, direction=pyproj.enums.TransformDirection.FORWARD)