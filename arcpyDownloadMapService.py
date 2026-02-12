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

url = "www.somemapserviceurl.com/1"

def downloadRestFeatures(url,queryLayer,query,outLocation,outName):
    
    """
    #https://gis.stackexchange.com/questions/324513/converting-rest-service-to-file-geodatabase-feature-class
    can export a map service to fc optionally add a query or selection layer
    to limit ouput or leave those as "" to get the whole thing
    returns the new fc
    """

    if not query:
        query = '1=1'
    
    data1 = requests.get("{}/query".format(url), {"where": query,
                                                  "f": "json",
                                                  "returnCountOnly": True}).json()
    
    print(data1['count'])
               
    data2 = requests.get("{}/query".format(url), {"where": query,
                                                  "f": "json",
                                                  "returnIdsOnly": True}).json()
    
    oidList = data2['objectIds']
    
    oidFieldName = data2['objectIdFieldName']
               
    data3 = requests.get(url, {"where": query,
                               "f": "json",
                               "returnIdsOnly": True}).json()

    n = data3['maxRecordCount']

    print(n)

    oidList.sort()
    
    list_of_groups = izip_longest(*(iter(oidList),) * n)
    
    x=1
    
    for group in list_of_groups:

        time.sleep(2)
        
        print(x)
        
        x=x+1
        
        group = [i for i in group if i is not None]

        firstNUMB = group[0]
        
        lastNUMB = group[-1]
        
        queryParam = '{} BETWEEN {} AND {}'.format(oidFieldName,firstNUMB,lastNUMB)
        
        params = {'where': queryParam,
                  'outFields': '*',
                  'f': 'pjson',
                  'returnGeometry': True}
        
        if queryLayer:
            
            spatial_ref = arcpy.Describe(queryLayer).spatialReference
            
            dissolved = arcpy.Dissolve_management(queryLayer,"dissolved")
            
            arcpy.AddGeometryAttributes_management(dissolved,
                                                   "EXTENT")
            
            with arcpy.da.SearchCursor(dissolved, ["OID@", "EXT_MIN_X", "EXT_MIN_Y","EXT_MAX_X", "EXT_MAX_Y"]) as sCur:
                
                for row in sCur:
                    
                    minX, minY, maxX, maxY = row[1], row[2], row[3], row[4]
                    
            extent = (str(minX) +","+ str(minY) +","+ str(maxX) +","+ str(maxY))
            
            params = {'where': queryParam,
                      'geometry': extent,
                      'geometryType':
                      'esriGeometryEnvelope ',
                      'inSR': spatial_ref,
                      'spatialRel':
                      'esriSpatialRelIntersects',
                      'outFields': '*',
                      'f': 'pjson',
                      'returnGeometry': True}
            
        r = requests.get("{}/query".format(url), params)
        
        data = r.json()
        
        dirpath = tempfile.mkdtemp()
        
        json_path = r"{}\mapService.json".format(dirpath)
        
        with open(json_path, 'w') as f:
            json.dump(data, f)
        f.close()
        r.close()
        
        arcpy.JSONToFeatures_conversion(json_path,
                                        "in_memory/singleFeature")

        if arcpy.Exists("in_memory/allFeatures"):
            arcpy.management.Append(["in_memory/singleFeature"],
                                    "in_memory/allFeatures","TEST")
        else:
            arcpy.conversion.FeatureClassToFeatureClass("in_memory/singleFeature",
                                                        "in_memory",
                                                        "allFeatures")

        arcpy.Delete_management("in_memory/singleFeature")

    arcpy.conversion.FeatureClassToFeatureClass("in_memory/allFeatures",
                                                outLocation,outName)

    shutil.rmtree(dirpath)
    arcpy.Delete_management("in_memory/allFeatures")
        
    return "{}\{}".format(outLocation,outName)

tempFc = downloadRestFeatures(url,"","","in_memory","test")

print [f.name for f in arcpy.ListFields(tempFc)]
    
