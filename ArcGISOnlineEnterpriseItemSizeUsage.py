import csv

from arcgis.gis import GIS

# Define the CSV file path

csv_file_path = r'C:\SOMECSV.csv'

# Connect to your ArcGIS Online or Portal

gis = GIS('home')

# Get all items in the organization

items = gis.content.search(query="",
                           max_items=10000, 
                           outside_org=False)

# Write item names, item IDs, and view counts to the CSV file

with open(csv_file_path, mode='w', newline='') as csv_file:

    fieldnames = ['Item Name', 'Item Type', 'Item ID', 'Item Size (Bytes)', 'View Count']

    writer = csv.DictWriter(csv_file, 
                            fieldnames=fieldnames)

    writer.writeheader()

    for item in items:
        
        try:

            item_size = item.size if item.size is not None else ''  # Set size to empty string if None

        except:

            item_size = 'NA'

        writer.writerow({'Item Name': item.title,
                         'Item Type': item.type, 
                         'Item ID': item.id,
                         'Item Size (Bytes)': item_size, 
                         'View Count': item.numViews})

print(f"Item names, IDs, and view counts have been written to {csv_file_path}")