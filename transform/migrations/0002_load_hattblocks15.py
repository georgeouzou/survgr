# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-22 15:28
from __future__ import unicode_literals
import os, json

from django.db import migrations
from django.contrib.gis.geos import GEOSGeometry

def load(apps, schema_editor):
	Hattblock = apps.get_model("transform", "Hattblock")
	OKXECoefficient = apps.get_model("transform", "OKXECoefficient")
	
	cur_dir = os.path.dirname(__file__) #/migrations
	transform_dir = os.path.split(cur_dir)[0] #/transform

	with open(os.path.join(transform_dir, 'hatt', 'hattblocks15.json'),'r') as fd:
		hattblocks = []
		coeffs = []
		for chunk in json.load(fd):
			hb = Hattblock(
				id=chunk['id'],
				name=chunk['name'],
				center_lon=chunk['cx'],
				center_lat=chunk['cy'],
				geometry=GEOSGeometry(json.dumps(chunk['geom']))
			)
			hattblocks.append(hb)
			for ctype, cvalue in chunk['okxe_coeffs'].iteritems():
				coeffs.append(OKXECoefficient(block=hb,type=ctype,value=cvalue))

		Hattblock.objects.bulk_create(hattblocks)
   		OKXECoefficient.objects.bulk_create(coeffs)

class Migration(migrations.Migration):

    dependencies = [
        ('transform', '0001_initial'),
    ]

    operations = [
    	migrations.RunPython(load)
    ]


