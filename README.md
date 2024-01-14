# OAS File Dependency Resolver

This script processes a OAS file, recursively downloads and updates its dependencies specified by `$ref` URLs, and saves the modified Swagger file.

## Prerequisites

- Python 3
- `requests` library (install using `pip install requests`)

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repository.git
   cd your-repository
   ```

2. Install the required dependencies:

   ```bash
   pip install requests
   ```

3. Run the script:

   ```bash
   python your_script_name.py
   ```

4. The script will process the main Swagger file and its dependencies, downloading any missing files, updating `$ref` URLs, and saving the modified Swagger file.

## Configuration

- **Input**: The main Swagger file should be named `swaggerfile.json` and placed in the same directory as the script. Update the script if your main file has a different name or location.

- **Output**: The modified Swagger file will be saved in the `local_dependencies` folder. If this folder doesn't exist, it will be created.

## Notes

- The script processes `$ref` URLs that start with `http`. If your Swagger file uses a different prefix, modify the `process_reference` function accordingly.

- The downloaded files are saved with relative paths in the `local_dependencies` folder, except for the main Swagger file that uses `/local_dependencies` prefix.
