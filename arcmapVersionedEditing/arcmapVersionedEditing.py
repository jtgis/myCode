################################################################################
#
# Version: 1.0
#
# Creates a temporary sde file that is used to create a version of the feature
# classes listed for editing. If a feature class that you are trying to edit
# using arcpy is not set in the fcLST it will not be versioned. The name used
# in fcLST (without the user ex USER.FeatureClass = "FeatureClass") is how the
# feature class can be called by arcpy geoprocessing and editing tools.
#
# To run the tool in your script you will need to import the listed libraries
# and set the appropriate environment settings. There are also two examples
# listed at the end on how to call the functions. One with variables previously
# set and the other with variables set during the function call. The end editing
# function does not require any variables as it reuses stuff from the start
# editing function.
#
# The only things that I can think of that will make it fall apart are if you
# reuse a variable name somewhere else in your script or something with the
# global variable stuff as they were set in not necessarily the best way, but in
# a way that made sense to me and worked.
#
# This is a modified version of some code I found on gis.stackexchange.com to
# make it more plug and play.
# 
# https://pro.arcgis.com/en/pro-app/help/data/geodatabases/overview/the-version-editing-process.htm
#
# Author: https://github.com/jtgis
#
# Date: 26 Nov 2019
#
################################################################################

import arcpy
import time
import os

# add these two functions to the beginning of your code
def createVersionStartEdit(fcLST,temploc,sdecon,user,password):
    global version, workspace, edit, fcLSTglob, userglob
    fcLSTglob = fcLST
    userglob = user
    version = "ARCPY"+time.strftime("%d%m%Y%I%M%S")
    tempsdecon = "SDECONN"+time.strftime("%d%m%Y%I%M%S")
    workspace = os.path.join(temploc,
                             tempsdecon+".sde")
    arcpy.CreateVersion_management(sdecon,
                                   "SDE.DEFAULT",
                                   version,
                                   "PRIVATE")
    arcpy.CreateArcSDEConnectionFile_management(temploc,
                                                tempsdecon,
                                                " ",
                                                "sde:oracle11g:somesde.world",
                                                "",
                                                "",
                                                userglob,password,
                                                "",
                                                user+"."+version)
    edit = arcpy.da.Editor(workspace) 
    edit.startEditing(False,True)
    edit.startOperation()
    for i in fcLSTglob:
        editfeature = os.path.join(workspace,
                                   i)
        arcpy.MakeFeatureLayer_management(editfeature,
                                          i.split(".")[1])
    print("versioned editing started")
    arcpy.AddMessage("versioned editing started")
    return version, workspace, edit, fcLSTglob, userglob
 
def stopEditReconcileVersion():
    edit.stopOperation()
    edit.stopEditing(True)
    for i in fcLSTglob:
        arcpy.ChangeVersion_management(i.split(".")[1],
                                       "TRANSACTIONAL",
                                       "SDE.DEFAULT")
    arcpy.ReconcileVersions_management(workspace,
                                       "",
                                       "SDE.DEFAULT",
                                       userglob+"."+version,
                                       "LOCK_ACQUIRED",
                                       "NO_ABORT",
                                       "BY_OBJECT",
                                       "FAVOR_EDIT_VERSION",
                                       "POST",
                                       "DELETE_VERSION")
    os.remove(workspace)
    print("versioned editing ended")
    arcpy.AddMessage("versioned editing ended")
    
################################################################################
if __name__ == '__main__':

    arcpy.env.overwriteOutput = True

    #you can call the functions like this
        
    #ex1 using the predefined variables
    #set variables
    fcLST = ["username.fc1","username.fc2,etc"]
    temploc = r"pathto\temploc"
    sdecon = r"pathto\somesde.sde"
    user = "username"
    password = "password"
    #start edit
    createVersionStartEdit(fcLST,temploc,sdecon,user,password)
    #do some stuff
    #stop edit
    stopEditReconcileVersion()

    #ex2 hardcoding the values to the function
    #start edit
    createVersionStartEdit(["username.fc1","username.fc2,etc"],
                            r"pathto\temploc",
                            r"pathto\somesde.sde",
                            "username",
                            "password")
    #do some stuff
    #stop edit
    stopEditReconcileVersion()
    
################################################################################


