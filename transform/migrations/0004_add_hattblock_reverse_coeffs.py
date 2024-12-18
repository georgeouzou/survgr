# Generated by Django 4.1.13 on 2024-11-09 17:36

import os
from django.db import migrations
import pandas as pd

def fill_reverse_coeffs(apps, schema_editor):
    cur_dir = os.path.dirname(__file__) #/migrations
    transform_dir = os.path.split(cur_dir)[0] #/transform

    field_names = ['okxe_id', 'name', 
                    'c1', 'c2', 'c3', 'c4', 'c5',
                    'd1', 'd2', 'd3', 'd4', 'd5']
    field_dtype = {
        field_names[0]: int,
        field_names[1]: str,
        field_names[2]: float,
        field_names[3]: float,
        field_names[4]: float,
        field_names[5]: float,
        field_names[6]: float,
        field_names[7]: float,
        field_names[8]: float,
        field_names[9]: float,
        field_names[10]: float,
        field_names[11]: float,
    }

    path = os.path.join(transform_dir, 'hatt', 'reverse_coeffs.csv')
    with open(path, 'r', encoding="utf8") as fd:
        OKXECoefficient = apps.get_model("transform", "OKXECoefficient")
        Hattblock = apps.get_model("transform", "Hattblock")
        df = pd.read_csv(fd,
                         sep=',',
                         names=field_names,
                         dtype=field_dtype,
                         decimal='.')

        coeffs = []
        for index, row in df.iterrows():
            hb = Hattblock.objects.get(id=index+1)
            assert(hb.okxe_id == row['okxe_id'])
            coeffs.append(OKXECoefficient(block=hb, type='C1', value=row['c1']))
            coeffs.append(OKXECoefficient(block=hb, type='C2', value=row['c2']))
            coeffs.append(OKXECoefficient(block=hb, type='C3', value=row['c3']))
            coeffs.append(OKXECoefficient(block=hb, type='C4', value=row['c4']))
            coeffs.append(OKXECoefficient(block=hb, type='C5', value=row['c5']))
            coeffs.append(OKXECoefficient(block=hb, type='D1', value=row['d1']))
            coeffs.append(OKXECoefficient(block=hb, type='D2', value=row['d2']))
            coeffs.append(OKXECoefficient(block=hb, type='D3', value=row['d3']))
            coeffs.append(OKXECoefficient(block=hb, type='D4', value=row['d4']))
            coeffs.append(OKXECoefficient(block=hb, type='D5', value=row['d5']))

        OKXECoefficient.objects.bulk_create(coeffs)

class Migration(migrations.Migration):

    dependencies = [
        ('transform', '0003_add_hatt_block_okxe_id'),
    ]

    operations = [
        migrations.RunPython(fill_reverse_coeffs)
    ]