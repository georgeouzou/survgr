# -*- coding: utf-8 -*-
import os
from functools import partial

import pyproj
import numpy

from .hatt import hatt2ggrs
from .hatt.models import Hattblock
from .htrs.grid import GridFile

class ReferenceSystem(object):
	'''
	Utility classed to encapsulate the used in greece reference systems.
	'''
	def __init__(self, name, datum_id, proj4text):
		self.name = name
		self.datum_id = datum_id
		self.proj4text = proj4text

	def is_longlat(self):
		return '+proj=longlat' in self.proj4text
		
# All underlying datums used in Greece as the basis for the various reference systems.
DATUMS = {
	# id : name
	0: 'ΕΓΣΑ87',
	1: 'HTRS07 (Hepos)',
	2: 'Παλαιό Ελληνικό Datum',
	3: 'ED50 (Ελλάδα)',
	4: 'WGS84'
}

# All the reference systems used in Greece.
# Each Hattblock has its own reference system (see Hattblock proj4text property...)
REF_SYS = {
	2100: ReferenceSystem('ΕΓΣΑ87 / ΤΜ87', 0, '+proj=etmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=-199.723,74.030,246.018 +units=m +no_defs'),
	4121: ReferenceSystem('ΕΓΣΑ87 (λ,φ)', 0, '+proj=longlat +ellps=GRS80 +towgs84=-199.723,74.030,246.018 +no_defs'),
	4815: ReferenceSystem('Παλαιό Ελληνικό (λ,φ)', 2, '+proj=longlat +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +no_defs'),
	4326: ReferenceSystem('WGS84 (λ,φ)', 4, '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'),
	4230: ReferenceSystem('ED50 (λ,φ)', 3, '+proj=longlat +ellps=intl +towgs84=-61.613,-81.380,-164.182 +no_defs'),
	23034: ReferenceSystem('ΕD50 / UTM 34N', 3, '+proj=utm +zone=34 +ellps=intl +towgs84=-61.613,-81.380,-164.182 +units=m +no_defs'),
	23035: ReferenceSystem('ED50 / UTM 35N', 3, '+proj=utm +zone=35 +ellps=intl +towgs84=-61.613,-81.380,-164.182 +units=m +no_defs '),
	# Παλαιό Ελληνικό / Hatt proj4text is general a template, that various hatt map blocks use with specific lat_0 and lon_0
	1000000: ReferenceSystem('Παλαιό Ελληνικό / Hatt', 2, '+proj=aeqd +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000001: ReferenceSystem('Παλαιό Ελληνικό / TM3 Δυτ.Ζώνη', 2, '+proj=tmerc +lat_0=34 +lon_0=-3 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000002: ReferenceSystem('Παλαιό Ελληνικό / TM3 Κεντ.Ζώνη', 2, '+proj=tmerc +lat_0=34 +lon_0=0 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000003: ReferenceSystem('Παλαιό Ελληνικό / TM3 Ανατ.Ζώνη', 2, '+proj=tmerc +lat_0=34 +lon_0=3 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000004: ReferenceSystem('HTRS07 (λ,φ)', 1, '+proj=longlat +ellps=GRS80 +towgs84=0,0,0 +no_defs'),
	1000005: ReferenceSystem('HTRS07 / TM07', 1, '+proj=etmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=-2000000 +ellps=GRS80 +towgs84=0,0,0 +units=m +no_defs'),
	#1000006: ReferenceSystem('ΕΓΣΑ87 (X,Y,Z)', 0, '+proj=geocent +ellps=GRS80 +towgs84=-199.723,74.030,246.018 +no_defs'),
	#1000007: ReferenceSystem('Παλαιό Ελληνικό (X,Y,Z)', 2, '+proj=geocent +ellps=bessel +towgs84=456.387,372.620,496.818 +no_defs'),
	#1000008: ReferenceSystem('HTRS07 (X,Y,Z)', 1, '+proj=geocent +ellps=GRS80 +towgs84=0,0,0 +no_defs')
}

# mostly used constants below 
HATT_SRID = 1000000
TM07_SRID = 1000005
TM87_SRID = 2100

class TransformerError(Exception):
	pass


class WorkHorseTransformer(object):
	'''
	Transforms points from ref. system 1 to ref. system 2 using other sub-transformers:
		- ProjTransformer
		- OKXETransformer
		- HeposTransformer
	Transformers are functors that get called with x, y and maybe z numpy arrays as arguments 
	and return x, y, maybe z numpy arrays transformed.
	Keyword arguments can be: 
		General params:
		-from_srid: the REF_SYS key corresponding to ref. system 1.
		-to_srid: the REF_SYS key corresponding to ref. system 2.
		Hatt params:
		-from_hatt_id: the id of the 1:50000 hatt block (given by OKXE service) if ref. system 1 is a hattblock.
		-to_hatt_id: the id of the 1:50000 hatt block if ref. system 2 is a hattblock.
	'''
	
	def __init__(self, **params):
		self.transformers = []
		self.log = []
	
		# add hattblock objects to the parameters, needed in _compile function
		if 'from_hatt_id' in params:
			if 'from_srid' not in params: params['from_srid'] = HATT_SRID
			try:
				params['from_hattblock'] = Hattblock.objects.get(id=params['from_hatt_id'])
			except Hattblock.DoesNotExist:
				raise ValueError("Parameter Error: Hatt block with id=%d does not exist" % params['from_hatt_id'])

		if 'to_hatt_id' in params:
			if 'to_srid' not in params: params['to_srid'] = HATT_SRID
			try:
				params['to_hattblock'] = Hattblock.objects.get(id=params['to_hatt_id'])
			except Hattblock.DoesNotExist:
				raise ValueError('Parameter Error: Hatt block with id "%d" does not exist' % params['to_hatt_id'])

		# TODO: check for srid numbers wrong, srid not integers, HATT_SRID without from_hattblock/to_hattblock etc..
		self._compile(**params)
			
	def _compile(self, **params):
		try:
			from_srid = params['from_srid']
			to_srid = params['to_srid']
		except KeyError as e:
			raise ValueError('Parameter Error: "%s" parameter is required' % e.args[0])

		# check if from-to ref. systems are the same (except if we are dealing with hatt blocks)
		# (compile can be recursive so we need this)
		if from_srid == to_srid:
			if from_srid != HATT_SRID: #and to_srid != HATT_SRID,  if both are NOT hattblocks
				return
			else: #if both are hattblocks
				if params['from_hattblock'].id == params['to_hattblock'].id:
					return # end

		srs1 = REF_SYS[from_srid]
		srs2 = REF_SYS[to_srid]
		# specialize proj4 definition for any of the reference systems that are hatt blocks
		if from_srid == HATT_SRID:
			srs1 = ReferenceSystem(name = '%s (%s)' % (srs1.name, params['from_hattblock'].name), 
						  datum_id = srs1.datum_id, 
						  proj4text = params['from_hattblock'].proj4text)
		
		if to_srid == HATT_SRID:
			srs2 = ReferenceSystem(name = '%s (%s)' % (srs2.name, params['to_hattblock'].name), 
						  datum_id = srs2.datum_id, 
						  proj4text = params['to_hattblock'].proj4text)
	 	
		# update log
		self.log.append('transformer: %s --> %s' % (srs1.name, srs2.name))

		# check if from-datum is the old greek, so we can use OKXE transformation
		if srs1.datum_id == 2 and srs2.datum_id != 2:
			block = params['from_hattblock']
			# if not hatt projected ref. sys. but on greek datum... i.e. TM03 --> HATT
			if from_srid != HATT_SRID:
				self._compile(from_srid=from_srid, to_srid=HATT_SRID, to_hattblock=block) # using ProjTransformer
			# transform hatt to ggrs / greek grid
			self.transformers.append(OKXETransformer(block.get_coeffs(), inverse=False))		
			# call recursively with ggrs / greek grid to srid
			self._compile(from_srid=TM87_SRID, to_srid=to_srid)
			return # end

		# check if target-datum is the old greek, so we can use OKXE transformation
		if srs1.datum_id != 2 and srs2.datum_id == 2:
			block = params['to_hattblock']
			# we need to transform from ggrs/greek grid to hatt so...we call recursively with ggrs / greek grid
			self._compile(from_srid=from_srid, to_srid=TM87_SRID)
			# and then transform from ggrs / greek grid to hatt map block
			self.transformers.append(OKXETransformer(block.get_coeffs(), inverse=True))
			# if to_srid is not hatt projected but in the old greek datum... i.e. TM03
			if to_srid != HATT_SRID:
				self._compile(from_srid=HATT_SRID, to_srid=to_srid, from_hattblock=block)
			return # end
		
		# check if from-datum is htrs, so we can use Hepos transformation
		if srs1.datum_id == 1 and srs2.datum_id != 1:
			# transform to TM07 projection if in HTRS datum
			self._compile(from_srid=from_srid, to_srid=TM07_SRID)
			# HTRS/TM07 --> GGRS/Greek Grid
			self.transformers.append(HeposTransformer(inverse=False))
			# call recursively with ggrs / greek grid
			self._compile(from_srid=TM87_SRID, to_srid=to_srid)
			return # end

		# check if target-datum is htrs 
		if srs1.datum_id != 1 and srs2.datum_id == 1:
			# transform from anywhere to greek grid
			self._compile(from_srid=from_srid, to_srid=TM87_SRID)
			# then use Hepos transformation : GGRS87/GG --> HTRS / TM07
			self.transformers.append(HeposTransformer(inverse=True))
			# and transform to longlat if not TM07
			self._compile(from_srid=TM07_SRID, to_srid=to_srid)
			return # end
		
		# last and general transformation
		self.transformers.append(ProjTransformer(srs1.proj4text, srs2.proj4text))

	def __call__(self, x, y, z=None):
		# create numpy array to modify in place
		# fastest method for proj4 library and modifies in place for the custom methods
		x = numpy.asarray(x)
		y = numpy.asarray(y)
		if z:
			z = numpy.asarray(z)

		if z:
			for f in self.transformers:
				x, y, z = f(x, y, z)
		else:
			for f in self.transformers:
				x, y  = f(x, y)
		
		return tuple(filter(lambda array: array is not None, [x, y, z]))

	def log(self):
		return '\n'.join(list(self.log))

#
# Below are the transformers that can be used with the workhorse transformer
#
def ProjTransformer(from_proj4, to_proj4):
    #Returns a callable partial function for general purpose - proj4 based tranformations.
	p1 = pyproj.Proj(from_proj4)
	p2 = pyproj.Proj(to_proj4)
	return partial(pyproj.transform, p1, p2)

class OKXETransformer(object):
	'''
	Func object for Old Greek Datum.
	Transforms in place from Hatt ref system to GGRS87 / GG (inverse=False)
	or from GGRS87 / GG to Hatt ref system (inverse=True)
	'''
	def __init__(self, coeffs, inverse=False):
		self._coeffs = coeffs
		self._inverse = inverse
		if inverse: # ggrs -> hatt
			self._scalarfunc = hatt2ggrs.inv
		else: # hatt -> ggrs
			self._scalarfunc = hatt2ggrs.fwd
				
	def __call__(self, x, y, z=None):
		for index, pt in enumerate(zip(x, y)):
			x[index], y[index] = self._scalarfunc(self._coeffs, pt[0], pt[1])

		return tuple(filter(lambda array: array is not None, [x, y, z]))

class HeposTransformer(object):
	'''
	Func object for HTRS07 Datum.
	Transforms in place from HTRS / TM07 to GGRS87 / GG (inverse=False)
	or from GGRS87 / GG to HTRS / TM07 (inverse=True)
	'''
	grid_path = os.path.join(os.path.dirname(__file__), "htrs", "htrs07.grb")

	def __init__(self, inverse=False):
		# grid containing the shifts de, dn in cm
		self._grid = GridFile(self.grid_path)

		# extended better ggrs - htrs 7 param. transformation provided by Hepos service
	    # overriding the proj4text of ggrs/gg shown in REF_SYS
		self._ggrs_proj4 = pyproj.Proj('+proj=etmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0\
		 +ellps=GRS80 +towgs84=-203.437,73.461,243.594,-0.17,-0.06,-0.151,0.294 +units=m +no_defs')
		self._htrs_proj4 = pyproj.Proj(REF_SYS[TM07_SRID].proj4text)
		self._inverse = inverse

	def __call__(self, x, y, z=None):
		grid = self._grid
		if self._inverse: #ggrs -> htrs
			# first apply the approximate tranformation
			h_xyz = pyproj.transform(self._ggrs_proj4, self._htrs_proj4, x, y, z)
			x, y = h_xyz[0], h_xyz[1] # we need to interpolate with htrs coords
			for index, pt in enumerate(zip(x, y)):
				de, dn = grid.interpolate(pt[0], pt[1])
				x[index] -= de / 100.0 # grid file contains cm corrections
				y[index] -= dn / 100.0

			return h_xyz

		else: # htrs -> ggrs
			# first apply the approximate transformation
			g_xyz = pyproj.transform(self._htrs_proj4, self._ggrs_proj4, x, y, z)
			# then apply shift correction
			g_x, g_y = g_xyz[0], g_xyz[1]
			for index, pt in enumerate(zip(x, y)): #again we need to interpolate with htrs coords
				de, dn = grid.interpolate(pt[0], pt[1])
				g_x[index] += de / 100.0
				g_y[index] += dn / 100.0

			return g_xyz
