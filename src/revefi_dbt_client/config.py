from dynaconf import Dynaconf

_CONFIG = Dynaconf(
    envvar_prefix='REVEFI',
    environments=False,
)

_API_ENDPOINT = "https://gateway.revefi.com/api/v1/dbt/upload"
_MAX_RETRIES = 30
_MAX_RETRY_WAIT_SECONDS = 10 * 60
_IGNORE_ERRORS = True
_RETRY_BACKOFF_MIN_SECONDS = 1
_RETRY_BACKOFF_MAX_SECONDS = 30
_RETRY_MAX_JITTER_SECONDS = 5
_RETRYABLE_STATUS_CODES = (429, *range(500, 600))


class Config:

    @staticmethod
    def get_api_endpoint() -> str:
        return _CONFIG.get('API_ENDPOINT', _API_ENDPOINT)

    @staticmethod
    def get_log_level() -> str:
        return _CONFIG.get('LOG_LEVEL', 'INFO')

    @staticmethod
    def get_max_retries() -> int:
        return int(_CONFIG.get('MAX_RETRIES', _MAX_RETRIES))

    @staticmethod
    def get_max_retry_wait_seconds() -> int:
        return int(_CONFIG.get('MAX_RETRY_WAIT_SECONDS', _MAX_RETRY_WAIT_SECONDS))

    @staticmethod
    def get_ignore_errors() -> bool:
        return bool(_CONFIG.get('IGNORE_ERRORS', _IGNORE_ERRORS))

    @staticmethod
    def get_retry_backoff_min_seconds() -> float:
        return float(_CONFIG.get('RETRY_BACKOFF_MIN_SECONDS', _RETRY_BACKOFF_MIN_SECONDS))

    @staticmethod
    def get_retry_backoff_max_seconds() -> float:
        return float(_CONFIG.get('RETRY_BACKOFF_MAX_SECONDS', _RETRY_BACKOFF_MAX_SECONDS))

    @staticmethod
    def get_retry_max_jitter_seconds() -> float:
        return float(_CONFIG.get('RETRY_MAX_JITTER_SECONDS', _RETRY_MAX_JITTER_SECONDS))

    @staticmethod
    def get_retryable_status_codes() -> tuple[int, ...]:
        codes = _CONFIG.get('RETRYABLE_STATUS_CODES', _RETRYABLE_STATUS_CODES)
        if isinstance(codes, str):
            codes = [code for code in codes.split(',') if code.strip()]
        elif isinstance(codes, int):
            codes = [codes]
        return tuple(int(code) for code in codes)
