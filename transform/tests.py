import json
from io import StringIO
import pandas as pd
import numpy as np
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

def round_list(l, dec):
    return [round(i, dec) for i in l]

def get_column(l2d, column):
    return list(zip(*l2d))[column]

class TransformWorkHorseTest(TestCase):

    def test_transformer_from_htrs07_tm07_to_hgrs87_tm87(self):
        # fwd
        params = {
            'from_srid':1000005, # htrs07 tm07
            'to_srid': 2100,     # hgrs87 tm87
        }
        t = WorkHorseTransformer(**params)
        E = [566446.108, 525000.011]
        N = [2529618.096, 2650967.938]
        h = [51.610, 172.591]
        Et, Nt, ht = t(E, N, h)
        self.assertEqual([round(v, 3) for v in Et], [566296.537, 524849.996])
        self.assertEqual([round(v, 3) for v in Nt], [4529332.307, 4650682.000])
        self.assertEqual([round(v, 3) for v in ht], [6.501, 123.000])

        # inverse
        params = {
            'from_srid': 2100, # hgrs87 tm87
            'to_srid':1000005, # htrs07 tm07
        }
        t = WorkHorseTransformer(**params)
        E = [566296.537, 524849.996]
        N = [4529332.307, 4650682.000]
        h = [6.501, 123.000]
        Et, Nt, ht = t(E, N, h)
        self.assertEqual([round(v, 3) for v in Et], [566446.108, 525000.011])
        self.assertEqual([round(v, 3) for v in Nt], [2529618.096, 2650967.938])
        self.assertEqual([round(v, 3) for v in ht], [51.610, 172.591])

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

    def test_transformer_approximate_between_hatt_wgs84(self):
        p0 = [
            [-10157.950, -21121.093],
            [-16090.967, -19478.049],
            [-2162.917,  -19596.748],
        ]
        p1 = [
            [22.348427556,40.560454368],
            [22.278332446,40.575158532],
            [22.442825451,40.574237399],
        ]

        params = {
            'from_hatt_id': '27',  # Alexandria
            'to_srid': 4326,       # wgs84
        }
        t = WorkHorseTransformer(**params)
        x, y = (get_column(p0, 0), get_column(p0, 1))
        lam, phi = t(x, y)
        # round to 5 decimals
        self.assertEqual(round_list(lam, 5), round_list(get_column(p1, 0), 5))
        self.assertEqual(round_list(phi, 5), round_list(get_column(p1, 1), 5))

        # inverse
        params = {
            'from_srid': 4326,   # wgs84
            'to_hatt_id': '27' # Alexandria
        }
        t = WorkHorseTransformer(**params)
        lam, phi = (get_column(p1, 0), get_column(p1, 1))
        x, y = t(lam, phi)
        # round to 1 meter
        self.assertEqual(round_list(x, 0), round_list(get_column(p0, 0), 0))
        self.assertEqual(round_list(y, 0), round_list(get_column(p0, 1), 0))

    def test_transformer_approximate_between_hatt_ed50(self):
        p0 = [
            [-10157.950, -21121.093],
            [-16090.967, -19478.049],
            [-2162.917,  -19596.748],
        ]
        p1 = [
            [22.349039642, 40.561875209],
            [22.278945936, 40.576579407],
            [22.443435951, 40.575657423],
        ]

        params = {
            'from_hatt_id': '27', # Alexandria
            'to_srid': 4230,      # ed50
        }
        t = WorkHorseTransformer(**params)
        x, y = (get_column(p0, 0), get_column(p0, 1))
        lam, phi = t(x, y)
        # round to 5 decimals
        self.assertEqual(round_list(lam, 5), round_list(get_column(p1, 0), 5))
        self.assertEqual(round_list(phi, 5), round_list(get_column(p1, 1), 5))

        # inverse
        params = {
            'from_srid': 4230,      # ed50
            'to_hatt_id': '27', # Alexandria
        }
        t = WorkHorseTransformer(**params)
        lam, phi = (get_column(p1, 0), get_column(p1, 1))
        x, y = t(lam, phi)
        # round to 1 meter
        self.assertEqual(round_list(x, 0), round_list(get_column(p0, 0), 0))
        self.assertEqual(round_list(y, 0), round_list(get_column(p0, 1), 0))

    def test_transformer_approximate_between_hgrs87_wgs84(self):
        p0 = [
            [273069.315, 4171340.811],
            [360028.79, 4490989.86],
            [354126.16, 4492735.79],
            [368047.90, 4492374.34],
            [357863.95, 4493264.94],
            [357133.34, 4494124.95],
            [370573.61, 4493899.90],
            [359019.22, 4494659.98],
            [361255.37, 4494828.49],
            [366895.56, 4494897.20],
            [356412.02, 4496626.27],
            [365136.21, 4497187.49],
            [361166.95, 4497382.23],
            [357953.56, 4497550.05],
            [353310.92, 4497950.95],
            [367458.81, 4497850.08],
        ]
        p1 = [
            [21.428909993,37.663839993],
            [22.348427505,40.560454352],
            [22.278332403,40.575158531],
            [22.442825432,40.574237378],
            [22.322355229,40.580573092],
            [22.313531731,40.588191744],
            [22.472342395,40.588374302],
            [22.335688331,40.593332843],
            [22.362067124,40.595227965],
            [22.428684375,40.596772539],
            [22.304442449,40.610591026],
            [22.407409741,40.617112627],
            [22.360460575,40.618209822],
            [22.322449041,40.619175600],
            [22.267492725,40.621975463],
            [22.434718217,40.623454808],
        ]
        params = {
            'from_srid' : 2100, # hgrs87
            'to_srid': 4326, # wgs84
        }
        t = WorkHorseTransformer(**params)
        x, y = (get_column(p0, 0), get_column(p0, 1))
        lam, phi = t(x, y)
        # round to 5 decimals
        self.assertEqual(round_list(lam, 5), round_list(get_column(p1, 0), 5))
        self.assertEqual(round_list(phi, 5), round_list(get_column(p1, 1), 5))

        params = {
            'from_srid': 4326, # wgs84
            'to_srid' : 2100, # hgrs87
        }
        lam, phi = (get_column(p1, 0), get_column(p1, 1))
        t = WorkHorseTransformer(**params)
        x, y = t(lam, phi)
        # round to 1 meter
        self.assertEqual(round_list(x, 0), round_list(get_column(p0, 0), 0))
        self.assertEqual(round_list(y, 0), round_list(get_column(p0, 1), 0))

    def test_transformer_approximate_between_hgrs87_ed50(self):
        p0 = [
            [273069.315, 4171340.811],
            [360028.79, 4490989.86],
            [354126.16, 4492735.79],
            [368047.90, 4492374.34],
            [357863.95, 4493264.94],
            [357133.34, 4494124.95],
            [370573.61, 4493899.90],
            [359019.22, 4494659.98],
            [361255.37, 4494828.49],
            [366895.56, 4494897.20],
            [356412.02, 4496626.27],
            [365136.21, 4497187.49],
            [361166.95, 4497382.23],
            [357953.56, 4497550.05],
            [353310.92, 4497950.95],
            [367458.81, 4497850.08],
        ]
        p1 = [
            [21.429513438,37.665327202],
            [22.349039591,40.561875193],
            [22.278945893,40.576579406],
            [22.443435932,40.575657402],
            [22.322967971,40.581993609],
            [22.314144702,40.589612132],
            [22.472952487,40.589793845],
            [22.336300948,40.594752995],
            [22.362679280,40.596647933],
            [22.429295336,40.598192119],
            [22.30505579, 40.612010946],
            [22.408021274,40.618531850],
            [22.361072969,40.619629269],
            [22.323062134,40.620595226],
            [22.26810684, 40.623395317],
            [22.435329312,40.624873740],
        ]

        params = {
            'from_srid' : 2100, # hgrs87
            'to_srid': 4230, # ed50
        }
        t = WorkHorseTransformer(**params)
        x, y = (get_column(p0, 0), get_column(p0, 1))
        lam, phi = t(x, y)
        # round to 5 decimals
        self.assertEqual(round_list(lam, 5), round_list(get_column(p1, 0), 5))
        self.assertEqual(round_list(phi, 5), round_list(get_column(p1, 1), 5))

        params = {
            'from_srid': 4230, # ed50
            'to_srid' : 2100, # hgrs87
        }
        lam, phi = (get_column(p1, 0), get_column(p1, 1))
        t = WorkHorseTransformer(**params)
        x, y = t(lam, phi)
        # round to 1 meter
        self.assertEqual(round_list(x, 0), round_list(get_column(p0, 0), 0))
        self.assertEqual(round_list(y, 0), round_list(get_column(p0, 1), 0))

    def test_transformer_approximate_between_hgrs87_ed50_utm34N(self):
            p0 = [
                [273069.315, 4171340.811],
                [360028.79, 4490989.86],
                [354126.16, 4492735.79],
                [368047.90, 4492374.34],
                [357863.95, 4493264.94],
                [357133.34, 4494124.95],
                [370573.61, 4493899.90],
                [359019.22, 4494659.98],
                [361255.37, 4494828.49],
                [366895.56, 4494897.20],
                [356412.02, 4496626.27],
                [365136.21, 4497187.49],
                [361166.95, 4497382.23],
                [357953.56, 4497550.05],
                [353310.92, 4497950.95],
                [367458.81, 4497850.08],
            ]
            p1 = [
                [537882.645,4168838.948],
                [614211.067,4491075.004],
                [608253.005,4492618.785],
                [622177.941,4492731.634],
                [611970.210,4493274.855],
                [611210.804,4494109.400],
                [624650.169,4494342.295],
                [613077.189,4494708.307],
                [615306.120,4494952.881],
                [620940.379,4495213.693],
                [610404.761,4496584.439],
                [619104.086,4497442.601],
                [615130.742,4497501.935],
                [611913.771,4497560.125],
                [607260.672,4497802.515],
                [621402.654,4498183.943],
            ]

            params = {
                'from_srid' : 2100, # hgrs87
                'to_srid': 23034, # ed50, utm34N
            }
            t = WorkHorseTransformer(**params)
            x, y = (get_column(p0, 0), get_column(p0, 1))
            xr, yr  = t(x, y)
            # round to 1 meter
            self.assertEqual(round_list(xr, 0), round_list(get_column(p1, 0), 0))
            self.assertEqual(round_list(yr, 0), round_list(get_column(p1, 1), 0))

            params = {
                'from_srid': 23034, # ed50, utm34N
                'to_srid' : 2100, # hgrs87
            }
            x, y = (get_column(p1, 0), get_column(p1, 1))
            t = WorkHorseTransformer(**params)
            xr, yr = t(x, y)
            # round to 1 meter
            self.assertEqual(round_list(xr, 0), round_list(get_column(p0, 0), 0))
            self.assertEqual(round_list(yr, 0), round_list(get_column(p0, 1), 0))

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

