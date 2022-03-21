import json
from django.test import TestCase
from .transform import WorkHorseTransformer

def dms2decdeg(d, m, s):
    sign = 1.0 if d > 0.0 else -1.0
    return sign * (abs(d) + m/60.0 + s/3600.0)

def decdeg2dms(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600.0,60.0)
    degrees,minutes = divmod(minutes,60.0)
    degrees = degrees if is_positive else -degrees
    return (degrees,minutes,seconds)

class TransformAPITest(TestCase):
    def test_transformer_from_htrs07_tm07_to_hgrs87_tm87(self):
        # fwd
        params = {
            'from_srid':1000005, # htrs07 tm07
            'to_srid': 2100,     # hgrs87 tm87
        }
        t = WorkHorseTransformer(**params)
        E = [566446.108]
        N = [2529618.096]
        h = [51.610]
        Et, Nt, ht = t(E, N, h)
        self.assertEqual(round(Et[0], 3), 566296.538)
        self.assertEqual(round(Nt[0], 3), 4529332.307)
        self.assertEqual(round(ht[0], 3), 6.501)

        # inverse
        params = {
            'from_srid': 2100, # hgrs87 tm87
            'to_srid':1000005, # htrs07 tm07
        }
        t = WorkHorseTransformer(**params)
        E = [566296.538]
        N = [4529332.307]
        h = [6.501]
        Et, Nt, ht = t(E, N, h)
        self.assertEqual(round(Et[0], 3), 566446.108)
        self.assertEqual(round(Nt[0], 3), 2529618.096)
        self.assertEqual(round(ht[0], 3), 51.610)

    def test_transformer_between_old_greek_and_old_greek_tm3(self):
        # fotiou 10.6
        params = {
            'from_srid': 1000001, # old greek, tm3 west zone
            'to_srid': 4815       # old greek
        }
        E = [328004.136]
        N = [423370.927]
        t = WorkHorseTransformer(**params)
        lam, phi = t(E, N)
        self.assertEqual(tuple(round(v, 4) for v in decdeg2dms(lam[0])), (-1.0, 32.0, 46.1233))
        self.assertEqual(tuple(round(v, 4) for v in decdeg2dms(phi[0])), (37.0, 48.0, 26.7492))

        params = {
            'from_srid': 1000003, # old greek, tm3 east zone
            'to_srid': 1000002,   # old greek, tm3 central zone
        }
        E = [102548.140]
        N = [707555.52]
        t = WorkHorseTransformer(**params)
        Et, Nt= t(E, N)
        self.assertEqual(round(Et[0], 3), 357287.091)
        self.assertEqual(round(Nt[0], 3), 708570.434)

    def test_transformer_between_hgrs87_and_hgrs87_tm87(self):
        # fotiou 10.7
        params = {
            'from_srid': 2100,  # hgrs87, tm87
            'to_srid': 4121     # hgrs87
        }
        E = [210057.870]
        N = [4356213.327]
        t = WorkHorseTransformer(**params)
        lam, phi = t(E, N)
        self.assertEqual(tuple(round(v, 5) for v in decdeg2dms(lam[0])), (20.0, 38.0, 14.76414))
        self.assertEqual(tuple(round(v, 5) for v in decdeg2dms(phi[0])), (39.0, 18.0, 24.37895))

        # inverse
        params = {
            'from_srid': 4121, # hgrs87
            'to_srid': 2100,   # hgrs87, tm87
        }
        lam = [dms2decdeg(20.0, 38.0, 14.76414)]
        phi = [dms2decdeg(39.0, 18.0, 24.37895)]
        t = WorkHorseTransformer(**params)
        E, N = t(lam, phi)
        self.assertEqual(round(E[0], 3), 210057.870)
        self.assertEqual(round(N[0], 3), 4356213.327)
    
    def test_transformer_between_ed50_utm_zones(self):
        # fotiou 10.8
        params = {
            'from_srid': 23034,  # utm zone 34
            'to_srid': 23035     # utm zone 35
        }
        E = [755283.165]
        N = [4016626.161]
        t = WorkHorseTransformer(**params)
        Et, Nt = t(E, N)
        self.assertEqual(round(Et[0], 3), 216200.724)
        self.assertEqual(round(Nt[0], 3), 4017510.079)

    def test_transformer_between_old_greek_grid_and_hgrs87(self):
        # Fotiou 
        params = {
            'from_srid': 1000000, # hatt
            'to_srid': 2100,      # hgrs87, tm87
            'from_hatt_id': '185' # Lamia
        }
        t = WorkHorseTransformer(**params)
        E = [1218.087, -4491.058, -2713.483, -4800.243, -4335.586, -2014.599]
        N = [16209.281, 16803.183, 17432.541, 18089.393, 20388.192, 21378.062]
        x, y = t(E, N)
        self.assertEqual(list(round(v, 3) for v in x), [368236.734, 362539.287, 364326.931, 362251.821, 362755.013, 365092.002])
        #self.assertEqual(list(round(v, 3) for v in y), [4306147.681, 4306837.383, 4307436.674, 4308128.472, 4310418.872, 4311369.406])

        # Kotsakis
        xt = [
            -10157.950,
            -16090.967,
            -2162.917,
            -12362.440,
            -13108.037,
            336.201,
            -11231.498,
            -8998.309,
            -3359.300,
            -13872.954,
            -5158.639,
            -9131.276,
            -12347.558,
            -16997.088,
            -2847.613,
        ]
        yt = [ 
            -21121.093,
            -19478.049,
            -19596.748,
            -18883.749,
            -18036.475,
            -18027.094,
            -17468.572,
            -17261.061,
            -17093.966,
            -15547.749,
            -14834.349,
            -14708.860,
            -14597.090,
            -14277.153,
            -14131.222,
        ]
        Et = [
            360028.79,
            354126.16,
            368047.90,
            357863.95,
            357133.34,
            370573.61,
            359019.22,
            361255.37,
            366895.56,
            356412.02,
            365136.21,
            361166.95,
            357953.56,
            353310.92,
            367458.81,
        ]
        Nt = [
            4490989.86,
            4492735.79,
            4492374.34,
            4493264.94,
            4494124.95,
            4493899.90,
            4494659.98,
            4494828.49,
            4494897.20,
            4496626.27,
            4497187.49,
            4497382.23,
            4497550.05,
            4497950.95,
            4497850.08,
        ]

        # fwd
        params = {
            'from_srid': 1000000, # hatt
            'to_srid': 2100,      # hgrs87, tm87
            'from_hatt_id': '27' # Alexandria
        }
        t = WorkHorseTransformer(**params)
        E, N = t(xt, yt)
        self.assertEqual(list(round(v, 2) for v in E), Et)
        self.assertEqual(list(round(v, 2) for v in N), Nt)
        
        # inverse
        params = {
            'from_srid': 2100,      # hgrs87, tm87
            'to_srid': 1000000, # hatt
            'to_hatt_id': '27' # Alexandria
        }
        t = WorkHorseTransformer(**params)
        x, y = t(E, N)
        self.assertEqual(list(round(v, 3) for v in x), xt)
        self.assertEqual(list(round(v, 3) for v in y), yt)
    
    def test_approximate_transforms(self):
        # hatt - wgs84
        x = [-10157.950, -16090.967, -2162.917]
        y = [-21121.093, -19478.049, -19596.748]

        params = {
            'from_srid': 1000000, # hatt
            'to_srid': 4326,      # hgrs87, tm87
            'from_hatt_id': '27' # Alexandria
        }
        t = WorkHorseTransformer(**params)
        lam, phi = t(x, y)
        self.assertEqual(list(round(v, 6) for v in lam), [22.348428, 22.278332, 22.442825])
        self.assertEqual(list(round(v, 6) for v in phi), [40.560454, 40.575159, 40.574237])

        # hatt - ed50
        params = {
            'from_srid': 1000000, # hatt
            'to_srid': 4230,      # ed50
            'from_hatt_id': '27' # Alexandria
        }
        t = WorkHorseTransformer(**params)
        lam, phi = t(x, y)
        self.assertEqual(list(round(v, 6) for v in lam), [22.349040, 22.278946, 22.443436])
        self.assertEqual(list(round(v, 6) for v in phi), [40.561875, 40.576579, 40.575657])

    def test_transformer_compile(self):
        HATT_SRID = 1000000
        GGRS_SRID = 2100
        with self.assertRaises(ValueError):
            horse = WorkHorseTransformer(from_srid=HATT_SRID)
        with self.assertRaises(ValueError):
            horse = WorkHorseTransformer(to_srid=HATT_SRID)
        with self.assertRaises(ValueError):
            horse = WorkHorseTransformer(from_hatt_id=-10, to_srid=GGRS_SRID)
        with self.assertRaises(ValueError):
            horse = WorkHorseTransformer(from_srid=HATT_SRID, to_srid=GGRS_SRID)
        with self.assertRaises(ValueError):
            horse = WorkHorseTransformer(from_srid=GGRS_SRID, to_srid=HATT_SRID)

        horse = WorkHorseTransformer(from_srid=GGRS_SRID, to_srid=HATT_SRID, to_hatt_id=2)



    # def test_transform_features(self):
    #       params = {
    #               'from_srid': 1000005, # HTRS07 geocentric
    #               'to_srid': 2100 # GGRS87/TM87
    #       }

    #       data = {
    #               "type": "FeatureCollection",
    #               "features": [
    #               {
    #                       'type':'Feature',
    #                       'geometry':{
    #                               'type':'Point',
    #                               'coordinates':[566446.108, 2529618.096]
    #                       },
    #                       'properties':{'name': 's1'}
    #               },
    #               {
    #                       'type':'Feature',
    #                       'geometry':{
    #                               'type':'Linestring',
    #                               'coordinates':[[566446.108, 2529618.096],[566450.555, 2529690.1]]
    #                       },
    #                       'properties':{'name': 's2'}
    #               },
    #               {
    #                       'type':'Feature',
    #                       'geometry':{
    #                               'type':'Polygon',
    #                               'coordinates':[[
    #                                                               [566446.108, 2529618.096],[566450.555, 2529690.1],
    #                                                               [566458.200, 2529620.100],[566446.108, 2529618.096]
    #                                                         ]]
    #                       },
    #                       'properties':{'name': 's3'}
    #               }]
    #       }

    #       response = self.client.post('/transform/api/',
    #                                                               data=json.dumps({'params':params,'data':data}),
    #                                                               content_type='application/json')

    #       self.assertTrue(response.json()['status'] == 'ok')
