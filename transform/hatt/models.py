from django.contrib.gis.db import models

class Hattblock(models.Model):
	'''
	A Hatt map block. Each block can be used as a seperate,
	individually contained projected reference system.
	'''
	name = models.CharField(max_length=25)
	center_lon = models.FloatField() # center of the hatt block used to create projection
	center_lat = models.FloatField()
	geometry = models.PolygonField(srid=4815) # SRID:4815 = Greek Athens

	# override default objects manager to GIS objects manager 
	objects = models.GeoManager()

	# utility func create projection proj4 string
	@property
	def proj4text(self):
		return '+proj=aeqd +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=bessel +pm=athens +towgs84=456.387,372.620,496.818 +units=m +no_defs' %  (self.center_lat, self.center_lon)

	def __unicode__(self):
		return self.name

class OKXECoefficient(models.Model):
	'''
    Tranformation coefficients provided by OKXE service. 
    '''
	block = models.ForeignKey(Hattblock,on_delete=models.CASCADE)
	type = models.CharField(max_length=3)
	value = models.FloatField()