class TransformAPITestHattGGRS87(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.df_in = pd.DataFrame(data={
            'id': ['p11', '222', '333'],
            'x' : [-10157.950, -16090.967, -2162.917],
            'y' : [-21121.093, -19478.049, -19596.748],
        })
        cls.df_in.set_index('id', inplace=True)

        cls.df_expect = pd.DataFrame(data={
            'id': ['p11', '222', '333'],
            'x' : [360028.794, 354126.164, 368047.902],
            'y' : [4490989.862, 4492735.790, 4492374.342],
        })
        cls.df_expect.set_index('id', inplace=True)

    def test_csv_xy(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000000,  # hatt
                'to_srid': 2100,      # hgrs87 tm87
                'from_hatt_id': '27', # Alexandria
                'input_type': 'csv',
                'csv_fields': 'x,y',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['x','y'], header=False, index=False))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['x','y'], index_col=False)
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))

    def test_csv_yx(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000000,  # hatt
                'to_srid': 2100,      # hgrs87 tm87
                'from_hatt_id': '27', # Alexandria
                'input_type': 'csv',
                'csv_fields': 'y,x',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['y', 'x'], header=False, index=False))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['y','x'], index_col=False)
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))

    def test_csv_idxy(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000000,  # hatt
                'to_srid': 2100,      # hgrs87 tm87
                'from_hatt_id': '27', # Alexandria
                'input_type': 'csv',
                'csv_fields': 'id,x,y',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['x','y'], header=False, index=True))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['id','x','y'], index_col='id')
            self.assertTrue(np.array_equal(df_out.index, self.df_expect.index))
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))

    def test_csv_idyx(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000000,  # hatt
                'to_srid': 2100,      # hgrs87 tm87
                'from_hatt_id': '27', # Alexandria
                'input_type': 'csv',
                'csv_fields': 'id,y,x',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['y','x'], header=False, index=True))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['id','y','x'], index_col='id')
            self.assertTrue(np.array_equal(df_out.index, self.df_expect.index))
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))

    def test_geojson(self):
        num_rows = len(self.df_in.index)

        geojson_in = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [
                        self.df_in.iloc[i]['x'],
                        self.df_in.iloc[i]['y'],
                    ]
                    for i in range(num_rows)
                ]
            },
            'properties': {
                'name': 'Test Data',
            }
        }

        params = {
            'from_srid':1000000,  # hatt
            'to_srid': 2100,      # hgrs87 tm87
            'from_hatt_id': '27', # Alexandria
            'input_type': 'geojson',
            'input': StringIO(json.dumps(geojson_in))
        }

        response = self.client.post('/api/', params)
        output = response.json()
        self.assertTrue('result' in output)

        geojson_out = output['result']
        self.assertTrue('properties' in geojson_out)
        geom = geojson_out['geometry']

        for i in range(num_rows):
            self.assertTrue(abs(geom['coordinates'][i][0] -
                self.df_expect.iloc[i]['x']) < 0.001)
            self.assertTrue(abs(geom['coordinates'][i][1] -
                self.df_expect.iloc[i]['y']) < 0.001)

