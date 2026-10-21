import base64
import hashlib
import logging

import requests

from revefi_dbt_client.config import Config


class ApiError(Exception):
    def __init__(self, *args, status_code: int):
        super().__init__(*args)
        self.status_code = status_code


def is_retryable_http_status_code(exception: BaseException) -> bool:
    # ValueError signals a non-transient problem (e.g. file too large), so don't retry it
    if isinstance(exception, ValueError):
        return False
    # only retry API errors that are transient (e.g. rate limiting or the server being unavailable)
    if isinstance(exception, ApiError):
        return exception.status_code in Config.get_retryable_status_codes()
    # network errors (connection refused, timeouts, ...) and anything else unexpected are retried
    return True


class MakeApiCall:
    log = logging.getLogger(__name__)

    def get_data(self, api, token, contents):
        # Send a POST request to the Next.js backend API route
        hash = hashlib.sha256(contents).hexdigest()
        # Encode the byte array in Base64
        encoded_bytes = base64.b64encode(contents)
        # Convert the encoded bytes to a string
        encoded_string = encoded_bytes.decode('utf-8')

        if len(contents) > 64 * 1024 * 1024:
            raise ValueError("File size exceeds 64 MB. Please try again with a smaller file size")

        response = requests.post(f"{api}",
                                 json={'token': token, 'hash': hash, 'contents': [encoded_string]})

        if response.status_code != 200:
            raise ApiError("Error uploading file", {
                'error': response.text
            }, status_code=response.status_code)

        self.log.info("Upload successful: {}".format(response.text))

    def __init__(self, api, token, contents):
        self.get_data(api, token, contents)
