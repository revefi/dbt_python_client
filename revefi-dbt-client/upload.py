import base64
import hashlib
import requests
import argparse
import os
import zipfile
import tempfile
from pathlib import Path


API_ENDPOINT = "https://gateway.revefi.com/api/uploadFile"


class MakeApiCall:

    def get_data(self, api, token, contents):
        hash = hashlib.sha256(contents).hexdigest()
        # Encode the byte array in Base64
        encoded_bytes = base64.b64encode(contents)
        # Convert the encoded bytes to a string
        encoded_string = encoded_bytes.decode('utf-8')
        response = requests.post(f"{api}", data={'token': token, 'contents': encoded_string, 'hash': hash})
        if response.status_code == 200:
            print("Upload successful.")
        else:
            error(f"Unable to upload. Status code - {response.status_code}")

    def __init__(self, api, token, contents):
        self.get_data(api, token, contents)


def error(msg: str) -> None:
    print("[ERROR] {msg}".format(msg=msg))


class RevefiCli:
    def __init__(self, token, target_folder, logs_folder, project_name, endpoint):
        self.token = token
        self.target_folder = target_folder
        self.logs_folder = logs_folder
        self.project_name = project_name if project_name is not None else 'dbt-project'
        self.endpoint = endpoint
        self.manifest_path = None
        self.run_results_path = None
        self.catalog_path = None
        self.log_file_path = None

    def is_valid(self) -> None:
        # check for valid token
        if not self.token:
            error("Missing token")

        if not self.target_folder:
            error("Missing target folder")

        target_folder_path = Path(self.target_folder)
        if not target_folder_path.is_dir():
            error(f"Invalid target folder: {self.target_folder}")

        # check that either manifest.json or run_results.json is present
        self.manifest_path = Path(os.path.join(target_folder_path, "manifest.json"))
        self.run_results_path = Path(os.path.join(target_folder_path,  "run_results.json"))
        self.catalog_path = Path(os.path.join(target_folder_path,  "catalog.json"))

        # if log files are specified, check the log folder
        if self.logs_folder:
            logs_folder_path = Path(self.logs_folder)
            if not logs_folder_path.is_dir():
                error(f"Invalid logs folder: {self.logs_folder}")
            self.log_file_path = os.path.join(logs_folder_path, "dbt.log")

        if not self.manifest_path.exists() or not self.run_results_path.exists():
            raise RuntimeError(
                f"Unable to locate 'manifest.json' or 'run_results.json' in the path - '{target_folder_path}'")

    def deploy(self) -> None:
        zip_file_path = self._create_zip()
        contents = self._read_zip_contents(zip_file_path)
        MakeApiCall(API_ENDPOINT, self.token, contents)

    def _read_zip_contents(self, zip_file_path) -> bytes:
        with open(zip_file_path, 'rb') as zip_file:
            contents = zip_file.read()
        return contents

    def _generate_project_file_contents(self) -> str:
        return f"name: '{self.project_name}'"

    def _create_zip(self) -> str:
        file_name = "compressed.zip"
        project_file_name = "dbt_project.yml"

        # create random temporary file
        temporary_path = Path(tempfile.mkdtemp())

        # Save the content of the project in a new file
        project_file_path = os.path.join(temporary_path, project_file_name)
        with open(project_file_path, "w") as project_file:
            project_file.write(self._generate_project_file_contents())

        zip_file_path = os.path.join(temporary_path, file_name)
        file_paths = [project_file_path]

        if os.path.exists(self.manifest_path):
            file_paths.append(self.manifest_path)
        if os.path.exists(self.run_results_path):
            file_paths.append(self.run_results_path)
        if os.path.exists(self.catalog_path):
            file_paths.append(self.catalog_path)

        # add logs if supplied
        if self.log_file_path is not None and os.path.exists(self.log_file_path):
            file_paths.append(self.log_file_path)

        # create zip file
        with zipfile.ZipFile(zip_file_path, "w") as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path, os.path.basename(file_path))

        return zip_file_path


def main():
    parser = argparse.ArgumentParser(description="revefi dbt cli")
    subparsers = parser.add_subparsers(dest='command')

    dbt_parser = subparsers.add_parser('dbt')
    dbt_parser.add_argument("--token", required=True, type=str, help="validation token")
    dbt_parser.add_argument("--target_folder", required=True, type=str, help="target folder for the dbt run")
    dbt_parser.add_argument("--logs_folder", required=False, type=str, help="log folder from the dbt run")
    dbt_parser.add_argument("--project_name", required=False, type=str, help="project name (example: my-project)")
    dbt_parser.add_argument("--endpoint", required=False, type=str, help="endpoint for API")
    args = parser.parse_args()
    deployer = RevefiCli(args.token, args.target_folder,
                         args.logs_folder, args.project_name, args.endpoint)
    deployer.is_valid()
    deployer.deploy()


if __name__ == "__main__":
    main()
