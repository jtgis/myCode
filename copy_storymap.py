"""
Script to copy a Story Map from active portal to another ArcGIS Online account/org.
Creates all new item IDs and updates references to point to them.
Uses the built-in clone_items function for proper handling of complex items.
Author JTotton
Date 12 Feb 2026
Current ArcPro AGOL and AGE Versions: 3.6, 2025.3, 12.0
"""

from arcgis.gis import GIS
import getpass


def connect_to_portals():
    """Connect to source (active) and destination portals."""
    
    print("=" * 60)
    print("STORY MAP COPY TOOL")
    print("=" * 60)
    
    # Connect to source portal (active portal from ArcGIS Pro or default)
    print("\n--- Source Portal (your active portal) ---")
    source_choice = input("Connect to source using:\n1. Active Portal (ArcGIS Pro)\n2. Enter credentials\nChoice (1/2): ").strip()
    
    if source_choice == "1":
        try:
            source_gis = GIS("pro")
            print(f"Connected to source: {source_gis.url}")
            print(f"Logged in as: {source_gis.users.me.username}")
        except Exception as e:
            print(f"Could not connect to active portal: {e}")
            print("Falling back to manual credentials...")
            source_choice = "2"
    
    if source_choice == "2":
        source_url = input("Source Portal URL (e.g., https://www.arcgis.com): ").strip()
        source_username = input("Source Username: ").strip()
        source_password = getpass.getpass("Source Password: ")
        source_gis = GIS(source_url, source_username, source_password)
        print(f"Connected to source: {source_gis.url}")
        print(f"Logged in as: {source_gis.users.me.username}")
    
    # Connect to destination portal
    print("\n--- Destination Portal ---")
    dest_choice = input("Connect to destination using:\n1. Active Portal (ArcGIS Pro)\n2. Enter credentials\nChoice (1/2): ").strip()
    
    if dest_choice == "1":
        try:
            dest_gis = GIS("pro")
            print(f"Connected to destination: {dest_gis.url}")
            print(f"Logged in as: {dest_gis.users.me.username}")
        except Exception as e:
            print(f"Could not connect to active portal: {e}")
            print("Falling back to manual credentials...")
            dest_choice = "2"
    
    if dest_choice == "2":
        dest_url = input("Destination Portal URL (e.g., https://www.arcgis.com): ").strip()
        dest_username = input("Destination Username: ").strip()
        dest_password = getpass.getpass("Destination Password: ")
        dest_gis = GIS(dest_url, dest_username, dest_password)
        print(f"Connected to destination: {dest_gis.url}")
        print(f"Logged in as: {dest_gis.users.me.username}")
    
    return source_gis, dest_gis


def get_storymap_item(source_gis):
    """Get the story map item to copy."""
    
    print("\n--- Select Story Map to Copy ---")
    print("Options:")
    print("1. Enter Item ID directly")
    print("2. Search for Story Maps by title")
    
    choice = input("Choice (1/2): ").strip()
    
    if choice == "1":
        item_id = input("Enter Story Map Item ID: ").strip()
        item = source_gis.content.get(item_id)
    else:
        search_term = input("Enter search term for Story Map title: ").strip()
        # Search for story maps (StoryMap type or Web Mapping Application with storymap tag)
        results = source_gis.content.search(
            query=f'title:{search_term} AND (type:"StoryMap" OR type:"Web Mapping Application")',
            max_items=20
        )
        
        if not results:
            print("No story maps found matching that search.")
            return None
        
        print("\nFound Story Maps:")
        for i, item in enumerate(results):
            print(f"  {i+1}. {item.title} (ID: {item.id}, Type: {item.type})")
        
        selection = int(input("\nSelect number: ").strip()) - 1
        item = results[selection]
    
    if item:
        print(f"\nSelected: {item.title}")
        print(f"  Type: {item.type}")
        print(f"  ID: {item.id}")
        print(f"  Owner: {item.owner}")
    
    return item


def copy_storymap(source_gis, dest_gis, storymap_item):
    """
    Copy a story map with all dependencies using clone_items.
    Returns the new story map item.
    """
    
    print("\n" + "=" * 60)
    print("COPYING STORY MAP")
    print("=" * 60)
    
    # Ask for destination folder
    dest_folder = input("\nDestination folder name (leave blank for root): ").strip() or None
    
    # Create folder if specified and doesn't exist
    if dest_folder:
        try:
            dest_gis.content.create_folder(dest_folder)
            print(f"Created folder: {dest_folder}")
        except:
            print(f"Using existing folder: {dest_folder}")
    
    print("\nCloning story map and all dependencies...")
    print("This may take a few minutes...\n")
    
    try:
        # Use clone_items - handles all dependencies, resources, and ID remapping
        cloned_items = dest_gis.content.clone_items(
            items=[storymap_item],
            folder=dest_folder,
            copy_data=True,
            search_existing_items=False  # Force new IDs
        )
        
        if cloned_items:
            print(f"\nSuccessfully cloned {len(cloned_items)} item(s):")
            new_storymap = None
            for item in cloned_items:
                print(f"  - {item.title} ({item.type}) - ID: {item.id}")
                if item.type == "StoryMap" or "StoryMap" in item.type:
                    new_storymap = item
            
            # If we didn't find a StoryMap type, return the first item
            if not new_storymap and cloned_items:
                new_storymap = cloned_items[0]
            
            return new_storymap
        else:
            print("No items were cloned.")
            return None
            
    except Exception as e:
        print(f"Error during cloning: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    
    try:
        # Connect to portals
        source_gis, dest_gis = connect_to_portals()
        
        # Select story map
        storymap_item = get_storymap_item(source_gis)
        
        if not storymap_item:
            print("No story map selected. Exiting.")
            return
        
        # Confirm
        confirm = input(f"\nCopy '{storymap_item.title}' to {dest_gis.url}? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        # Copy the story map
        new_storymap = copy_storymap(source_gis, dest_gis, storymap_item)
        
        if new_storymap:
            print("\n" + "=" * 60)
            print("COPY COMPLETE!")
            print("=" * 60)
            print(f"New Story Map: {new_storymap.title}")
            print(f"New Item ID: {new_storymap.id}")
            print(f"URL: {dest_gis.url}/home/item.html?id={new_storymap.id}")
            
            # Option to make public
            share = input("\nShare story map publicly? (y/n): ").strip().lower()
            if share == 'y':
                new_storymap.share(everyone=True)
                print("Story map shared publicly.")
        else:
            print("\nCopy failed. Please check errors above.")
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
