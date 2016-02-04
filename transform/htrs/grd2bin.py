import os, struct
from grid import GridInfo

# This module converts to binary (grb) the text (grd) files
# contained in the free software HEPOS TRANSFORM
# see http://www.hepos.gr/

folder = os.path.dirname(__file__)
grb_path = os.path.join(folder, "hepos.grb")
grd_de_path = os.path.join(folder, "grdfiles", "dE_2km_V1-0.grd")
grd_dn_path = os.path.join(folder, "grdfiles", "dN_2km_V1-0.grd")
 
# grid
#
# | east -> west
# |    south 
# |      |
# |    north
# |	east -> west

with open(grd_de_path, 'r') as de:
	with open(grd_dn_path, 'r') as dn:
		with open(grb_path, 'wb') as grb:
			rows = int(de.readline()) # ys
			cols = int(de.readline()) # xs
			res = float(de.readline())
			min_y = float(de.readline())
			min_x = float(de.readline())

			for i in range(5):
				dn.readline()

			s = GridInfo.header_struct
			header = s.pack(rows, cols, res, min_x, min_y)
			grb.write(header)

			s = struct.Struct('f f')
			for line1, line2 in zip(de, dn):
				for val_de, val_dn in zip(line1.split(), line2.split()):
					grb.write(s.pack(float(val_de), float(val_dn)))