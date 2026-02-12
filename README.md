# myCode
Useful tools, mostly GIS related, made by me for you. Using human readable code to make computers do what we want.

## Scripts

### arcmapBasicErase.py
Adds the erase geoprocessing tool to the ArcMap Basic license level. Works by UNIONing two input feature classes, selecting features that do not overlap with the erase features. Tested with ArcMap Desktop Basic 10.5.1 and Python 2.7.

### arcmapPileVolumes.py
Calculates volumes from polygon boundaries. Takes a DEM, DSM, and input polygons to compute volume calculations between surfaces.

### arcmapRasterClipper.py
Clips a single raster, a list of rasters, or a directory of rasters to an input extent. Useful for batch processing raster datasets with a specific area of interest.

### arcmapVersionedEditing.py
Creates a temporary SDE file for versioned editing of feature classes using ArcPy. Enables editing workflows for versioned geodatabase feature classes with proper version management.

### arcpyDownloadMapService.py
Requests feature class data from an ArcGIS REST API map service. Takes a URL and output feature class as input and downloads the data.

### tpkxToPortal.py
Creates tile packages (TPKX) from raster data and uploads them to ArcGIS Portal. Uses a template APRX file and input polygons to generate and publish tile packages.

### ArcGISOnlineEnterpriseItemSizeUsage.py
Exports a CSV file containing information about all items in an ArcGIS Online organization or Portal, including item name, type, ID, size in bytes, and view count.

### SNBPropertyDataDownloader.py
Downloads property data from SNB (Service New Brunswick) REST services. Features a PyQt6 GUI for selecting output folder and monitoring download progress. Exports data as GeoJSON, Shapefile, GeoPackage, and KML formats.

### cameraMetadataChecker.py
Checks images for GPS coordinates, camera orientation (roll/pitch/yaw), and sensor specifications by parsing EXIF metadata tags. Useful for drone imagery and aerial photography workflows.

### checkForRetiredItems.py
Scans an ArcGIS Portal for retired item types including Web AppBuilder applications, Map Viewer Classic items, and other deprecated content. Exports findings to a CSV file for migration planning.

### copy_storymap.py
Copies a Story Map from one ArcGIS Portal to another, creating new item IDs and updating all references. Uses the built-in clone_items function for proper handling of complex items.

### sendEmail.py
Simple email sending function using SMTP. Requires configuration of email server and credentials.

### siteScanAPIExample.py
Demonstrates how to use the Site Scan API to create projects and missions, upload images, start processing, and check processing status. Includes examples for creating mosaics and adding images to existing missions.
