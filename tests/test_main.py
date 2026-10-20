import sys

import pytest

from revefi_dbt_client.main import main


@pytest.fixture(scope='function')
def mock_upload(monkeypatch):
    monkeypatch.setattr('revefi_dbt_client.main.upload', lambda *args, **kwargs: None)


def test_main_with_legacy_parser(mock_upload, monkeypatch):
    argv = 'revefi-dbt-client dbt --token definitely-a-real-token --project_folder /path/to/project/dir'.split(' ')
    monkeypatch.setattr(target=sys, name='argv', value=argv)
    main(legacy_parser=True)


def test_main_with_v2_parser(mock_upload, monkeypatch):
    argv = 'revefi-dbt-client --token definitely-a-real-token --project_folder /path/to/project/dir'.split(' ')
    monkeypatch.setattr(target=sys, name='argv', value=argv)
    main()


def test_main_passes_retry_args_to_upload(monkeypatch):
    captured = {}
    monkeypatch.setattr('revefi_dbt_client.main.upload', lambda *args, **kwargs: captured.update(args=args))
    argv = ('revefi-dbt-client --token t --project_folder /p '
            '--max-retries 2 --max-retry-wait-seconds 30').split(' ')
    monkeypatch.setattr(target=sys, name='argv', value=argv)
    main()
    assert captured['args'] == ('t', '/p', None, None, 2, 30)
