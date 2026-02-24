# [jtgis code](https://code.jtgis.ca/)
Useful tools, mostly GIS related.

## Scripts

- [arcmapBasicErase.py](#arcmapbasicerasepy)
- [arcmapPileVolumes.py](#arcmappilevolumespy)
- [arcmapRasterClipper.py](#arcmaprasterclipperpy)
- [arcmapVersionedEditing.py](#arcmapversionededitingpy)
- [arcpyDownloadMapService.py](#arcpydownloadmapservicepy)
- [tpkxToPortal.py](#tpkxtoportalpy)
- [ArcGISOnlineEnterpriseItemSizeUsage.py](#arcgisonlineenterpriseitemsizeusagepy)
- [SNBPropertyDataDownloader.py](#snbpropertydatadownloaderpy)
- [cameraMetadataChecker.py](#camerametadatacheckerpy)
- [checkForRetiredItems.py](#checkforretireditemspy)
- [copy_storymap.py](#copy_storymappy)
- [sendEmail.py](#sendemailpy)
- [siteScanAPIExample.py](#sitescanapiexamplepy)

---

### [arcmapBasicErase.py](https://github.com/jtgis/myCode/blob/master/arcmapBasicErase.py)
Adds the erase geoprocessing tool to the ArcMap Basic license level. Works by UNIONing two input feature classes, selecting features that do not overlap with the erase features, and clipping the result. If either input is not a polygon, it will be buffered to a polygon before processing. Tested with ArcMap Desktop Basic 10.5.1 and Python 2.7.

**Requirements:**
- ArcMap Desktop (Basic license or higher) with Python 2.7
- `arcpy`

**Setup & Usage:**
1. Add the script as a Script Tool in an ArcMap Toolbox.
2. Configure three parameters in the tool:
   - **Parameter 0:** Input Features (feature class to keep)
   - **Parameter 1:** Erase Features (feature class to erase with)
   - **Parameter 2:** Output Feature Class (result location)
3. Run the tool from ArcMap, or call directly:
   ```python
   from arcmapBasicErase import erase
   erase("path/to/input_fc", "path/to/erase_fc", "path/to/output_fc")
   ```

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/arcmapBasicErase.py)**

---

### [arcmapPileVolumes.py](https://github.com/jtgis/myCode/blob/master/arcmapPileVolumes.py)
Calculates volumes between two surfaces (DEM and DSM) within polygon boundaries. For each input polygon, extracts the raster surfaces, runs a Cut/Fill analysis, and writes the gross and net volume (in cubic meters) back to the output shapefile.

**Requirements:**
- ArcMap Desktop with 3D Analyst and Spatial Analyst extensions
- Python 2.7
- `arcpy`

**Setup & Usage:**
1. Add the script as a Script Tool in an ArcMap Toolbox.
2. Configure four parameters:
   - **Parameter 0:** Input Polygons (polygon feature class defining pile boundaries)
   - **Parameter 1:** Input DEM (base surface raster)
   - **Parameter 2:** Input DSM (top surface raster)
   - **Parameter 3:** Output Folder (where the result shapefile is saved)
3. Run the tool. The output shapefile will include `GROSS_M3` and `NET_M3` fields.

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/arcmapPileVolumes.py)**

---

### [arcmapRasterClipper.py](https://github.com/jtgis/myCode/blob/master/arcmapRasterClipper.py)
Clips a single raster, a list of rasters, or an entire directory of rasters to the extent of an input feature class. Outputs are saved with a `clipped_` prefix in the specified output folder. Useful for batch processing raster datasets with a specific area of interest.

**Requirements:**
- ArcMap Desktop with Spatial Analyst extension
- Python 2.7
- `arcpy`, `arcpy.sa`

**Setup & Usage:**
1. Add the script as a Script Tool in an ArcMap Toolbox.
2. Configure three parameters:
   - **Parameter 0:** Input Rasters (a single raster, list, or folder of rasters)
   - **Parameter 1:** Extent (feature class defining the clip boundary)
   - **Parameter 2:** Output Folder
3. Run the tool, or call directly:
   ```python
   from arcmapRasterClipper import rasterClipper
   rasterClipper("path/to/rasters", "path/to/extent_fc", "path/to/output")
   ```

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/arcmapRasterClipper.py)**

---

### [arcmapVersionedEditing.py](https://github.com/jtgis/myCode/blob/master/arcmapVersionedEditing.py)
Creates a temporary SDE connection file and a named version for versioned editing of enterprise geodatabase feature classes using ArcPy. Handles version creation, editing, reconciliation, posting, and cleanup.

**Requirements:**
- ArcMap Desktop or ArcGIS Pro with access to an enterprise geodatabase (SDE)
- Python 2.7+
- `arcpy`

**Setup & Usage:**
1. Import the two functions into your script.
2. Define your variables:
   ```python
   fcLST = ["username.fc1", "username.fc2"]    # feature classes to edit
   temploc = r"path\to\temp\folder"             # location for temp SDE file
   sdecon = r"path\to\connection.sde"           # existing SDE connection file
   user = "username"
   password = "password"
   ```
3. Start editing, perform operations, then stop editing:
   ```python
   from arcmapVersionedEditing import createVersionStartEdit, stopEditReconcileVersion
   createVersionStartEdit(fcLST, temploc, sdecon, user, password)
   # ... perform your edits here ...
   stopEditReconcileVersion()
   ```
4. Update the SDE connection string on line 54 (`sde:oracle11g:somesde.world`) to match your database.

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/arcmapVersionedEditing.py)**

---

### [arcpyDownloadMapService.py](https://github.com/jtgis/myCode/blob/master/arcpyDownloadMapService.py)
Downloads feature class data from an ArcGIS REST API map service by paginating through all object IDs. Supports optional spatial filtering using a query layer. The data is saved as a feature class in a file geodatabase or in-memory workspace.

**Requirements:**
- ArcMap Desktop or ArcGIS Pro
- Python 2.7+
- `arcpy`, `requests`, `json`, `tempfile`, `shutil`

**Setup & Usage:**
1. Edit line 20 to set the map service URL:
   ```python
   url = "https://your-server.com/arcgis/rest/services/ServiceName/MapServer/0"
   ```
2. Call the function:
   ```python
   from arcpyDownloadMapService import downloadRestFeatures
   fc = downloadRestFeatures(url, queryLayer="", query="", outLocation="path/to/gdb", outName="output_fc")
   ```
   - `queryLayer`: Optional feature class to spatially filter results (pass `""` for none).
   - `query`: Optional SQL WHERE clause (pass `""` for all features).

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/arcpyDownloadMapService.py)**

---

### [tpkxToPortal.py](https://github.com/jtgis/myCode/blob/master/tpkxToPortal.py)
Creates tile packages (TPKX) from raster data clipped by individual polygon features and optionally uploads them to ArcGIS Portal. Loops through each polygon, generates a TPKX tile package, and publishes it to the active Portal.

**Requirements:**
- ArcGIS Pro with Python 3.6+
- `arcpy`, `arcgis`

**Setup & Usage:**
1. Edit the input variables at the top of the script (lines 10–19):
   ```python
   rasterType = "TYPE OF RASTER DATA"
   subArea = "CITY?"
   area = "PROVINCE"
   inputPolygons = r"path\to\polygon_features"
   inputPolyNameField = 'NAME_FIELD'
   detail = 16                                    # level of detail for tiles
   templateAPRXFile = r"path\to\template.aprx"    # APRX with one empty map named "Map"
   inputRasterLyr = r"path\to\raster.lyrx"        # layer file with raster data
   outputFolder = r"path\to\output"
   enableUploadToPortal = True                     # set False to only create local TPKX
   ```
2. Sign into your Portal within ArcGIS Pro (the script connects using `GIS("home")`).
3. Run: `python tpkxToPortal.py`

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/tpkxToPortal.py)**

---

### [ArcGISOnlineEnterpriseItemSizeUsage.py](https://github.com/jtgis/myCode/blob/master/ArcGISOnlineEnterpriseItemSizeUsage.py)
Exports a CSV file containing information about all items in an ArcGIS Online organization or Portal, including item name, type, ID, size in bytes, and view count. Useful for auditing organizational content and storage usage.

**Requirements:**
- Python 3.6+
- `arcgis` (ArcGIS API for Python)

**Setup & Usage:**
1. Install the ArcGIS API for Python:
   ```
   pip install arcgis
   ```
2. Edit line 7 to set the output CSV path:
   ```python
   csv_file_path = r'C:\path\to\output.csv'
   ```
3. Sign into your Portal within ArcGIS Pro, or modify line 11 to use credentials:
   ```python
   gis = GIS("https://your-portal.com", "username", "password")
   ```
4. Run: `python ArcGISOnlineEnterpriseItemSizeUsage.py`

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/ArcGISOnlineEnterpriseItemSizeUsage.py)**

---

### [SNBPropertyDataDownloader.py](https://github.com/jtgis/myCode/blob/master/SNBPropertyDataDownloader.py)
Downloads property assessment data from the Service New Brunswick (SNB) GeoNB REST service. Features a PyQt6 GUI where you can enter a custom query expression, select an output folder, and monitor download progress. Results are exported as KMZ and Excel files.

**Requirements:**
- Python 3.6+
- `requests`, `geopandas`, `pandas`, `simplekml`, `PyQt6`, `openpyxl`

**Setup & Usage:**
1. Install dependencies:
   ```
   pip install requests geopandas pandas simplekml PyQt6 openpyxl
   ```
2. Run: `python SNBPropertyDataDownloader.py`
3. In the GUI:
   - Enter or modify the SQL query expression (a default query is provided).
   - Click **Select Output Folder** to choose where files are saved.
   - Click **Download Data** to start the download.
4. Output files (`SNBPropertyData.kmz` and `SNBPropertyData.xlsx`) are saved to the selected folder.

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/SNBPropertyDataDownloader.py)**

---

### [cameraMetadataChecker.py](https://github.com/jtgis/myCode/blob/master/cameraMetadataChecker.py)
Scans a folder of JPEG images for GPS coordinates (latitude, longitude, altitude), camera orientation (roll/pitch/yaw), and sensor specifications (make, model, focal length) by parsing EXIF metadata. Outputs a CSV report summarizing what metadata each image contains. Useful for drone imagery and aerial photography quality checks.

**Requirements:**
- Python 3.6+
- No external dependencies (uses only standard library: `os`, `struct`, `csv`)

**Setup & Usage:**
1. Edit line 4 to set the folder containing your images:
   ```python
   IMAGE_FOLDER = r"path/to/your/images"
   ```
2. Run: `python cameraMetadataChecker.py`
3. The script outputs `image_metadata_check.csv` in the image folder with columns: `image_name`, `image_path`, `has_gps_xyz`, `has_camera_orientation`, `has_sensor_info`.

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/cameraMetadataChecker.py)**

---

### [checkForRetiredItems.py](https://github.com/jtgis/myCode/blob/master/checkForRetiredItems.py)
Scans an ArcGIS Portal or ArcGIS Online organization for retired JavaScript 3.x item types including Web AppBuilder applications, Web AppBuilder extensions, AppBuilder Widget Packages, and Map Viewer Classic web maps. Exports findings to a CSV file for migration planning.

**Requirements:**
- Python 3.6+
- `arcgis` (ArcGIS API for Python)

**Setup & Usage:**
1. Install the ArcGIS API for Python:
   ```
   pip install arcgis
   ```
2. Sign into your Portal within ArcGIS Pro, or modify line 38 to use credentials:
   ```python
   gis = GIS("https://your-portal.com", "username", "password")
   ```
3. Edit line 40 to set the output CSV path:
   ```python
   outputCSV = r"C:\path\to\retired_items.csv"
   ```
4. Run: `python checkForRetiredItems.py`

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/checkForRetiredItems.py)**

---

### [copy_storymap.py](https://github.com/jtgis/myCode/blob/master/copy_storymap.py)
Interactive command-line tool that copies a Story Map from one ArcGIS Portal or ArcGIS Online organization to another. Creates all new item IDs and updates internal references. Uses the built-in `clone_items` function for proper handling of complex Story Map dependencies.

**Requirements:**
- Python 3.6+
- `arcgis` (ArcGIS API for Python)

**Setup & Usage:**
1. Install the ArcGIS API for Python:
   ```
   pip install arcgis
   ```
2. Run: `python copy_storymap.py`
3. Follow the interactive prompts:
   - Connect to the **source** portal (via ArcGIS Pro active portal or manual credentials).
   - Connect to the **destination** portal.
   - Select a Story Map by item ID or search by title.
   - Confirm the copy and optionally share publicly.

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/copy_storymap.py)**

---

### [sendEmail.py](https://github.com/jtgis/myCode/blob/master/sendEmail.py)
Simple email sending function using Python's `smtplib`. Provides a reusable `sendEmail()` function for sending plain-text emails via SMTP.

**Requirements:**
- Python 2.7+
- `smtplib` (standard library)

**Setup & Usage:**
1. Edit line 3 to set the sender address:
   ```python
   from_address = "your_email@example.com"
   ```
2. Edit line 8 to set the SMTP server:
   ```python
   server = smtplib.SMTP("your.smtp.server.com")
   ```
3. Import and call the function:
   ```python
   from sendEmail import sendEmail
   sendEmail("recipient@example.com", "Subject Line", "Email body text")
   ```

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/sendEmail.py)**

---

### [siteScanAPIExample.py](https://github.com/jtgis/myCode/blob/master/siteScanAPIExample.py)
Demonstrates a full Site Scan API workflow: creating a project and mission, uploading drone images, starting processing, polling for completion, downloading output products (Ortho, DTM, DSM), and uploading results to ArcGIS Portal using `copy_raster`.

**Requirements:**
- Python 3.6+
- `requests`, `arcgis` (ArcGIS API for Python)
- A valid Site Scan API token

**Setup & Usage:**
1. Install dependencies:
   ```
   pip install requests arcgis
   ```
2. Edit the API variables (lines 157–159):
   ```python
   url = 'https://sitescan-api.arcgis.com/api/v2'
   token = 'YOUR_API_TOKEN'
   ```
3. Edit the processing variables (lines 167–171):
   ```python
   project_name = "nameForProject"
   mission_name = "nameForMission"
   imagesPath = r"C:\path\to\images"
   ```
4. Sign into your Portal within ArcGIS Pro (for uploading results).
5. Run: `python siteScanAPIExample.py`

🔗 **[View the source code on GitHub](https://github.com/jtgis/code/blob/master/siteScanAPIExample.py)**
