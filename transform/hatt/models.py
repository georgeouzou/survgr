from django.db import models

class Hattblock(models.Model):
	'''
	A Hatt map block. Each block can be used as a seperate,
	individually contained projected reference system.
	'''
	name = models.CharField(max_length=25)
	center_lon = models.FloatField() # center of the hatt block used to create projection
	center_lat = models.FloatField()
	geometry = models.CharField(max_length=255)

	# utility func create projection proj4 string
	@property
	def proj4text(self):
		return '+proj=aeqd +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs' %  (self.center_lat, self.center_lon)

	def get_coeffs(self):
		return self.okxecoefficient_set.order_by('type').values_list('value', flat=True)

	def __str__(self):
		return self.name

class OKXECoefficient(models.Model):
	'''
    Tranformation polynomial coefficients provided by OKXE service. 
    '''
	block = models.ForeignKey(Hattblock,on_delete=models.CASCADE)
	type = models.CharField(max_length=3) # can be from A0...A5 or B0...B5
	value = models.FloatField()

	def __str__(self):
		return '%s-%s: %e' % (self.block.name, self.type, self.value)
