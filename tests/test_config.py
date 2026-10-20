import pytest

from revefi_dbt_client import config
from revefi_dbt_client.config import Config


def test_get_api_endpoint():
    assert Config.get_api_endpoint() == "https://gateway.revefi.com/api/uploadFile"


def test_get_max_retries():
    assert Config.get_max_retries() == 30


def test_get_max_retry_wait_seconds():
    assert Config.get_max_retry_wait_seconds() == 10 * 60


def test_get_ignore_errors():
    assert Config.get_ignore_errors() is True


def test_get_retry_backoff_min_seconds():
    assert Config.get_retry_backoff_min_seconds() == 1


def test_get_retry_backoff_max_seconds():
    assert Config.get_retry_backoff_max_seconds() == 30


def test_get_retry_max_jitter_seconds():
    assert Config.get_retry_max_jitter_seconds() == 5


def test_get_retryable_status_codes():
    assert Config.get_retryable_status_codes() == (429, *range(500, 600))


@pytest.mark.parametrize('value, expected', [
    ([429, 503], (429, 503)),
    ('429, 503', (429, 503)),
    ('503', (503,)),
    (503, (503,)),
])
def test_get_retryable_status_codes_from_config(monkeypatch, value, expected):
    monkeypatch.setattr(config._CONFIG, 'RETRYABLE_STATUS_CODES', value, raising=False)
    assert Config.get_retryable_status_codes() == expected
