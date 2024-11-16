# -*- coding: utf-8 -*-
from django.test import TestCase

from .models import Hattblock
from .okxe_transformer import OKXETransformer

class OKXETransformTest(TestCase):

    def setup(self):
        self.coeffs = [370552.68, 0.9997155, 0.0175123, -1.08e-09, 1.63e-09, 2.04e-09,\
        4511927.23, -0.0174755, 0.9996979, -6.50e-10, 5.60e-10, -1.65e-09]
        self.transformer = OKXETransformer(self.coeffs, inverse=False)
        self.inv_transformer = OKXETransformer(self.coeffs, inverse=True)

    def test_coeff_num(self):
        with self.assertRaises(IndexError):
            OKXETransformer([1]*9, inverse=False)
        with self.assertRaises(IndexError):
            OKXETransformer([1]*8, inverse=False)
        with self.assertRaises(IndexError):
            OKXETransformer([1]*12, inverse=True, iterative_inverse=False)

    def test_forward_func(self):
        self.setup()
        x1, y1 = (-16997.09, -14277.15)
        x2, y2 = self.transformer(x1, y1)

        self.assertEqual(round(x2,2), 353310.92)
        self.assertEqual(round(y2,2), 4497950.95)

    def test_inverse_func(self):
        self.setup()
        x1, y1 = (353310.92, 4497950.95)
        x2, y2 = self.inv_transformer(x1, y1)

        self.assertEqual(round(x2,2),-16997.09)
        self.assertEqual(round(y2,2),-14277.15)
            
    def test_inverse_coeffs(self):
        for i in range(Hattblock.objects.count()):
            hb = Hattblock.objects.get(id=i+1)
            fwd_transformer = OKXETransformer(hb.get_coeffs(), inverse=False, iterative_inverse=False)
            x, y = (1013, 1500)
            E, N = fwd_transformer(x, y)
            inv_transformer = OKXETransformer(hb.get_coeffs(), inverse=True, iterative_inverse=False)
            x1, y1 = inv_transformer(E, N)
            
            self.assertEqual(x, round(x1, 2))
            self.assertEqual(y, round(y1, 2))
            
        
class HattBlockTest(TestCase):

    def test_ids(self):
        hb = Hattblock.objects.get(id=1)
        self.assertEqual(hb.name, "Άβδηρα")
        hb = Hattblock.objects.get(id=126)
        self.assertEqual(hb.name, "Ίος")
        hb = Hattblock.objects.get(id=241)
        self.assertEqual(hb.name, "Νέον-Καρλοβάσιον")

    def test_coefficients(self):
        hb = Hattblock.objects.get(name='Άθως')
        coeffs = [497146.35, 0.9996218, 0.0004028, -1.70E-010, 2.60E-010, 2.70E-010,\
            4455299.91, -0.0003894, 0.99961, 1.60E-010, 1.30E-010, -2.70E-010]
        for i,j in zip(coeffs, hb.get_coeffs()):
            self.assertEqual(i, j)

        hb = Hattblock.objects.get(name='Ερυθραί')
        coeffs = [453315.02, 0.9996023, 0.0057615, -2.01E-009, 2.70E-010, -6.00E-011,\
            4233504.49, -0.005829, 0.9996627, -1.10E-009, 5.10E-010, -2.36E-009]
        for i,j in zip(coeffs, hb.get_coeffs()):
            self.assertEqual(i, j)

        hb = Hattblock.objects.get(name='Ψαχνά')
        coeffs = [453637.6, 0.9996193, 0.0058377, -6.50E-010, 5.90E-010, -1.00E-011,\
            4288980.93, -0.0058421, 0.9996147, 2.40E-010, -5.10E-010, -1.53E-009]
        for i,j in zip(coeffs, hb.get_coeffs()):
            self.assertEqual(i, j)

        hb = Hattblock.objects.get(name='Αλμυρός')
        coeffs = [1.0002212,-0.0114449,6.07E-10,-9.42E-10,-5.06E-10,\
            0.0114486,1.0002216,6.77E-10,-3.21E-10,1.70E-09]
        for i,j in zip(coeffs, hb.get_coeffs()[12:22]):
            self.assertEqual(i, j)