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
            self.log.error("File size exceeds 64 MB. Please try again with a smaller file size.")
            return
        response = requests.post(f"{api}",
                                 json={'token': token, 'hash': hash, 'contents': [encoded_string]})

        if response.status_code == 200:
            self.log.info("Upload successful.")
        else:
            self.log.error(f"[{response.status_code}] Unable to upload - {response}")
            return

    def __init__(self, api, token, contents):
        self.get_data(api, token, contents)
