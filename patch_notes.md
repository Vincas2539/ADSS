### 1.33

Compatibility and CI updates:

- Fixed Python 3.8/3.9 type hint compatibility in authentication download method.
- Updated dependency markers in pyproject.toml to preserve support for Python 3.8/3.9 while keeping newer versions supported.
- Implemented comprehensive test suite covering models, utilities, exceptions, authentication and client.
- Expanded CI matrix to test Python 3.8, 3.9, 3.10, 3.11 and 3.12.
- CI now installs project extras (`test` and `dev`) and runs pytest.

### 1.32

Renamed 

download_image() -> download_file()

### 1.31

Renamed image collection methods for clarity:

get_image_collections() -> get_collections()
get_image_collection -> get_collection()
list_image_files() -> list_files()
