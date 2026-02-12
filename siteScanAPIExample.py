###############################################################################
# Description: This script demonstrates how to use the SiteScan API to create a
# project, mission, upload images, start processing, and check the processing
# status of the mission.
#
# Usage:
# - Update the api variables with your SiteScan API URL and token
# - Update the processing variables with the project name, mission name, and
#   path to the images
# - Run the script (first time enable create mosaic, subsequent times enable add image)
#
# Author: J Totton
# Date: October 2025
# Version: 0.1
###############################################################################

###############################################################################
# imports #####################################################################
###############################################################################

import requests
import os
import shutil
import tempfile
from datetime import time
from arcgis.gis import GIS
from arcgis.raster.analytics import copy_raster

###############################################################################
# functions ###################################################################
###############################################################################

def getOrgID(token, url):
    # Get organization id
    orgRequestURL = f'{url}/organizations'
    response = requests.get(url=orgRequestURL, 
                            headers={'Authorization': f'Bearer {token}'})
    data = response.json()
    for item in data:
        organization_id = item.get('id')
        print(f"Organization ID: {organization_id}")
    return organization_id

def createProject(token, url, organization_id, project_name):
    # Create a new project in the organization
    createProjectURL = f'{url}/organizations/{organization_id}/projects'
    project_data = {"name": f"{project_name}"}
    response = requests.post(url=createProjectURL, 
                             headers={'Authorization': f'Bearer {token}'}, 
                             json=project_data)
    if response.status_code == 201:
        print("Project created successfully")
        project = response.json()
        project_id = project.get('id')
        return project_id
    else:
        print(f"Failed to create project: {response.status_code}")

def createMission(token, url, project_id, mission_name):
    # Create a new mission in the project
    createMissionURL = f'{url}/projects/{project_id}/missions'
    mission_data = {"name": f"{mission_name}"}
    response = requests.post(url=createMissionURL, 
                             headers={'Authorization': f'Bearer {token}'}, 
                             json=mission_data)
    if response.status_code == 201:
        print("Mission created successfully")
        mission =  response.json()
        mission_id = mission.get('id')
        return mission_id
    else:
        print(f"Failed to create mission: {response.status_code}")

def uploadImages(token, url, mission_id, imagesPath):
    # Upload images to the mission
    uploadURL = f'{url}/missions/{mission_id}/media'
    for filename in os.listdir(imagesPath):
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.JPG') or filename.endswith('.JPEG'):
            file = []
            file_path = os.path.join(imagesPath, filename)
            file.append(('file', (filename, open(file_path, 'rb'), 'image/jpeg')))
            response = requests.post(url=uploadURL, 
                                     headers={'Authorization': f'Bearer {token}'}, 
                                     files=file)
            if response.status_code == 201:
                print(f"{file_path} uploaded successfully!")
            else:
                print(f"Failed to upload images: {response.status_code}")

def startProcessing(token, url, mission_id):
    # Start processing the mission
    processURL = f'{url}/missions/{mission_id}/process/default'
    response = requests.post(url=processURL, 
                             headers={'Authorization': f'Bearer {token}'}, 
                             json={})
    if response.status_code == 200:
        print("Processing started successfully")
    else:
        print(f"Failed to start processing: {response.status_code}")

def checkProcessingStatus(token, url, mission_id):
    # Check the processing status of the mission
    missionURL = f'{url}/missions/{mission_id}'
    response = requests.get(missionURL, headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        productList = [['Ortho', 'ortho'], ['DTM', 'dtm'], ['DSM', 'dem']]
        productURLs = []
        for product in productList:
            success = False
            while success == False:
                response = requests.get(missionURL, headers={'Authorization': f'Bearer {token}'})
                mission_data = response.json()
                productURL = mission_data.get('data', {}).get(product[1], {}).get('current', {}).get('url')
                if productURL:
                    print(f"{product[0]} Created")
                    productURLs.append([product[0],productURL])
                    success = True
                else:
                    print(f"{product[0]} in progress")
                    success = False
                    time.sleep(3600)
    else:
        print(f"Failed to get mission data: {response.status_code}")
        print(response.text)
    return productURLs

def downloadFiles(productURLs,temp_dir):
    downloaded_files = []
    for url in productURLs:
        # Download the file
        local_filename = os.path.join(temp_dir, url[1].split('/')[-1])
        with requests.get(url[1], stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded {local_filename}")
        downloaded_files.append([url[0],local_filename])

    return downloaded_files

def createTempFolder():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Temporary directory created at {temp_dir}")
    return temp_dir

def deleteTempFolder(temp_dir):
    # Delete the temporary directory
    shutil.rmtree(temp_dir)
    print(f"Temporary directory {temp_dir} deleted")

###############################################################################
# api variables ###############################################################
###############################################################################

url = 'https://sitescan-api.arcgis.com/api/v2'

token = 'YOUR_API_TOKEN'

gis = GIS('home')

###############################################################################
# processing variables ########################################################
###############################################################################

project_name = "nameForProject"

mission_name = "nameForMission"

imagesPath = r"C:\images"

###############################################################################
# main ########################################################################
###############################################################################

organization_id = getOrgID(token, url)

project_id = createProject(token, url, organization_id, project_name)

mission_id = createMission(token, url, project_id, mission_name)

uploadImages(token, url, mission_id, imagesPath)

startProcessing(token, url, mission_id)

productURLs = checkProcessingStatus(token, url, mission_id)

temp_dir = createTempFolder()

localFiles = downloadFiles(productURLs,temp_dir)

print(localFiles)

for fileToUpload in localFiles:
    if fileToUpload[0] in ('Ortho', 'DTM', 'DSM'):
        print(f"Uploading {fileToUpload[1]} to ArcGIS Portal...")
        base_name = os.path.splitext(os.path.basename(fileToUpload[1]))[0]
        search = gis.content.search(base_name, max_items=1)
        for item in search:
            if item.title == base_name:
                itemID = item.id
        try:
            item_for_deletion = gis.content.get(itemID)
            item_for_deletion.protect(enable = False)
            item_for_deletion.delete(permanent=True)
        except:
            pass
        copy_raster(input_raster=fileToUpload[1],
                    output_name="test_naming")
        print(f"Uploaded {fileToUpload[0]} to ArcGIS Portal!")

deleteTempFolder(temp_dir)
###############################################################################
