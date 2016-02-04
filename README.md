# survgr  
A Python-2.7 Django-1.9 project for transforming coordinates between the various Coordinate Systems used in Greece.  
  
It is (will be for the time being) a website / web api for transforming earth point coordinates and other geometries between:  
    -GGRS87 / TM87 (EPSG:2100 and EPSG:4121 - http://spatialreference.org/ref/epsg/ggrs87-greek-grid/)  
    -Old Greek Datum (EPSG:4815 - http://spatialreference.org/ref/epsg/4815/)  
    -Various HATT (Old Greek Datum) projections using the published coefficients by OKXE (http://www.okxe.gr/el/)  
    -TM3 zone projections (Old Greek Datum)  
    -ED50 / UTM (EPSG:4230, EPSG:23034, EPSG:23035)  
    -WGS85 (EPSG:4326)  
    -The new HTRS07 / TM07 using the accurate transformation published by Hepos (http://www.hepos.gr/)  
  
The project can be run locally:  
    -Make an new python 2.7 virtual environment
    -Pip install the requirements  
    -Rename the survgr/local_settings.py.template to local_settings.py  
    -Django migrate to create a local sqlite db with some initial data
    -Run htrs/grd2bin script to compile the hepos binary grid file
    -Run tests  
