################################################################################
#
# purpose: calculate volumes from polygon boundaries
#
# author: jtgis
#
# date: 07 may 2020
#
# edits:
#
################################################################################
import arcpy
import os

def calcVolumeBtwnSurfaces(inputdem,inputdsm,inputpolygons):
    
    arcpy.CopyFeatures_management(inputpolygons,
                                "in_memory/poly")

    arcpy.AddField_management("in_memory/poly",
                            "GROSS_M3",
                            "DOUBLE")

    arcpy.AddField_management("in_memory/poly",
                              "NET_M3",
                              "DOUBLE")

    field_names = [f.name for f in arcpy.ListFields("in_memory/poly")]

    with arcpy.da.SearchCursor("in_memory/poly",[field_names[0]]) as cursor:
        for row in cursor:

            i = row[0]

            print(i)

            arcpy.Select_analysis("in_memory/poly",
                                  "in_memory/poly",
                                  field_names[0] +" = "+str(cursor[0])+"")

            rastList = [[inputdem,"in_memory/dembottom"],
                        [inputdsm,"in_memory/demtop"]]

            for f in rastList:
                arcpy.gp.ExtractByMask_sa(f[0],
                                          "in_memory/poly",
                                          f[1])
            
            arcpy.CutFill_3d("in_memory/demtop",
                            "in_memory/dembottom",
                            "in_memory/results",
                            "1")

            volume = 0

            with arcpy.da.SearchCursor("in_memory/results",["VOLUME"]) as cursor1:
                for row1 in cursor1:
                    if row1[0] > 0:
                        volume = volume + row1[0]

            with arcpy.da.UpdateCursor("in_memory/poly",[field_names[0],"PERCENT","GROSS_M3","NET_M3"]) as cursor2:
                for row2 in cursor2:
                    if str(row2[0]) == str(i):
                        arcpy.AddMessage(volume)
                        row2[2] = round(volume)
                        try:
                            row2[3] = round(volume * row2[1]/100)
                        except:
                            pass
                        cursor2.updateRow(row2)

    return "in_memory/poly"

if __name__ == '__main__':

    inputpolygons = arcpy.GetParameterAsText(0)
    inputdem = arcpy.GetParameterAsText(1)
    inputdsm = arcpy.GetParameterAsText(2)
    outputfolder = arcpy.GetParameterAsText(3)

    arcpy.env.overwriteOutput = True

    arcpy.Delete_management("in_memory")

    outPolys = calcVolumeBtwnSurfaces(inputdem,inputdsm,inputpolygons)

    outName = os.path.splitext(os.path.basename(inputpolygons))[0]

    arcpy.CopyFeatures_management(outPolys,
                                  outputfolder + "/"+outName+"_pilevolumes.shp")
