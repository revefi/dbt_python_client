import base64
import hashlib
import logging

import requests


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
            raise Exception("Error uploading file", {
                'error': response.text
            })

        self.log.info("Upload successful: {}".format(response.text))

    def __init__(self, api, token, contents):
        self.get_data(api, token, contents)
