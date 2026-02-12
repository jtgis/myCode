################################################################################
#
# Version: 1.0
#
# The purpose of this tool is to add the erase geoprocessing tool to the Arcmap 
# Basic license level. Tested and developed using ArcMap Desktop Basic 10.5.1 
# and Python 2.7.
#
# Author: https://github.com/jtgis
#
# Date: 18 June 2019
#
################################################################################

import arcpy

def erase(input_features,erase_features,output_feature_class):
    """
    Works by UNIONing the two input feature classes, SELECTing the created
    features that do not overlap with the erase_features using the 
    "erasefeaturesname_FID", and then CLIPping the original input_features to 
    include just those features. If either input_features or erase_features is 
    not a polygon it will be BUFFERed to a polygon prior to the union.
    """
    arcpy.AddMessage("BEGINNING ERASE PROCESS...")

    arcpy.Delete_management("in_memory")

    attr = erase_features.split('/')[-1]

    desc =arcpy.Describe(input_features)

    if desc.shapeType != 'Polygon':
        arcpy.AddMessage("BUFFERING INPUT FEATURES TO POLYGON...")
        arcpy.Buffer_analysis(in_features=input_features, 
                            out_feature_class="in_memory/buffered", 
                            buffer_distance_or_field="0.25 Meters")
        arcpy.AddMessage("INPUT FEATURES BUFFERED")

    desc =arcpy.Describe(erase_features)

    if desc.shapeType != 'Polygon':
        arcpy.AddMessage("BUFFERING ERASE FEATURES TO POLYGON...")
        arcpy.Buffer_analysis(in_features=erase_features, 
                            out_feature_class="in_memory/erase_buffered", 
                            buffer_distance_or_field="0.25 Meters")
        erase_features = "in_memory/erase_buffered"
        attr = erase_features.split('/')[-1]
        arcpy.AddMessage("ERASE FEATURES BUFFERED")

    arcpy.AddMessage("UNIONING...")
    arcpy.Union_analysis(in_features=["in_memory/buffered",erase_features], 
                        out_feature_class="in_memory/unioned")
    arcpy.AddMessage("UNIONED")

    arcpy.AddMessage("SELECTING...")
    arcpy.Select_analysis(in_features="in_memory/unioned", 
                        out_feature_class="in_memory/selected", 
                        where_clause="FID_"+attr+" = -1")
    arcpy.AddMessage("SELECTED")

    arcpy.AddMessage("CLIPPING...")
    arcpy.Clip_analysis(in_features=input_features, 
                        clip_features="in_memory/selected", 
                        out_feature_class=output_feature_class)
    arcpy.AddMessage("CLIPPED")

    arcpy.AddMessage("ERASED")

if __name__ == '__main__':
    """
    Accept feature classes as input from ArcMap Toolbox Script Tool
    """
    input_features = arcpy.GetParameterAsText(0)
    erase_features = arcpy.GetParameterAsText(1)
    output_feature_class = arcpy.GetParameterAsText(2)

    erase(input_features,erase_features,output_feature_class)