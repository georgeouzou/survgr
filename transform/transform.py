# -*- coding: utf-8 -*-
import os
import enum
from functools import partial

import pyproj # TODO: update pyproj.transform as it is now deprecated
import numpy

from .hatt import hatt2ggrs
from .hatt.models import Hattblock
from .htrs.grid import GridFile

@enum.unique
class Datum(enum.Enum):
	HGRS87 = 0
	HTRS07 = 1
	OLD_GREEK= 2
	ED50 = 3
	WGS84 = 4

# All underlying datums used in Greece as the basis for the various reference systems.
DATUMS = {
	# id : name
	Datum.HGRS87:		'ΕΓΣΑ87',
	Datum.HTRS07: 		'HTRS07 (Hepos)',
	Datum.OLD_GREEK:	'Παλαιό Ελληνικό Datum (Νέο Bessel)',
	Datum.ED50:			'ED50 (Ελλάδα)',
	Datum.WGS84:		'WGS84',
}

class ReferenceSystem(object):
	'''
	Utility classed to encapsulate the used in greece reference systems.
	'''
	def __init__(self, name, datum, proj4text):
		self.name = name
		self.datum = datum
		self.proj4text = proj4text

	def is_longlat(self):
		return '+proj=longlat' in self.proj4text
		
# All the reference systems used in Greece.
# Each Hattblock has its own reference system (see Hattblock proj4text property...)
# All +towgs84 dx,dy,dz are taken from Fotiou book
# going from ed50->wgs84->egsa87 == ed50->egsa87
REF_SYS = {
	2100: ReferenceSystem('ΕΓΣΑ87 / ΤΜ87', Datum.HGRS87, '+proj=etmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=-199.723,74.030,246.018 +units=m +no_defs'),
	4121: ReferenceSystem('ΕΓΣΑ87 (λ,φ)', Datum.HGRS87, '+proj=longlat +ellps=GRS80 +towgs84=-199.723,74.030,246.018 +no_defs'),
	4815: ReferenceSystem('Παλαιό Ελληνικό (λ,φ)', Datum.OLD_GREEK, '+proj=longlat +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +no_defs'),
	4326: ReferenceSystem('WGS84 (λ,φ)', Datum.WGS84, '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'),
	4230: ReferenceSystem('ED50 (λ,φ)', Datum.ED50, '+proj=longlat +ellps=intl +towgs84=-61.613,-81.380,-164.182 +no_defs'),
	23034: ReferenceSystem('ΕD50 / UTM 34N', Datum.ED50, '+proj=utm +zone=34 +ellps=intl +towgs84=-61.613,-81.380,-164.182 +units=m +no_defs'),
	23035: ReferenceSystem('ED50 / UTM 35N', Datum.ED50, '+proj=utm +zone=35 +ellps=intl +towgs84=-61.613,-81.380,-164.182 +units=m +no_defs '),
	# Παλαιό Ελληνικό / Hatt proj4text is general a template, that various hatt map blocks use with specific lat_0 and lon_0
	1000000: ReferenceSystem('Παλαιό Ελληνικό / Hatt', Datum.OLD_GREEK, '+proj=aeqd +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000001: ReferenceSystem('Παλαιό Ελληνικό / TM3 Δυτ.Ζώνη', Datum.OLD_GREEK, '+proj=tmerc +lat_0=34 +lon_0=-3 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000002: ReferenceSystem('Παλαιό Ελληνικό / TM3 Κεντ.Ζώνη', Datum.OLD_GREEK, '+proj=tmerc +lat_0=34 +lon_0=0 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000003: ReferenceSystem('Παλαιό Ελληνικό / TM3 Ανατ.Ζώνη', Datum.OLD_GREEK, '+proj=tmerc +lat_0=34 +lon_0=3 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000004: ReferenceSystem('HTRS07 (λ,φ)', Datum.HTRS07, '+proj=longlat +ellps=GRS80 +towgs84=0,0,0 +no_defs'),
	1000005: ReferenceSystem('HTRS07 / TM07', Datum.HTRS07, '+proj=etmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=-2000000 +ellps=GRS80 +towgs84=0,0,0 +units=m +no_defs'),
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
		self.transformation_steps = []
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
	
		try:
			self._compile(**params)
		except KeyError as e:
			key = e.args[0]
			if key == 'from_hattblock':
				key = 'from_hatt_id'
			elif key == 'to_hattblock':
				key = 'to_hatt_id'
			raise ValueError('Parameter Error: "%s" parameter is required' % key)

		# if any key error happens this will throw above
		self.from_refsys = REF_SYS[params['from_srid']]
		self.to_refsys = REF_SYS[params['to_srid']]
			
	def _compute_tranform_accuracy(self, refsys1, refsys2):

		#middle_text = "%s συντεταγμένων %s σε %s συντεταγμένες %s" % (
		#		"γεωδαιτικών" if refsys1.is_longlat() else "προβολικών",
		#		refsys1.name,
		#		"γεωδαιτικές" if refsys2.is_longlat() else "προβολικές",
		#		refsys2.name
		#)
		middle_text = "%s -> %s" % (refsys1.name, refsys2.name)

		if refsys1.datum == refsys2.datum:
			# this is a simple project / unproject case
			return "Μετατροπή %s. Ακρίβεια: ∞ (ίδιο datum)" % (middle_text)
		else:
			# this is a datum change
			ggrs_htrs = (refsys1.datum == Datum.HGRS87 and refsys2.datum == Datum.HTRS07)
			ggrs_htrs |= (refsys1.datum == Datum.HTRS07 and refsys2.datum == Datum.HGRS87)

			ggrs_oldgreek = (refsys1.datum == Datum.HGRS87 and refsys2.datum == Datum.OLD_GREEK)
			ggrs_oldgreek |= (refsys1.datum == Datum.OLD_GREEK and refsys2.datum == Datum.HGRS87)

			ggrs_ed50 = (refsys1.datum == Datum.HGRS87 and refsys2.datum == Datum.ED50)
			ggrs_ed50 |= (refsys1.datum == Datum.ED50 and refsys2.datum == Datum.HGRS87)
 			
			ggrs_wgs84 = (refsys1.datum == Datum.HGRS87 and refsys2.datum == Datum.WGS84)
			ggrs_wgs84 |= (refsys1.datum == Datum.WGS84 and refsys2.datum == Datum.HGRS87)

			ed50_wgs84 = (refsys1.datum == Datum.ED50 and refsys2.datum == Datum.WGS84)
			ed50_wgs84 |= (refsys1.datum == Datum.WGS84 and refsys2.datum == Datum.ED50)
			
			if ggrs_htrs:
				return "Μετασχηματισμός %s μέσω διορθωτικών grid του Hepos. Ακρίβεια Οριζόντια ~ 0.05 m, Υψομετρική > 1 m" % (middle_text)
			elif ggrs_oldgreek: 
				return "Μετασχηματισμός %s μέσω πολυωνυμικών συντελεστών OKXE. Ακρίβεια ~ 0.10-0.15 m" % (middle_text)
			elif ggrs_ed50 or ggrs_wgs84 or ed50_wgs84:
				acc = "1" if ggrs_wgs84 else "5-10"
				return "Προσεγγιστικός μετασχηματισμός %s. Ακρίβεια ~ %s m" % (middle_text, acc)

			return ""

	def _compile(self, **params):	
		from_srid = params['from_srid']
		to_srid = params['to_srid']

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
						  datum = srs1.datum,
						  proj4text = params['from_hattblock'].proj4text)
		if to_srid == HATT_SRID:
			srs2 = ReferenceSystem(name = '%s (%s)' % (srs2.name, params['to_hattblock'].name),
						  datum = srs2.datum,
						  proj4text = params['to_hattblock'].proj4text)
	 	
		# check if from-datum is the old greek, so we can use OKXE transformation
		if srs1.datum == Datum.OLD_GREEK and srs2.datum != Datum.OLD_GREEK:
			block = params['from_hattblock']
			# if not hatt projected ref. sys. but on greek datum... i.e. TM03 --> HATT
			if from_srid != HATT_SRID:
				self._compile(from_srid=from_srid, to_srid=HATT_SRID, to_hattblock=block) # using ProjTransformer
			# transform hatt to ggrs / greek grid
			self.transformers.append(OKXETransformer(block.get_coeffs(), inverse=False))
			self.log.append('%s (%s) --(OKXE)--> %s' % (REF_SYS[HATT_SRID].name, block.name, REF_SYS[TM87_SRID].name))
			self.transformation_steps.append(self._compute_tranform_accuracy(REF_SYS[HATT_SRID], REF_SYS[TM87_SRID]))
			# call recursively with ggrs / greek grid to srid
			self._compile(from_srid=TM87_SRID, to_srid=to_srid)
			return # end

		# check if target-datum is the old greek, so we can use OKXE transformation
		if srs1.datum != Datum.OLD_GREEK and srs2.datum == Datum.OLD_GREEK:
			block = params['to_hattblock']
			# we need to transform from ggrs/greek grid to hatt so...we call recursively with ggrs / greek grid
			self._compile(from_srid=from_srid, to_srid=TM87_SRID)
			# and then transform from ggrs / greek grid to hatt map block
			self.transformers.append(OKXETransformer(block.get_coeffs(), inverse=True))
			self.log.append('%s --(OKXE)--> %s (%s)' % (REF_SYS[TM87_SRID].name, REF_SYS[HATT_SRID].name, block.name))
			self.transformation_steps.append(self._compute_tranform_accuracy(REF_SYS[TM87_SRID], REF_SYS[HATT_SRID]))
			# if to_srid is not hatt projected but in the old greek datum... i.e. TM03
			if to_srid != HATT_SRID:
				self._compile(from_srid=HATT_SRID, to_srid=to_srid, from_hattblock=block)
			return # end
		
		# check if from-datum is htrs, so we can use Hepos transformation
		if srs1.datum == Datum.HTRS07 and srs2.datum != Datum.HTRS07:
			# transform to TM07 projection if in HTRS datum
			self._compile(from_srid=from_srid, to_srid=TM07_SRID)
			# HTRS/TM07 --> GGRS/Greek Grid
			self.transformers.append(HeposTransformer(inverse=False))
			self.log.append('%s --(Hepos)--> %s' % (REF_SYS[TM07_SRID].name, REF_SYS[TM87_SRID].name))
			self.transformation_steps.append(self._compute_tranform_accuracy(REF_SYS[TM07_SRID], REF_SYS[TM87_SRID]))
			# call recursively with ggrs / greek grid
			self._compile(from_srid=TM87_SRID, to_srid=to_srid)
			return # end

		# check if target-datum is htrs 
		if srs1.datum != Datum.HTRS07 and srs2.datum == Datum.HTRS07:
			# transform from anywhere to greek grid
			self._compile(from_srid=from_srid, to_srid=TM87_SRID)
			# then use Hepos transformation : GGRS87/GG --> HTRS / TM07
			self.transformers.append(HeposTransformer(inverse=True))
			# update log
			self.log.append('%s --(Hepos)--> %s' % (REF_SYS[TM87_SRID].name, REF_SYS[TM07_SRID].name))
			self.transformation_steps.append(self._compute_tranform_accuracy(REF_SYS[TM87_SRID], REF_SYS[TM07_SRID]))
			# and transform to longlat if not TM07
			self._compile(from_srid=TM07_SRID, to_srid=to_srid)
			return # end
		
		# last and general transformation
		self.transformers.append(ProjTransformer(srs1.proj4text, srs2.proj4text))
		self.log.append('%s --> %s' % (srs1.name, srs2.name))
		self.transformation_steps.append(self._compute_tranform_accuracy(srs1, srs2))

	def __call__(self, x, y, z=None):
		# create numpy array to modify in place
		# fastest method for proj4 library and modifies in place for the custom methods
		x = numpy.asarray(x)
		y = numpy.asarray(y)
		if z is not None:
			z = numpy.asarray(z)

		if z is not None:
			for f in self.transformers:
				x, y, z = f(x, y, z)
		else:
			for f in self.transformers:
				x, y  = f(x, y)

		return tuple(filter(lambda array: array is not None, [x, y, z]))

	def log_str(self):
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
	def __init__(self, coeffs, inverse):
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

	def __init__(self, inverse):
		# grid containing the shifts de, dn in cm
		self._grid = GridFile(self.grid_path)
		self._inverse = inverse
		# extended better ggrs - htrs 7 param. transformation provided by Hepos service
		self._htrs_to_ggrs_approx = pyproj.Transformer.from_pipeline(
			'''
			+proj=pipeline
			+step +inv +proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=-2000000 +ellps=GRS80 +units=m 
			+step +proj=cart
			+step +proj=helmert +convention=coordinate_frame 
				+x=203.437 +y=-73.461 +z=-243.594 
				+rx=-0.170 +ry=-0.060 +rz=-0.151 +s=-0.294
			+step +inv +proj=cart
			+step +proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +units=m 
			''')

	def __call__(self, x, y, z=None):
		grid = self._grid
		if self._inverse: #ggrs -> htrs
			# first apply the approximate tranformation
			h_xyz = self._htrs_to_ggrs_approx.transform(x, y, z, direction=pyproj.enums.TransformDirection.INVERSE)
			x, y = h_xyz[0], h_xyz[1] # we need to interpolate with htrs coords
			for index, pt in enumerate(zip(x, y)):
				de, dn = grid.interpolate(pt[0], pt[1])
				x[index] -= de / 100.0 # grid file contains cm corrections
				y[index] -= dn / 100.0

			return h_xyz

		else: # htrs -> ggrs
			# first apply the approximate transformation
			g_xyz = self._htrs_to_ggrs_approx.transform(x, y, z, direction=pyproj.enums.TransformDirection.FORWARD)
			# then apply shift correction
			g_x, g_y = g_xyz[0], g_xyz[1]
			for index, pt in enumerate(zip(x, y)): #again we need to interpolate with htrs coords
				de, dn = grid.interpolate(pt[0], pt[1])
				g_x[index] += de / 100.0
				g_y[index] += dn / 100.0

			return g_xyz
