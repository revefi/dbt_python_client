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
