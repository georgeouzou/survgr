import csv
from itertools import islice
from io import StringIO

def transform(transformer, fp, **fmtparams):
	fieldnames = fmtparams['csv_fields']
	reader = csv.DictReader(fp, fieldnames=fieldnames, delimiter=fmtparams['csv_delimiter'], skipinitialspace=True)
	output = StringIO()
	writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore', delimiter=fmtparams['csv_delimiter'])

	# chucked reading of points
	while True:
		it = iter(reader)
		chunk = list(islice(it, 0, 20))
		if not chunk:
			break

		print(chunk)

		hasz = 'z' in fieldnames
		if hasz:
			coords = ((float(pt['x']), float(pt['y']), float(pt['z'])) for pt in chunk)
		else:
			coords = ((float(pt['x']), float(pt['y'])) for pt in chunk)

		coords = zip(*transformer(*zip(*coords)))
		
		for pt, c in zip(chunk, coords):
			pt['x'] = round(c[0],4)
			pt['y'] = round(c[1],4)
			if hasz:
				pt['z'] = round(c[2], 4)

			writer.writerow(pt)

	output.seek(0)
	return output