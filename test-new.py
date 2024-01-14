import os
import json
import requests
from queue import Queue
from urllib.parse import urlparse

def download_file(url, folder_path):
    """Download a file from the given URL and save it to the specified folder."""
    # Extract JSON filename from the URL
    json_filename = os.path.basename(urlparse(url).path)
    file_path = os.path.join(folder_path, json_filename)

    # Skip download if the file already exists
    if os.path.exists(file_path):
        print(f"File '{json_filename}' already exists. Skipping download.")
    else:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"File '{json_filename}' downloaded successfully.")
            queue.put(file_path)
        else:
            raise Exception(f"Failed to download file from {url}. Status code: {response.status_code}")

    return file_path

def process_reference(ref, output_folder, is_main_file):
    """Recursively process $ref in the Swagger file."""
    if ref.startswith("http"):
        # Download and update the dependency file
        download_url = ref.replace("http://127.0.0.1:10000", "https://developer-specs.company-information.service.gov.uk")
        dependency_path = download_file(download_url, output_folder)

        # Extract JSON filename from the original URL for relative path
        original_filename = os.path.basename(urlparse(ref).path)
        
        # Calculate relative path from the current folder
        relative_path = os.path.relpath(dependency_path, output_folder)
        
        # Append # part from the original URL
        fragment = urlparse(ref).fragment
        ref_path = f"{relative_path}#{fragment}"

        if is_main_file is False:
            return ref_path.replace(os.sep, "/")  # Ensure consistent file paths for all operating systems
        else:
            ref_path = f"/local_dependencies/{ref_path}"
            return ref_path.replace(os.sep, "/")
    else:
        return ref

def traverse(obj, output_folder):
    """Traverse the Swagger file and update $ref with http prefix."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and value.startswith("http"):
                # Process $ref if it starts with http
                obj[key] = process_reference(value, output_folder, is_main_file)
            elif isinstance(value, (dict, list)):
                # Recursively traverse nested dictionaries and lists
                traverse(value, output_folder)

def process_swagger_file(swagger_file_path, output_folder, is_main_file):
    """Process Swagger file, download and update dependencies, and save the modified Swagger file."""
    with open(swagger_file_path, 'r') as file:
        swagger_data = json.load(file)

    # Create a folder for local dependencies if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    # Traverse the entire Swagger file
    traverse(swagger_data, output_folder)

    # Modify Swagger file to replace specific URL prefixes
    for path, path_data in swagger_data.get("paths", {}).items():
        for method, method_data in path_data.items():
            if "$ref" in method_data and method_data["$ref"].startswith("http"):
                method_data["$ref"] = process_reference(method_data["$ref"], output_folder, is_main_file)

    # Save the modified Swagger file
    with open(swagger_file_path, 'w') as output_file:
        json.dump(swagger_data, output_file, indent=2)

    return swagger_file_path

if __name__ == "__main__":
    try:
        # Get the directory of the script
        script_directory = os.path.dirname(os.path.realpath(__file__))

        # Construct the full path to the Swagger file
        swagger_file_path = os.path.join(script_directory, "swaggerfile.json")

        # Output folder
        output_folder = os.path.join(script_directory, "local_dependencies")

        queue = Queue()
        queue.put(swagger_file_path)
        is_main_file = True
        while not queue.empty():
            current_swagger_path = queue.get()
            # Process Swagger file
            modified_swagger_path = process_swagger_file(current_swagger_path, output_folder, is_main_file)
            print(f"Swagger file processed successfully: {modified_swagger_path}")
            is_main_file = False

    except Exception as e:
        print(f"Error: {str(e)}")
