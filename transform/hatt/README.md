This module contains utility functions to enable tranformation between  
GGRS/Greek Grid (EPSG:2100) and the various HATT projections on the Old Greek  
Datum using the published polynomial coefficients by OKXE (http://www.okxe.gr/el/).  

-- hattblocks15.json file contain hattblock information, geometry and the okxe  
coefficients published for each block. These are stored to the database when initializing  the project. The geometries are with respect to the  geodetic Old Greek Datum reference   system (EPSG:4815).