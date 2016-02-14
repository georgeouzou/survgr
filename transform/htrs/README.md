# HTRS07

This module contains utility functions to enable tranformation between  
GGRS/Greek Grid (EPSG:2100) and the newest Greek Reference System called HTRS07/TM07.   
For more info see http://www.hepos.gr/.  

* grdfiles contain the ascii grd files contained in the free software HEPOS TRANSFORM.  
The grd files contain shifts by dEast and dNorth in cm.  

* grd2bin.py converts the grd ascii files to a binary hepos.grb file.  