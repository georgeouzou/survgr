import csv
import numpy as np
import re
from itertools import islice
from io import StringIO

def transform(transformer, fp, decimals=(3,3,3), fieldnames='x,y'):
	# read chunk of 1024 bytes
	file_chunk = fp.read(1024)
	# replace all multi-space occurencies with single space
	file_chunk = re.sub(' +', ' ', file_chunk)
	dialect = csv.Sniffer().sniff(file_chunk, delimiters=";, \t")
	fp.seek(0)

	fieldnames = fieldnames.strip().split(',')
	reader = csv.DictReader(fp, fieldnames=fieldnames, delimiter=dialect.delimiter, skipinitialspace=True, strict=True)
	
	output = StringIO()
	writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore', delimiter=dialect.delimiter)

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
