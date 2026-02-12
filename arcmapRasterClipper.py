################################################################################
#
# Version: 1.0
#
# The purpose of this tool is to arcpy.GetParameterAsText(0) a single raster, 
# a list of rasters, or a directory of rasters to an input extent.
#
# Author: https://github.com/jtgis
#
# Date: 17 march 2021
#
################################################################################

import arcpy
import os
from arcpy.sa import *

def rasterClipper(inputRasters,extent,outputFolder):
    """
    This function takes 3 inputs inputRasters can be a raster file, list of
    rasters, or a folder of rasters. The extent file should be some feature
    class. The output rasters should end up in the same format as the input in 
    the output folder with the prefix "clipped_".
    Add prints to see what the lists have in them to help debug.
    It also returns a list of the new rasters if you want to do more with them...
    """
    arcpy.CheckOutExtension("Spatial")
    #if the type is a string we will assume it is a folder or a raster
    if type(inputRasters) is str:
        #make an empty list that will be input for the extract by mask loop below
        rasterList = []
        #now we check the type of the string. if it is just a single raster,
        #we add just one raster to rasterList, if it is a folder we iterate
        #through the files to see if they are rasters and add them to the list.
        #i did not check to see if this checks subdirectories.
        varType = arcpy.Describe(inputRasters).dataType
        if varType == "RasterDataset":
            rasterList.append(inputRasters)
        elif varType == "Folder":
            #next 3 lines from https://stackoverflow.com/questions/9816816/get-absolute-paths-of-all-files-in-a-directory
            #this loops through the files in the folder and checks for rasters.
            #rasters get added to rasterList.
            for dirpath,_,filenames in os.walk(inputRasters):
                for f in filenames:
                    fileCheck = os.path.abspath(os.path.join(dirpath, f))
                    varType = arcpy.Describe(fileCheck).dataType
                    if varType == "RasterDataset":
                        rasterList.append(fileCheck)
        else:
            #if it is some other string than raster or folder you get a talking to.
            arcpy.AddMessage("This tool needs either a raster, directory of rasters, or a list of rasters to run.")
            return
    #if it is a list just make the lists equal to each other, a little redundant,
    # but i like it. This list is the input to the extract by mask loop below.
    elif type(inputRasters) is list:
        rasterList = inputRasters
    else:
        #give us some rasters!
        arcpy.AddMessage("This tool needs either a raster, directory of rasters, or a list of rasters to run.")
        return
    
    newRasters = []
    for raster in rasterList:
        #for all of the rasters in the list we will create a clipped raster
        #in our output directory of the same file type with teh same name plus
        # a prefix "clipped_"
        fileName = raster.split("\\")[-1]
        outRaster = "{}\clipped_{}".format(outputFolder,fileName)
        arcpy.gp.ExtractByMask_sa(raster,extent,outRaster)
        newRasters.append(outRaster)

    #the list of rasters created with full path and extension (if applicable)
    return newRasters
    
if __name__ == '__main__':
    """
    Accept feature classes as input from ArcMap Toolbox Script Tool
    """
    inputRasters = arcpy.GetParameterAsText(0)
    extent = arcpy.GetParameterAsText(1)
    outputFolder = arcpy.GetParameterAsText(2)

    rasterClipper(inputRasters,extent,outputFolder)