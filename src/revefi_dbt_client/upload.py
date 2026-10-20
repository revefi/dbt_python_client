import logging
import os
import tempfile
import zipfile
from pathlib import Path

from tenacity import Retrying, before_sleep_log, retry_if_exception, stop_after_attempt, stop_after_delay, \
    wait_exponential_jitter

from revefi_dbt_client.api_helper import MakeApiCall, is_retryable_http_status_code
from revefi_dbt_client.config import Config

# dbt related constants
_DBT_PROJECT_FILE_NAME = "dbt_project.yml"
_DBT_DEFAULT_TARGET_FOLDER_NAME = "target"

LOG = logging.getLogger(__name__)


class Uploader:
    def __init__(self, token, project_folder, target_folder, logs_folder, max_retries: int,
                 max_retry_wait_seconds: int):
        self.token = token
        self.project_folder = project_folder
        self.target_folder = target_folder
        self.logs_folder = logs_folder
        self.max_retries = max_retries
        self.max_retry_wait_seconds = max_retry_wait_seconds
        self.project_file_path = None
        self.manifest_path = None
        self.run_results_path = None
        self.catalog_path = None
        self.log_file_path = None

        self._validate()

    def _validate(self) -> None:
        # check for valid token
        if not self.token:
            raise ValueError("Missing auth token")

        # project folder must be supplied.
        if not self.project_folder:
            raise ValueError("Missing project folder")

        # make sure the project folder is a valid folder
        project_folder_path = Path(self.project_folder)
        target_folder_path = None

        # check "dbt_project.yml" file is present in the project folder
        self.project_file_path = Path(os.path.join(project_folder_path, _DBT_PROJECT_FILE_NAME))
        if not self.project_file_path.exists():
            raise ValueError(f"Unable to locate '{_DBT_PROJECT_FILE_NAME}' in the path - '{project_folder_path}'")

        target_folder_name = self.target_folder if self.target_folder else _DBT_DEFAULT_TARGET_FOLDER_NAME
        if not self.target_folder:
            # default to "target" within the project folder
            self.target_folder = Path(os.path.join(project_folder_path, _DBT_DEFAULT_TARGET_FOLDER_NAME))

        target_folder_path = Path(self.target_folder)
        if not target_folder_path.exists():
            raise ValueError(f"Unable to locate '{target_folder_name}' in the path - '{project_folder_path}'")

        if not target_folder_path.is_dir():
            raise ValueError(f"'{target_folder_name}' should be a dir")

        # check that either manifest.json or run_results.json is present
        self.manifest_path = Path(os.path.join(target_folder_path, "manifest.json"))
        self.run_results_path = Path(os.path.join(target_folder_path, "run_results.json"))
        self.catalog_path = Path(os.path.join(target_folder_path, "catalog.json"))

        # if log files are specified, check the log folder
        if self.logs_folder:
            logs_folder_path = Path(self.logs_folder)
            if not logs_folder_path.is_dir():
                raise ValueError(f"Invalid logs folder: {self.logs_folder}")
            self.log_file_path = os.path.join(logs_folder_path, "dbt.log")

        if not self.manifest_path.exists():
            raise ValueError(f"Unable to locate 'manifest.json' in the path - '{target_folder_path}'")

        if not self.run_results_path.exists():
            raise ValueError(f"Unable to locate 'run_results.json' in the path - '{target_folder_path}'")

    def upload(self) -> None:
        zip_file_path = self._create_zip()
        contents = self._read_zip_contents(zip_file_path)
        self._retrying()(MakeApiCall, Config.get_api_endpoint(), self.token, contents)

    def _retrying(self) -> Retrying:
        return Retrying(
            retry=retry_if_exception(is_retryable_http_status_code),
            stop=stop_after_attempt(self.max_retries + 1) | stop_after_delay(self.max_retry_wait_seconds),
            # exponential backoff plus a random jitter in [0, max jitter] to avoid synchronized retries
            wait=wait_exponential_jitter(multiplier=Config.get_retry_backoff_min_seconds(),
                                         max=Config.get_retry_backoff_max_seconds(),
                                         jitter=Config.get_retry_max_jitter_seconds()),
            before_sleep=before_sleep_log(LOG, logging.WARNING),
            reraise=True,
        )

    def _read_zip_contents(self, zip_file_path) -> bytes:
        with open(zip_file_path, 'rb') as zip_file:
            contents = zip_file.read()
        return contents

    def _create_zip(self) -> str:
        file_name = "compressed.zip"

        # create random temporary file
        temporary_path = Path(tempfile.mkdtemp())

        zip_file_path = os.path.join(temporary_path, file_name)
        file_paths = [self.project_file_path]

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


def upload(token, project_folder, target_folder=None, logs_folder=None, max_retries=None,
           max_retry_wait_seconds=None):
    if max_retries is None:
        max_retries = Config.get_max_retries()
    if max_retry_wait_seconds is None:
        max_retry_wait_seconds = Config.get_max_retry_wait_seconds()
    Uploader(token, project_folder, target_folder, logs_folder, max_retries, max_retry_wait_seconds).upload()
