import csv
import numpy as np
import pandas as pd
from io import StringIO

def transform(transformer, fp, decimals=(3, 3, 3), fieldnames='x,y'):
	dialect = csv.Sniffer().sniff(fp.readline(), delimiters=";, \t")
	fp.seek(0)

	if dialect.delimiter in [' ', '\t']:
		sep = '\s+'
	else:
		sep = dialect.delimiter

	fieldnames = fieldnames.strip().split(',')
	field_dtype = {
		'id': str,
		'x': float,
		'y': float,
		'z': float
	}
	has_id = 'id' in fieldnames
	has_z = 'z' in fieldnames

	df = pd.read_csv(fp,
		sep=sep,
		names=fieldnames,
		dtype=field_dtype,
		index_col='id' if has_id else False,
		skipinitialspace=True,
		skip_blank_lines=True,
		decimal='.')

	if df.isna().values.any():
		raise ValueError('missing values')

	if has_z:
		coords = transformer(df['x'], df['y'], df['z'])
	else:
		coords = transformer(df['x'], df['y'])

	df['x'] = coords[0]
	df['y'] = coords[1]
	if has_z:
		df['z'] = coords[2]

	decx, decy, decz = decimals
	df['x'] = df['x'].map(lambda x: np.format_float_positional(x, decx))
	df['y'] = df['y'].map(lambda y: np.format_float_positional(y, decy))
	if has_z:
		df['z'] = df['z'].map(lambda z: np.format_float_positional(z, decz))

	output = StringIO()
	df.to_csv(output, sep=dialect.delimiter, header=False, index=has_id)
	output.seek(0)
	return output