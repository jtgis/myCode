"""Check images for GPS coordinates, camera orientation (roll/pitch/yaw), and sensor specs"""
import os, struct, csv

IMAGE_FOLDER = r"SOMEFOLDER"

# EXIF tag hex codes for finding metadata
TAGS = {'make': 0x010F, 'model': 0x0110, 'exif_ifd': 0x8769, 'gps_ifd': 0x8825,
        'focal': 0x920A, 'sensor_w': 0xA002, 'lat': 0x0002, 'lon': 0x0004, 'alt': 0x0006}

def parse_tags(data, offset, order):
    """Extract tag IDs from EXIF section"""
    if offset + 2 > len(data): return {}
    tags = {}
    for i in range(struct.unpack(order + 'H', data[offset:offset+2])[0]):
        p = offset + 2 + i*12
        if p + 12 > len(data): break
        tid = struct.unpack(order + 'H', data[p:p+2])[0]
        ttype = struct.unpack(order + 'H', data[p+2:p+4])[0]
        tags[tid] = struct.unpack(order + 'I', data[p+8:p+12])[0] if ttype == 4 else True
    return tags


def check_image(path):
    """Check single image → return {gps, orientation, sensor}"""
    try:
        with open(path, 'rb') as f:
            data = f.read(min(os.path.getsize(path), 50*1024*1024))  # Max 50MB
        
        if data[:2] != b'\xff\xd8': return {k: False for k in ['gps', 'orientation', 'sensor']}
        
        # Orientation: must have roll, pitch, yaw
        orientation = all(x in data for x in [b'RollDegree="', b'PitchDegree="', b'YawDegree="'])
        
        # Parse EXIF
        start = data.find(b'Exif\x00\x00')
        if start == -1: return {'gps': False, 'orientation': orientation, 'sensor': False}
        
        exif = data[start + 6:]
        if len(exif) < 8: return {'gps': False, 'orientation': orientation, 'sensor': False}
        
        order = '<' if exif[:2] == b'II' else '>'
        if struct.unpack(order + 'H', exif[2:4])[0] != 0x002A:
            return {'gps': False, 'orientation': orientation, 'sensor': False}
        
        main = parse_tags(exif, struct.unpack(order + 'I', exif[4:8])[0], order)
        
        # Sensor: need make/model + (focal or sensor width)
        sensor = TAGS['make'] in main and TAGS['model'] in main
        if sensor and TAGS['exif_ifd'] in main:
            etags = parse_tags(exif, main[TAGS['exif_ifd']], order)
            sensor = TAGS['focal'] in etags or TAGS['sensor_w'] in etags
        
        # GPS: need lat/lon/alt
        gps = False
        if TAGS['gps_ifd'] in main:
            gtags = parse_tags(exif, main[TAGS['gps_ifd']], order)
            gps = all(TAGS[k] in gtags for k in ['lat', 'lon', 'alt'])
        
        return {'gps': gps, 'orientation': orientation, 'sensor': sensor}
    
    except: return {'gps': False, 'orientation': False, 'sensor': False}


def main(folder):
    """Process: find JPEGs → check metadata → save CSV"""
    if not os.path.exists(folder): return print(f"Error: '{folder}' not found!")
    
    images = [os.path.join(r,f) for r,_,fs in os.walk(folder) for f in fs if f.lower().endswith(('.jpg','.jpeg'))]
    if not images: return print("No JPEGs found")
    
    print(f"Checking {len(images)} image(s)...\n")
    
    results = []
    for i, path in enumerate(images, 1):
        name = os.path.basename(path)
        m = check_image(path)
        results.append({'image_name': name, 'image_path': os.path.relpath(path, folder),
                       'has_gps_xyz': m['gps'], 'has_camera_orientation': m['orientation'], 
                       'has_sensor_info': m['sensor']})
        print(f"  [{i}/{len(images)}] {name}... GPS:{m['gps']}, Orient:{m['orientation']}, Sensor:{m['sensor']}")
    
    out = os.path.join(folder, "image_metadata_check.csv")
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['image_name', 'image_path', 'has_gps_xyz', 'has_camera_orientation', 'has_sensor_info'])
        w.writeheader()
        w.writerows(results)
    
    print(f"\n✓ Saved: {out}\n")
    print(f"Total: {len(results)} | GPS: {sum(r['has_gps_xyz'] for r in results)} | Orient: {sum(r['has_camera_orientation'] for r in results)} | Sensor: {sum(r['has_sensor_info'] for r in results)}")

if __name__ == "__main__": main(IMAGE_FOLDER)
