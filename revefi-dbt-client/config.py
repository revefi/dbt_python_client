from dynaconf import Dynaconf

_CONFIG = Dynaconf(
    envvar_prefix='REVEFI',
    environments=False,
)

_API_ENDPOINT = "https://gateway.revefi.com/api/uploadFile"
_CHUNK_SIZE = 524288  # 0.5MB chunk size


class Config:

    @staticmethod
    def get_api_endpoint() -> str:
        return _CONFIG.get('API_ENDPOINT', _API_ENDPOINT)

    @staticmethod
    def get_chunk_size() -> int:
        return _CONFIG.get('CHUNK_SIZE', _CHUNK_SIZE)
