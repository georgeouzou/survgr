import csv
from itertools import islice
from io import StringIO

def transform(transformer, fp, fieldnames='x,y', delimiter=','):
	fieldnames = fieldnames.strip().split(',')
	reader = csv.DictReader(fp, fieldnames=fieldnames, delimiter=delimiter, skipinitialspace=True)
	
	output = StringIO()
	writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore', delimiter=delimiter)

	# chucked reading of points
	while True:
		it = iter(reader)
		chunk = list(islice(it, 0, 20))
		if not chunk:
			break

		hasz = 'z' in fieldnames
		if hasz:
			coords = ((float(pt['x']), float(pt['y']), float(pt['z'])) for pt in chunk)
		else:
			coords = ((float(pt['x']), float(pt['y'])) for pt in chunk)

		coords = zip(*transformer(*zip(*coords)))
		
		for pt, c in zip(chunk, coords):
			pt['x'] = c[0]
			pt['y'] = c[1]
			if hasz:
				pt['z'] = c[2]

			writer.writerow(pt)

	output.seek(0)
	return output