# -*- coding: utf-8 -*-
import enum

import pyproj
import numpy as np

from .hatt.models import Hattblock
from .hatt.okxe_transformer import OKXETransformer
from .hatt.proj_generate import proj_text as hatt_proj_text_generate
from .htrs.hepos_transformer import HeposTransformer
from procrustes import deserialize as deserialize_procrustes

@enum.unique
class Datum(enum.Enum):
	HGRS87 = 0
	HTRS07 = 1
	NEW_BESSEL = 2
	ED50 = 3
	WGS84 = 4,
	PROCRUSTES = 5,
	OLD_BESSEL = 6,

# All underlying datums used in Greece as the basis for the various reference systems.
DATUMS = {
	# id : name
	Datum.HGRS87:		'ΕΓΣΑ87',
	Datum.HTRS07: 		'HTRS07 (Hepos)',
	Datum.NEW_BESSEL:	'Παλαιό Ελληνικό Datum - Νέο Bessel',
	Datum.ED50:			'ED50 (Ελλάδα)',
	Datum.WGS84:		'WGS84',
	Datum.PROCRUSTES:	'Προκρούστης',
	Datum.OLD_BESSEL:	'Παλαιο Ελληνικό Datum - Παλιό Bessel',
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
# proj4text for Hatt systems, is a general template that various hatt map blocks use with specific lat_0 and lon_0
REF_SYS = {
	2100: ReferenceSystem('ΕΓΣΑ87 / ΤΜ87', Datum.HGRS87, '+proj=etmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=-199.723,74.030,246.018 +units=m +no_defs'),
	4121: ReferenceSystem('ΕΓΣΑ87 (λ,φ)', Datum.HGRS87, '+proj=longlat +ellps=GRS80 +towgs84=-199.723,74.030,246.018 +no_defs'),
	4326: ReferenceSystem('WGS84 (λ,φ)', Datum.WGS84, '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'),
	4230: ReferenceSystem('ED50 (λ,φ)', Datum.ED50, '+proj=longlat +ellps=intl +towgs84=-61.613,-81.380,-164.182 +no_defs'),
	23034: ReferenceSystem('ΕD50 / UTM 34N', Datum.ED50, '+proj=utm +zone=34 +ellps=intl +towgs84=-61.613,-81.380,-164.182 +units=m +no_defs'),
	23035: ReferenceSystem('ED50 / UTM 35N', Datum.ED50, '+proj=utm +zone=35 +ellps=intl +towgs84=-61.613,-81.380,-164.182 +units=m +no_defs '),
	4815: ReferenceSystem('Νέο Bessel (λ,φ)', Datum.NEW_BESSEL, '+proj=longlat +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +no_defs'),
	1000000: ReferenceSystem('Νέο Bessel / Hatt', Datum.NEW_BESSEL, '+proj=aeqd +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000001: ReferenceSystem('Νέο Bessel / TM3 Δυτ.Ζώνη', Datum.NEW_BESSEL, '+proj=tmerc +lat_0=34 +lon_0=-3 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000002: ReferenceSystem('Νέο Bessel / TM3 Κεντ.Ζώνη', Datum.NEW_BESSEL, '+proj=tmerc +lat_0=34 +lon_0=0 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000003: ReferenceSystem('Νέο Bessel / TM3 Ανατ.Ζώνη', Datum.NEW_BESSEL, '+proj=tmerc +lat_0=34 +lon_0=3 +k=0.9999 +x_0=200000 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
	1000004: ReferenceSystem('HTRS07 (λ,φ)', Datum.HTRS07, '+proj=longlat +ellps=GRS80 +towgs84=0,0,0 +no_defs'),
	1000005: ReferenceSystem('HTRS07 / TM07', Datum.HTRS07, '+proj=etmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=-2000000 +ellps=GRS80 +towgs84=0,0,0 +units=m +no_defs'),
	1000006: ReferenceSystem('Προκρούστης', Datum.PROCRUSTES, ''),
	1000007: ReferenceSystem('Παλιό Bessel (λ,φ)', Datum.OLD_BESSEL, '+proj=longlat +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +no_defs'),
	1000008: ReferenceSystem('Παλιό Bessel / Hatt', Datum.OLD_BESSEL, '+proj=aeqd +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs'),
}

# mostly used constants below
HATT_NEW_SRID = 1000000
HATT_OLD_SRID = 1000008
TM07_SRID = 1000005
TM87_SRID = 2100
PROCRUSTES_SRID = 1000006

class TransformerError(Exception):
	pass

class ProjTransformer(object):

	def __init__(self, from_proj, to_proj):
		self._transformer = pyproj.Transformer.from_proj(from_proj, to_proj)

	def __call__(self, x, y, z=None):
		return self._transformer.transform(x, y, z)

class ProcrustesTransformer(object):

	def __init__(self, session_data):
		self._procrustes_transformer = deserialize_procrustes.from_session_data(session_data)
		if 'validation_statistics' in session_data['residual_correction']:
			self.accuracy = float(session_data['residual_correction']['validation_statistics']['std'])
		elif 'validation_statistics' in session_data['transformation']:
			self.accuracy = float(session_data['transformation']['validation_statistics']['std'])
		else:
			self.accuracy = float('inf')

	def __call__(self, x, y, z=None):
		num_coords = x.shape[0]
		in_coords = np.concatenate((x.reshape(num_coords,1), y.reshape(num_coords,1)), axis=1)
		out_coords = self._procrustes_transformer(in_coords)
		x, y = out_coords[:, 0], out_coords[:, 1]
		return tuple(filter(lambda array: array is not None, [x, y, z]))

class WorkHorseTransformer(object):
	'''
	Transforms points from ref. system 1 to ref. system 2 using other sub-transformers:
		- ProjTransformer
		- OKXETransformer
		- HeposTransformer
		- ProcrustesTransformer
	Transformers are functors that get called with x, y and maybe z numpy arrays as arguments
	and return x, y, maybe z numpy arrays transformed.
	Keyword arguments can be:
		General params:
		-from_srid: the REF_SYS key corresponding to ref. system 1.
		-to_srid: the REF_SYS key corresponding to ref. system 2.
		-procrustes: we might have data from procrustes transformation
		Hatt params:
		-from_hatt_id: for the NEW_BESSEL datum, the id of the 1:50000 hatt block (given by OKXE service) if ref. system 1 is a hattblock.
		-to_hatt_id: for the NEW_BESSEL datum the id of the 1:50000 hatt block if ref. system 2 is a hattblock.
		-okxe_inverse_type: for the NEW_BESSEL datum, if the okxe inverse transform will be iterative or use the respective inverse coefficients
		-from_hatt_centroid: for the OLD_BESSEL datum, a centroid for the hatt source projection
		-to_hatt_centroid: for the OLD_BESSEL datum, a centroid for the hatt destination projection
	'''

	def __init__(self, **params):
		self.transformers = []
		self.transformation_steps = []
		self.log = []

		# add hattblock objects to the parameters, needed in _compile function
		if 'from_hatt_id' in params:
			if 'from_srid' not in params: params['from_srid'] = HATT_NEW_SRID
			try:
				params['from_hattblock'] = Hattblock.objects.get(id=params['from_hatt_id'])
			except Hattblock.DoesNotExist:
				raise ValueError("Parameter Error: Hatt block with id=%d does not exist" % params['from_hatt_id'])

		if 'to_hatt_id' in params:
			if 'to_srid' not in params: params['to_srid'] = HATT_NEW_SRID
			try:
				params['to_hattblock'] = Hattblock.objects.get(id=params['to_hatt_id'])
			except Hattblock.DoesNotExist:
				raise ValueError('Parameter Error: Hatt block with id "%d" does not exist' % params['to_hatt_id'])

		is_procrustes = 'procrustes' in params and params['from_srid'] == PROCRUSTES_SRID and params['to_srid'] == PROCRUSTES_SRID
		if not is_procrustes:
			try:
				self._compile(**params)
			except KeyError as e:
				key = e.args[0]
				if key == 'from_hattblock':
					key = 'from_hatt_id'
				elif key == 'to_hattblock':
					key = 'to_hatt_id'
				raise ValueError('Parameter Error: "%s" parameter is required' % key)
		else:
			transformer = ProcrustesTransformer(params['procrustes'])
			self.transformers.append(transformer)
			self.log.append('Procrustes Transformation')
			if transformer.accuracy == float('inf'):
				self.transformation_steps.append("Μετασχηματισμός μέσω Προκρούστη. Άγνωστη ακρίβεια.")
			else:
				self.transformation_steps.append("Μετασχηματισμός μέσω Προκρούστη. Ακρίβεια ~ %s m." % round(transformer.accuracy,3))

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

			ggrs_new_bessel = (refsys1.datum == Datum.HGRS87 and refsys2.datum == Datum.NEW_BESSEL)
			ggrs_new_bessel |= (refsys1.datum == Datum.NEW_BESSEL and refsys2.datum == Datum.HGRS87)

			ggrs_ed50 = (refsys1.datum == Datum.HGRS87 and refsys2.datum == Datum.ED50)
			ggrs_ed50 |= (refsys1.datum == Datum.ED50 and refsys2.datum == Datum.HGRS87)
 			
			ggrs_wgs84 = (refsys1.datum == Datum.HGRS87 and refsys2.datum == Datum.WGS84)
			ggrs_wgs84 |= (refsys1.datum == Datum.WGS84 and refsys2.datum == Datum.HGRS87)

			ed50_wgs84 = (refsys1.datum == Datum.ED50 and refsys2.datum == Datum.WGS84)
			ed50_wgs84 |= (refsys1.datum == Datum.WGS84 and refsys2.datum == Datum.ED50)

			bessel_to_bessel = (refsys1.datum == Datum.NEW_BESSEL and refsys2.datum == Datum.OLD_BESSEL)
			bessel_to_bessel |= (refsys1.datum == Datum.OLD_BESSEL and refsys2.datum == Datum.NEW_BESSEL)
			
			if ggrs_htrs:
				return "Μετασχηματισμός %s μέσω διορθωτικών grid του Hepos. Ακρίβεια Οριζόντια ~ 0.05 m, Υψομετρική > 1 m" % (middle_text)
			elif ggrs_new_bessel: 
				return "Μετασχηματισμός %s μέσω πολυωνυμικών συντελεστών OKXE. Ακρίβεια ~ 0.10-0.15 m" % (middle_text)
			elif bessel_to_bessel:
				return "Μετασχηματισμός %s, θεωρητικά ίδιων datum αλλά άγνωστης ακρίβειας στην πράξη." % (middle_text)
			else:
				acc = "1" if ggrs_wgs84 else "5-10"
				return "Προσεγγιστικός μετασχηματισμός %s. Ακρίβεια ~ %s m" % (middle_text, acc)

	def _compile(self, **params):	
		from_srid = params['from_srid']
		to_srid = params['to_srid']

		# check if from-to ref. systems are the same (except if we are dealing with hatt blocks)
		# (compile can be recursive so we need this)
		if from_srid == to_srid:
			if from_srid != HATT_NEW_SRID and from_srid != HATT_OLD_SRID: #if both are NOT hatt
				return
			else: #if both are hattblocks
				if from_srid == HATT_NEW_SRID and params['from_hattblock'].id == params['to_hattblock'].id:
					return # end
				elif from_srid == HATT_OLD_SRID and params['from_hatt_centroid'] == params['to_hatt_centroid']:
					return # end

		srs1 = REF_SYS[from_srid]
		srs2 = REF_SYS[to_srid]
		# specialize proj4 definition for any of the reference systems that are hatt blocks
		if from_srid == HATT_NEW_SRID:
			srs1 = ReferenceSystem(name = '%s (%s)' % (srs1.name, params['from_hattblock'].name), 
						  datum = srs1.datum,
						  proj4text = params['from_hattblock'].proj4text)
		elif from_srid == HATT_OLD_SRID:
			phi0, lambda0 = params['from_hatt_centroid']
			srs1 = ReferenceSystem(name = '%s (Φο=%.2f, Λο=%.2f)' % (srs1.name, phi0, lambda0),
							datum = srs1.datum,
							proj4text = hatt_proj_text_generate(phi0, lambda0))

		if to_srid == HATT_NEW_SRID:
			srs2 = ReferenceSystem(name = '%s (%s)' % (srs2.name, params['to_hattblock'].name),
						  datum = srs2.datum,
						  proj4text = params['to_hattblock'].proj4text)
		elif to_srid == HATT_OLD_SRID:
			phi0, lambda0 = params['to_hatt_centroid']
			srs2 = ReferenceSystem(name = '%s (Φο=%.2f, Λο=%.2f)' % (srs2.name, phi0, lambda0),
							datum = srs2.datum,
							proj4text = hatt_proj_text_generate(phi0, lambda0))

		bessel_to_bessel = (srs1.datum == Datum.NEW_BESSEL and srs2.datum == Datum.OLD_BESSEL) or (srs1.datum == Datum.OLD_BESSEL and srs2.datum == Datum.NEW_BESSEL)

		# check if from-datum is the old greek (new bessel), so we can use OKXE transformation
		if not bessel_to_bessel and srs1.datum == Datum.NEW_BESSEL and srs2.datum != Datum.NEW_BESSEL:
			block = params['from_hattblock']
			# if not hatt projected ref. sys. but on greek datum... i.e. TM03 --> HATT
			if from_srid != HATT_NEW_SRID:
				self._compile(from_srid=from_srid, to_srid=HATT_NEW_SRID, to_hattblock=block) # using ProjTransformer
			# transform hatt to ggrs / greek grid
			self.transformers.append(OKXETransformer(block.get_coeffs(), inverse=False))
			self.log.append('%s (%s) --(OKXE)--> %s' % (REF_SYS[HATT_NEW_SRID].name, block.name, REF_SYS[TM87_SRID].name))
			self.transformation_steps.append(self._compute_tranform_accuracy(REF_SYS[HATT_NEW_SRID], REF_SYS[TM87_SRID]))
			# call recursively with ggrs / greek grid to srid
			self._compile(from_srid=TM87_SRID, to_srid=to_srid)
			return # end

		# check if target-datum is the old greek (new bessel), so we can use OKXE transformation
		if not bessel_to_bessel and srs1.datum != Datum.NEW_BESSEL and srs2.datum == Datum.NEW_BESSEL:
			block = params['to_hattblock']
			if 'okxe_inverse_type' in params:
				is_iterative_inverse = params['okxe_inverse_type'] == 'iterative'
			else:
				is_iterative_inverse = True #default
			# we need to transform from ggrs/greek grid to hatt so...we call recursively with ggrs / greek grid
			self._compile(from_srid=from_srid, to_srid=TM87_SRID)
			# and then transform from ggrs / greek grid to hatt map block
			self.transformers.append(OKXETransformer(block.get_coeffs(), inverse=True, iterative_inverse=is_iterative_inverse))
			self.log.append('%s --(OKXE)--> %s (%s) %s' % (REF_SYS[TM87_SRID].name, REF_SYS[HATT_NEW_SRID].name, block.name, "iter" if is_iterative_inverse else "coeffs"))
			self.transformation_steps.append(self._compute_tranform_accuracy(REF_SYS[TM87_SRID], REF_SYS[HATT_NEW_SRID]))
			# if to_srid is not hatt projected but in the old greek datum... i.e. TM03
			if to_srid != HATT_NEW_SRID:
				self._compile(from_srid=HATT_NEW_SRID, to_srid=to_srid, from_hattblock=block)
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
			params['from_srid'] = TM87_SRID
			self._compile(**params)
			return # end

		# check if target-datum is htrs 
		if srs1.datum != Datum.HTRS07 and srs2.datum == Datum.HTRS07:
			# transform from anywhere to greek grid
			params['to_srid'] = TM87_SRID
			self._compile(**params)
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
		x = np.asarray(x)
		y = np.asarray(y)
		if z is not None:
			z = np.asarray(z)

		if z is not None:
			for f in self.transformers:
				x, y, z = f(x, y, z)
		else:
			for f in self.transformers:
				x, y  = f(x, y)

		return tuple(filter(lambda array: array is not None, [x, y, z]))

	def log_str(self):
		return '\n'.join(list(self.log))
