################################################################################
#
# Version: 1.0
#
# Request a feature class from a arcgis rest api map service. Takes a URL and
# output feature class as input
#
# Author: https://github.com/jtgis
#
# Date: 19 mar 2021
#
################################################################################

import json
import arcpy
import requests
import tempfile
import shutil

url = "www.somemapserviceurl.com/1/query"

def downloadRestFeatures(url,queryLayer,query,outName):
    """
    #https://gis.stackexchange.com/questions/324513/converting-rest-service-to-file-geodatabase-feature-class
    can export a map service to fc optionally add a query or selection layer
    to limit ouput or leave those as "" to get the whole thing
    returns the new fc
    """
    #the parameters for the map service query
    if not query:
        query = '1=1'
    params = {'where': query, 'outFields': '*', 'f': 'pjson', 'returnGeometry': True}
    if queryLayer:
        spatial_ref = arcpy.Describe(queryLayer).spatialReference
        dissolved = arcpy.Dissolve_management(queryLayer,"dissolved")
        arcpy.AddGeometryAttributes_management(dissolved,"EXTENT")
        with arcpy.da.SearchCursor(dissolved, ["OID@", "EXT_MIN_X", "EXT_MIN_Y","EXT_MAX_X", "EXT_MAX_Y"]) as sCur:
            for row in sCur:
                minX, minY, maxX, maxY = row[1], row[2], row[3], row[4]
        extent = (str(minX) +","+ str(minY) +","+ str(maxX) +","+ str(maxY))
        params = {'where': query, 'geometry': extent, 'geometryType': 'esriGeometryEnvelope ', 'inSR': spatial_ref, 'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*', 'f': 'pjson', 'returnGeometry': True}
    #making the request
    r = requests.get(url, params)
    #read the data from the request to a json and write it to a file in a temp
    #directory
    data = r.json()
    dirpath = tempfile.mkdtemp()
    json_path = r"{}\mapService.json".format(dirpath)
    with open(json_path, 'w') as f:
        json.dump(data, f)
    f.close()
    r.close()
    #turn that json into a feature class!
    arcpy.JSONToFeatures_conversion(json_path,outName)
    shutil.rmtree(dirpath)
    
    return outName

tempFc = downloadRestFeatures(url,"","","in_memory/test")

print [f.name for f in arcpy.ListFields(tempFc)]
    
