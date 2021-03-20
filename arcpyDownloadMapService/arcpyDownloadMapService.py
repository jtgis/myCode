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

def downloadRestFeatures(url,outFC):
    """
    https://gis.stackexchange.com/questions/324513/converting-rest-service-to-file-geodatabase-feature-class
    Mostly from the link above but condensed into an easy function that takes a
    url and output name for a feature class and returns an in_memory feature 
    class from the service.
    Creates a temp dir that is later removed where the json file is stored before
    it becomes a feature class.
    """
    #the parameters for the map service query
    params = {'where': '1=1', 'outFields': '*', 'f': 'pjson', 'returnGeometry': True}
    #making the request
    r = requests.get(url, params)
    #read the data from the request to a json and write it to a file in a temp
    #directory
    data = r.json()
    dirpath = tempfile.mkdtemp()
    json_path = r"{}\mapService.json".format(dirpath)
    with open(json_path, 'w') as f:
        json.dump(data, f)
    #turn that json into a feature class!
    outFC = 'in_memory/{}'.format(outName)
    arcpy.JSONToFeatures_conversion(json_path,outFC)
    shutil.rmtree(dirpath)
    return outFC

tempFc = downloadRestFeatures(url,"in_memory/test")

print [f.name for f in arcpy.ListFields(tempFc)]
    
