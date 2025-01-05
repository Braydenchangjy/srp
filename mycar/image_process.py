import os
import json
import argparse
from PIL import Image

def update_tub(tub_path):
    # Define paths to images folder and manifest.json
    images_path = os.path.join(tub_path, "images")
    manifest_path = os.path.join(tub_path, "manifest.json")

    # Check if images folder exists
    if not os.path.exists(images_path):
        print(f"Images folder not found at {images_path}. Exiting.")
        return

    # Get the list of existing images
    existing_images = set(os.listdir(images_path))

    # Function to check for corrupted images
    def is_image_corrupted(image_path):
        try:
            with Image.open(image_path) as img:
                img.verify()  # Verify that the image is valid
            return False
        except (IOError, SyntaxError):
            return True

    # Update manifest.json
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as manifest_file:
            try:
                # Load the JSON objects line by line
                lines = manifest_file.readlines()
                manifest_data = [json.loads(line.strip()) for line in lines if line.strip()]
            except json.JSONDecodeError as e:
                print(f"Error reading manifest.json: {e}")
                return

        # Process each JSON object in the manifest
        updated_manifest_data = []
        for obj in manifest_data:
            if isinstance(obj, dict) and "paths" in obj:
                catalog_paths = obj["paths"]

                for catalog_path in catalog_paths:
                    catalog_file_path = os.path.join(tub_path, catalog_path)
                    catalog_manifest_file_path = f"{catalog_file_path}_manifest"

                    # Process the catalog manifest
                    if os.path.exists(catalog_manifest_file_path):
                        with open(catalog_manifest_file_path, "r") as cm_file:
                            catalog_manifest = json.load(cm_file)

                        if os.path.exists(catalog_file_path):
                            with open(catalog_file_path, "r") as c_file:
                                catalog_lines = c_file.readlines()

                            updated_lines = []

                            for line in catalog_lines:
                                entry = json.loads(line)
                                image_name = entry.get("cam/image_array")
                                image_path = os.path.join(images_path, image_name)
                                index_to_remove = entry.get("_index")

                                if image_name in existing_images:
                                    if is_image_corrupted(image_path):
                                        print(f"Corrupted image detected and removed: {image_name}, Index: {index_to_remove}")
                                        os.remove(image_path)  # Delete corrupted image
                                        obj.setdefault("deleted_indexes", []).append(index_to_remove)
                                    else:
                                        updated_lines.append(line)
                                else:
                                    print(f"Missing image detected: {image_name}, Index: {index_to_remove}")
                                    obj.setdefault("deleted_indexes", []).append(index_to_remove)

                            # Write the updated catalog back
                            with open(catalog_file_path, "w") as c_file:
                                c_file.writelines(updated_lines)

                            # Update catalog_manifest line lengths
                            #catalog_manifest["line_lengths"] = [len(line) for line in updated_lines]
                            #with open(catalog_manifest_file_path, "w") as cm_file:
                                #json.dump(catalog_manifest, cm_file, indent=4)

                # Update deleted_indexes based on missing indexes in the range
                current_index = obj.get("current_index", 0)
                all_indexes = set(range(current_index))
                existing_indexes = {int(img.split("_")[0]) for img in existing_images if "_cam_image_array_" in img}
                missing_indexes = sorted(all_indexes - existing_indexes)
                print(f"Missing indexes: {missing_indexes}")
                obj["deleted_indexes"] = sorted(set(obj.get("deleted_indexes", [])) | set(missing_indexes))

            updated_manifest_data.append(obj)

        # Write the updated manifest.json
        with open(manifest_path, "w") as manifest_file:
            for obj in updated_manifest_data:
                manifest_file.write(json.dumps(obj) + "\n")

        print("Manifest and catalogs updated successfully.")
    else:
        print(f"manifest.json not found at {manifest_path}. Exiting.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update DonkeyCar tub JSON files after image deletions.")
    parser.add_argument(
        "--tub",
        type=str,
        required=True,
        help="Path to the DonkeyCar tub directory (e.g., '/path/to/tub')"
    )
    args = parser.parse_args()

    update_tub(args.tub)
