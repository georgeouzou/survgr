# survgr  
A django project for transforming coordinates between the various Coordinate Systems used in Greece.  
  
It is (will be for the time being) a website / web api for transforming earth point coordinates and other geometries between:  
* [GGRS87 / TM87 (EPSG:2100 and EPSG:4121)](http://spatialreference.org/ref/epsg/ggrs87-greek-grid/)
* [Old Greek Datum (EPSG:4815)](http://spatialreference.org/ref/epsg/4815/)  
* Various HATT projections with respect to the Old Greek Datum  using the published coefficients by [OKXE](http://www.okxe.gr/el/)  
* TM3 zone projections with respect to the Old Greek Datum  
* ED50 / UTM (EPSG:4230, EPSG:23034, EPSG:23035) 
* WGS84 (EPSG:4326)  
* The new HTRS07 / TM07 using the accurate transformation published by [Hepos](http://www.hepos.gr/)  

Prerequisites:
* You need to have python3 and virtualenv setup for backend

To install the project locally:  
* Make a fresh python 3 virtual environment
* `Pip install requirements.txt` for the back-end dependancies
* `python manage.py migrate` to create an sqlite db with some initial data
* Run `python manage.py test` for testing
* Run `python manage.py runserver` to run the server locally