class TransformAPITestHTRS07GGRS87(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.df_in = pd.DataFrame(data={
            'id': ['s1', 's2'],
            'x' : [566446.108, 525000.011],
            'y' : [2529618.096, 2650967.938],
            'z' : [51.610, 172.591]
        })
        cls.df_in.set_index('id', inplace=True)

        cls.df_expect = pd.DataFrame(data={
            'id': ['s1', 's2'],
            'x' : [566296.537, 524849.996],
            'y' : [4529332.307, 4650682.000],
            'z' : [6.501, 123.000],
        })
        cls.df_expect.set_index('id', inplace=True)

    def test_csv_xyz(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000005, # htrs07 tm07
                'to_srid': 2100,     # hgrs87 tm87
                'input_type': 'csv',
                'csv_fields': 'x,y,z',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['x','y','z'], header=False, index=False))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['x','y','z'], index_col=False)
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))
            self.assertTrue(np.array_equal(df_out['z'], self.df_expect['z']))

    def test_csv_yxz(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000005, # htrs07 tm07
                'to_srid': 2100,     # hgrs87 tm87
                'input_type': 'csv',
                'csv_fields': 'y,x,z',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['y', 'x', 'z'], header=False, index=False))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['y','x','z'], index_col=False)
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))
            self.assertTrue(np.array_equal(df_out['z'], self.df_expect['z']))

    def test_csv_idxyz(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000005, # htrs07 tm07
                'to_srid': 2100,     # hgrs87 tm87
                'input_type': 'csv',
                'csv_fields': 'id,x,y,z',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['x','y','z'], header=False, index=True))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['id','x','y','z'], index_col='id')
            self.assertTrue(np.array_equal(df_out.index, self.df_expect.index))
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))
            self.assertTrue(np.array_equal(df_out['z'], self.df_expect['z']))

    def test_csv_idyxz(self):
        for sep in [',', ', ', ';', '\t', ' ']:
            sep_with_space = sep == ', '
            if sep_with_space:
                sep = ','

            params = {
                'from_srid':1000005, # htrs07 tm07
                'to_srid': 2100,     # hgrs87 tm87
                'input_type': 'csv',
                'csv_fields': 'id,y,x,z',
                'input': StringIO(self.df_in.to_csv(sep=sep, columns=['y','x','z'], header=False, index=True))
            }
            if sep_with_space:
                params['input'] = StringIO(params['input'].read().replace(',', ', '))

            response = self.client.post('/api/', params)
            output = response.json()
            self.assertTrue('result' in output)
            df_out = pd.read_csv(StringIO(output['result']), sep=sep, names=['id','y','x','z'], index_col='id')
            self.assertTrue(np.array_equal(df_out.index, self.df_expect.index))
            self.assertTrue(np.array_equal(df_out['x'], self.df_expect['x']))
            self.assertTrue(np.array_equal(df_out['y'], self.df_expect['y']))
            self.assertTrue(np.array_equal(df_out['z'], self.df_expect['z']))

    def test_geojson(self):
        num_rows = len(self.df_in.index)

        geojson_in = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [
                        self.df_in.iloc[i]['x'],
                        self.df_in.iloc[i]['y'],
                        self.df_in.iloc[i]['z'],
                    ]
                    for i in range(num_rows)
                ]
            },
            'properties': {
                'name': 'Test Data',
            }
        }

        params = {
            'from_srid':1000005, # htrs07 tm07
            'to_srid': 2100,     # hgrs87 tm87
            'input_type': 'geojson',
            'input': StringIO(json.dumps(geojson_in))
        }

        response = self.client.post('/api/', params)
        output = response.json()
        self.assertTrue('result' in output)

        geojson_out = output['result']
        self.assertTrue('properties' in geojson_out)
        geom = geojson_out['geometry']

        for i in range(num_rows):
            self.assertTrue(abs(geom['coordinates'][i][0] -
                self.df_expect.iloc[i]['x']) < 0.001)
            self.assertTrue(abs(geom['coordinates'][i][1] -
                self.df_expect.iloc[i]['y']) < 0.001)
            self.assertTrue(abs(geom['coordinates'][i][2] -
                self.df_expect.iloc[i]['z']) < 0.001)

