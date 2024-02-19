import json
import os
import requests
from urllib.parse import urlparse

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        with requests.get(url, stream=True) as response:
            with open(local_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

def update_refs_with_local_dependency(openapi_file, local_folder):
    with open(openapi_file, 'r') as file:
        spec = json.load(file)

    update_refs_in_paths(spec, local_folder)
    update_refs_in_responses(spec, local_folder)
    update_refs_in_request_bodies(spec, local_folder)

    with open(openapi_file, 'w') as file:
        json.dump(spec, file, indent=2)

def update_refs_in_paths(spec, local_folder):
    for path, definition in find_refs(spec.get('paths', {})):
        update_ref(definition, local_folder)

def update_refs_in_responses(spec, local_folder):
    responses = spec.get('components', {}).get('responses', {})
    for response_name, response_def in responses.items():
        for path, definition in find_refs(response_def):
            update_ref(definition, local_folder)

def update_refs_in_request_bodies(spec, local_folder):
    request_bodies = spec.get('components', {}).get('requestBodies', {})
    for body_name, body_def in request_bodies.items():
        for path, definition in find_refs(body_def):
            update_ref(definition, local_folder)

def update_ref(definition, local_folder):
    url = definition.get('$ref')
    if url:
        modified_url = modify_url(url)
        filename = urlparse(modified_url).path.rsplit('/', 1)[-1]

        local_path = os.path.join(local_folder, filename)
        download_file(modified_url, local_path)
        definition['$ref'] = f"local_dependencies/{filename}"

        update_local_dependency(local_path, local_folder)

def update_local_dependency(local_path, local_folder):
    with open(local_path, 'r') as file:
        dependency_spec = json.load(file)

    for path, definition in find_refs(dependency_spec):
        url = definition.get('$ref')
        if url:
            modified_url = modify_url(url)
            filename = urlparse(modified_url).path.rsplit('/', 1)[-1]

            dependency_local_path = os.path.join(local_folder, filename)

            # Check if the nested file already exists in local dependencies
            if not os.path.exists(dependency_local_path):
                download_file(modified_url, dependency_local_path)
                definition['$ref'] = f"local_dependencies/{filename}"

                update_local_dependency(dependency_local_path, local_folder)

    with open(local_path, 'w') as file:
        json.dump(dependency_spec, file, indent=2)

def modify_url(url):
    if "http://127.0.0.1:10000" in url:
        return url.replace("http://127.0.0.1:10000", "https://developer-specs.company-information.service.gov.uk")
    return url

def find_refs(obj, path=''):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == '$ref':
                yield path, obj
            else:
                yield from find_refs(value, f"{path}/{key}")

    elif isinstance(obj, list):
        for i, element in enumerate(obj):
            yield from find_refs(element, f"{path}/{i}")

if __name__ == "__main__":
    openapi_file = "your_openapi_file.json"
    local_folder = "local_dependencies"

    script_path = os.path.dirname(os.path.abspath(__file__))
    openapi_file_path = os.path.join(script_path, openapi_file)
    local_folder_path = os.path.join(script_path, local_folder)

    if not os.path.exists(local_folder_path):
        os.makedirs(local_folder_path)

    update_refs_with_local_dependency(openapi_file_path, local_folder_path)
