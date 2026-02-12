import os
import sys
import requests
import geopandas as gpd
import pandas as pd
import simplekml
import xml.sax.saxutils as saxutils
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QLabel, QProgressBar, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal

def sanitize(value):
    if isinstance(value, str):
        return saxutils.escape(value)
    return value

class DataFetcher(QThread):
    progress = pyqtSignal(int)
    data_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, query, rest_service_url, max_record_count, total_count):
        super().__init__()
        self.query = query
        self.rest_service_url = rest_service_url
        self.max_record_count = max_record_count
        self.total_count = total_count

    def run(self):
        all_features = []
        offset = 0

        while True:
            params = {
                "where": self.query,
                "outFields": "*",  # Fetch all attributes
                "f": "geojson",
                "resultOffset": offset,
                "resultRecordCount": self.max_record_count
            }
            try:
                response = requests.get(self.rest_service_url, params=params)
                response.raise_for_status()
                data = response.json()
                features = data.get("features", [])

                if not features:
                    break  # No more records to fetch

                all_features.extend(features)
                offset += self.max_record_count
                progress_percentage = int((offset / self.total_count) * 100)
                self.progress.emit(min(progress_percentage, 100))
            except Exception as e:
                self.error_occurred.emit(str(e))
                return

        self.data_fetched.emit({"features": all_features})

class SNBDataDownloader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Bulk SNB Property Assessment Data Downloader")
        self.setGeometry(100, 100, 500, 300)
        
        layout = QtWidgets.QVBoxLayout()

        self.queryLabel = QtWidgets.QLabel("Query Expression:")
        self.queryInput = QTextEdit()
        self.queryInput.setText("UPPER(Descript) SIMILAR TO '%(MULTI|APT|APART)%' AND UPPER(Descript) NOT LIKE '%(BAPT)%'")
        self.queryInput.setFixedHeight(100)
        layout.addWidget(self.queryLabel)
        layout.addWidget(self.queryInput)

        self.outputBtn = QtWidgets.QPushButton("Select Output Folder")
        self.outputBtn.clicked.connect(self.select_output_folder)
        layout.addWidget(self.outputBtn)

        self.outputFolderLabel = QLabel("Output Folder: Not selected")
        layout.addWidget(self.outputFolderLabel)
        
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        self.statusLabel = QLabel("Status: Ready")
        layout.addWidget(self.statusLabel)

        self.processBtn = QtWidgets.QPushButton("Download Data")
        self.processBtn.clicked.connect(self.process_rest_data)
        layout.addWidget(self.processBtn)

        self.outputFolder = ""
        self.rest_service_url = "https://geonb.snb.ca/arcgis/rest/services/GeoNB_SNB_Pan/MapServer/0/query"
        
        self.setLayout(layout)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.outputFolder = folder
            self.outputFolderLabel.setText(f"Output Folder: {folder}")
            print(f"Output folder selected: {folder}")

    def get_max_record_count(self):
        params = {"f": "json"}
        try:
            response = requests.get(self.rest_service_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("maxRecordCount", 1000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch maxRecordCount: {e}")
            return 1000

    def get_total_record_count(self, query):
        params = {
            "where": query,
            "returnCountOnly": True,
            "f": "json"
        }
        try:
            response = requests.get(self.rest_service_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("count", 0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch total record count: {e}")
            return 0

    def process_rest_data(self):
        self.processBtn.setEnabled(False)
        self.outputBtn.setEnabled(False)
        self.statusLabel.setText("Status: In Progress...")

        query = self.queryInput.toPlainText()

        if not query or not self.outputFolder:
            QMessageBox.critical(self, "Error", "All fields must be filled out!")
            self.processBtn.setEnabled(True)
            self.outputBtn.setEnabled(True)
            self.statusLabel.setText("Status: Ready")
            return

        max_record_count = self.get_max_record_count()
        total_count = self.get_total_record_count(query)
        if total_count == 0:
            QMessageBox.critical(self, "Error", "No records found for the given query!")
            self.reset_ui()
            return

        self.fetcher = DataFetcher(query, self.rest_service_url, max_record_count, total_count)
        self.fetcher.progress.connect(self.progressBar.setValue)
        self.fetcher.data_fetched.connect(self.process_fetched_data)
        self.fetcher.error_occurred.connect(self.handle_error)
        self.fetcher.start()

    def process_fetched_data(self, geojson_data):
        if not geojson_data or not geojson_data["features"]:
            QMessageBox.critical(self, "Error", "No data retrieved!")
            self.reset_ui()
            return

        gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])

        output_kmz = os.path.join(self.outputFolder, "SNBPropertyData.kmz")
        output_xls = os.path.join(self.outputFolder, "SNBPropertyData.xlsx")

        try:
            # Create KML file using simplekml
            kml = simplekml.Kml()
            for _, row in gdf.iterrows():
                geom = row.geometry
                attrs = row.drop('geometry').to_dict()
                if geom.geom_type == 'Point':
                    pnt = kml.newpoint(name=row['Descript'], coords=[(geom.x, geom.y)])
                    for key, value in attrs.items():
                        pnt.extendeddata.newdata(name=key, value=str(sanitize(value)))
                elif geom.geom_type == 'Polygon':
                    pol = kml.newpolygon(name=row['Descript'])
                    pol.outerboundaryis = [(x, y) for x, y in zip(*geom.exterior.xy)]
                    for key, value in attrs.items():
                        pol.extendeddata.newdata(name=key, value=str(sanitize(value)))
                elif geom.geom_type == 'LineString':
                    line = kml.newlinestring(name=row['Descript'])
                    line.coords = [(x, y) for x, y in zip(*geom.xy)]
                    for key, value in attrs.items():
                        line.extendeddata.newdata(name=key, value=str(sanitize(value)))
                else:
                    print(f"Unsupported geometry type: {geom.geom_type}")
            kml.save(output_kmz)
            print(f"KMZ file saved to: {output_kmz}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save KMZ file: {e}")
            self.reset_ui()
            return

        try:
            gdf.to_excel(output_xls, index=False)
            print(f"Excel file saved to: {output_xls}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save Excel file: {e}")
            self.reset_ui()
            return

        self.progressBar.setValue(100)
        QMessageBox.information(self, "Success", "Processing complete!")
        self.close()

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error", f"{error_message}")
        self.reset_ui()

    def reset_ui(self):
        self.processBtn.setEnabled(True)
        self.outputBtn.setEnabled(True)
        self.statusLabel.setText("Status: Ready")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SNBDataDownloader()
    window.show()
    sys.exit(app.exec())



