import csv
import numpy as np
from itertools import islice
from io import StringIO

def transform(transformer, fp, decimals=(3,3,3), fieldnames='x,y', delimiter=','):
	fieldnames = fieldnames.strip().split(',')
	reader = csv.DictReader(fp, fieldnames=fieldnames, delimiter=delimiter, skipinitialspace=True)
	
	output = StringIO()
	writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore', delimiter=delimiter)

	hasz = 'z' in fieldnames
	decx, decy, decz = decimals

	# reading points in chunks of 32
	while chunk := list(islice(reader, 0, 32)):
		if hasz:
			coords = [(float(pt['x']), float(pt['y']), float(pt['z'])) for pt in chunk]
		else:
			coords = [(float(pt['x']), float(pt['y'])) for pt in chunk]

		coords = zip(*transformer(*zip(*coords)))
		
		# replace x,y,z in chunk with transformed values
		for pt, c in zip(chunk, coords):
			pt['x'] = np.format_float_positional(c[0], decx)
			pt['y'] = np.format_float_positional(c[1], decy)
			if hasz:
				pt['z'] = np.format_float_positional(c[2], decz)

			writer.writerow(pt)

	output.seek(0)
	return output
