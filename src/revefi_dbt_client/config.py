from dynaconf import Dynaconf

_CONFIG = Dynaconf(
    envvar_prefix='REVEFI',
    environments=False,
)

_API_ENDPOINT = "https://gateway.revefi.com/api/uploadFile"


class Config:

    @staticmethod
    def get_api_endpoint() -> str:
        return _CONFIG.get('API_ENDPOINT', _API_ENDPOINT)

    @staticmethod
    def get_log_level() -> str:
        return _CONFIG.get('LOG_LEVEL', 'INFO')
