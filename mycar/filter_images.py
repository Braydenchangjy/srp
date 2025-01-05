import os
import json

# Paths for the catalog and image folders
catalog_folder = './data_loop/house/2'
image_folder = os.path.join(catalog_folder, 'images')

# Function to process each catalog file
def process_catalog_file(catalog_file):
    valid_entries = []

    # Open and read the catalog file
    with open(catalog_file, 'r') as f:
        for line in f:
            try:
                # Parse each line as JSON
                data = json.loads(line)
                index = data.get("_index")

                # Build the expected image filename
                image_filename = f"{index}_cam_image_array_.jpg"
                image_path = os.path.join(image_folder, image_filename)

                # Check if the image exists
                if os.path.exists(image_path):
                    # Keep valid entries
                    valid_entries.append(line)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON in {catalog_file}: {line}")

    # Overwrite the catalog file with valid entries
    with open(catalog_file, 'w') as f:
        f.writelines(valid_entries)

    print(f"Processed {catalog_file}. Valid entries: {len(valid_entries)}")

# Main function to scan for catalog files and process them
def scan_and_clean_catalogs():
    # Scan for all catalog files in the folder
    for file in os.listdir(catalog_folder):
        if file.startswith("catalog_") and file.endswith(".catalog"):
            catalog_file = os.path.join(catalog_folder, file)
            process_catalog_file(catalog_file)

if __name__ == "__main__":
    scan_and_clean_catalogs()
