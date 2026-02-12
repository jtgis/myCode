import csv
from arcgis.gis import GIS

# function to find js3.x items can add items to the itemsToCheckList to check for other items

def checkForRetiredJSItems(gis, filename):

    # find all items in the Portal
    items = gis.content.search("*", max_items=-1)

    # set the headings for the export csv
    javaScript3xItems = [["Retired Item Type", "Title", "Owner", "Link"]]


    # loop through the items and check for the types of items that are retired and add to list
    for item in items:

        # this list check for web appbuilder apps by item.type and they all have a theme
        # it also finds web appbuilder extensions and packages purely by item type
        # and to find map viewr classic items it checks for the authoring app in the web map item data
        itemsToCheckList = [["Web AppBuilder",item.type == "Web Mapping Application" and 'theme' in item.get_data()],
                            ["Web AppBuilder Extension",item.type == "AppBuilder Extension"],
                            ["AppBuilder Widget Package",item.type == "AppBuilder Widget Package"],
                            ["Map Viewer Classic",item.type == "Web Map" and item.get_data().get('authoringApp') == "WebMapViewer"]]
        
        for check in itemsToCheckList:
            if check[1]:
                xlsRow = [check[0], item.title, item.owner, item.homepage]
                javaScript3xItems.append(xlsRow)

    # save the list to a csv file
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(javaScript3xItems)

# test of the function with input of a gis and outputCSV location and name

gis = GIS("home")

outputCSV = r"C:\Users\jtotton\Desktop\javaScript3xItems.csv"

checkForRetiredJSItems(gis,outputCSV)


