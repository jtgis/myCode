print("start script")

import arcpy
import os
from arcgis.gis import GIS
from datetime import datetime
arcpy.env.overwriteOutput = True

# Input Variables! #############################################################
rasterType = "TYPE OF RASTER DATA"
subArea = "CITY?"
area = "PROVINCE"
inputPolygons = r"INPUT POLY FEATURES"
inputPolyNameField = 'FIELD IN INPUT POLYS TO USE FOR NAMING'
detail = 16
templateAPRXFile = r"TEMPLATE APRX WITH ONE EMPTY MAP NAMED Map"
inputRasterLyr = r"LYR OR LYRX with RASTER DATA"
outputFolder = r"FOLDER TO DO THE WORK"
enableUploadToPortal = True

################################################################################

# Step 1 Create Temp APRX, add mosaic dataset, and save

aprx = arcpy.mp.ArcGISProject(templateAPRXFile)
aprx.saveACopy(r"{}\temp.aprx".format(outputFolder))
aprx = arcpy.mp.ArcGISProject(r"{}\temp.aprx".format(outputFolder))
map1 = aprx.listMaps("Map")[0]
lyrx1 = arcpy.mp.LayerFile(inputRasterLyr)
map1.addLayer(lyrx1)
map1.spatialReference = arcpy.SpatialReference(102100)
aprx.save()

# Step 2 Loop through poly features and create one tpkx per poly using raster

with arcpy.da.SearchCursor(inputPolygons,inputPolyNameField) as cursor:
    
    for row in cursor:

        print("starting {} at {}".format(row[0],datetime.now().strftime('%H:%M')))

        query = "{} = '{}'".format(inputPolyNameField,row[0])

        outTPKX = "{}\{}_{}_{}_{}.tpkx".format(outputFolder,rasterType,row[0],subArea,area)

        arcpy.MakeFeatureLayer_management(inputPolygons,"AREA",query)

        arcpy.management.CreateMapTilePackage(
            in_map=map1,
            service_type="ONLINE",
            output_file=outTPKX,
            format_type="MIXED",
            level_of_detail=detail,
            service_file=None,
            summary="",
            tags="",
            extent="DEFAULT",
            compression_quality=75,
            package_type="tpkx",
            min_level_of_detail=0,
            area_of_interest="AREA",
            create_multiple_packages=None,
            output_folder=None)

        print("finished {} at {}".format(row[0],datetime.now().strftime('%H:%M')))

# Step 3 upload TPKX to active Portal and delete temp tpkx file ################

        if enableUploadToPortal == True:

            gis = GIS("home")

            folder = 'TPKX {} {}, {}'.format(rasterType,subArea,area)

            try:
    
                gis.content.create_folder(folder)
    
            except:
    
                pass

            print("uploading {}".format(outTPKX))

            upload_properties={
                'title':'{} {}, {}, {}'.format(rasterType,row[0],subArea,area),
                'summary':'{} {}, {}, {}'.format(rasterType,row[0],subArea,area),
                'description':'{} {}, {}, {}'.format(rasterType,row[0],subArea,area),
                'tags':'{}, {}, {}, {}'.format(rasterType,row[0],subArea,area)}

            tpk_item = gis.content.add(
                item_properties=upload_properties,
                data=outTPKX,
                folder=folder)

            print("uploaded tpkx")

            os.remove(outTPKX)

        else:

            pass

os.remove(r"{}\temp.aprx".format(outputFolder))

print("finished script")

