from unittest.mock import Mock

import pytest
import requests

import upload

AUTH_TOKEN = 'definitely_a_real_token'


@pytest.fixture(scope='function')
def mock_post(monkeypatch):
    def mock_response(*args, **kwargs):
        response = Mock()
        response.status_code = 200
        return response

    monkeypatch.setattr(requests, 'post', mock_response)


@pytest.fixture(scope='function')
def project_folder(tmpdir):
    return tmpdir.mkdir('fake_project_folder')


@pytest.fixture(scope='function')
def dbt_project_yml(project_folder):
    dbt_project_yml = project_folder.join('dbt_project.yml')
    dbt_project_yml.write('emulate data for a dbt_project.yml')
    return dbt_project_yml


@pytest.fixture(scope='function')
def target_folder(project_folder):
    return project_folder.mkdir('target')


@pytest.fixture(scope='function')
def manifest_json(target_folder):
    manifest_json = target_folder.join('manifest.json')
    manifest_json.write('emulate data for a manifest.json')
    return manifest_json


@pytest.fixture(scope='function')
def run_results_json(target_folder):
    run_results_json = target_folder.join('run_results.json')
    run_results_json.write('emulate data for a run_results.json')
    return project_folder


@pytest.fixture(scope='function')
def valid_project_folder(project_folder, dbt_project_yml, manifest_json, run_results_json):
    return project_folder


def test_upload_works(mock_post, valid_project_folder):
    upload.upload(AUTH_TOKEN, valid_project_folder)


def test_upload_fails_without_token(mock_post, valid_project_folder):
    with pytest.raises(ValueError) as exc_info:
        upload.upload(None, valid_project_folder)
    assert str(exc_info.value) == 'Missing auth token'


def test_upload_fails_without_project_folder(mock_post):
    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, None)
    assert str(exc_info.value) == 'Missing project folder'


def test_upload_fails_without_dbt_project_yml(mock_post, project_folder):
    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, project_folder)
    assert str(exc_info.value) == f"Unable to locate 'dbt_project.yml' in the path - '{project_folder}'"


def test_upload_fails_without_target_folder(mock_post, project_folder, dbt_project_yml):
    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, project_folder)
    assert str(exc_info.value) == f"Unable to locate 'target' in the path - '{project_folder}'"

    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, project_folder, 'custom_target_folder')
    assert str(exc_info.value) == f"Unable to locate 'custom_target_folder' in the path - '{project_folder}'"


def test_upload_fails_with_target_folder_that_is_not_a_folder(mock_post, project_folder, dbt_project_yml):
    project_folder.join('target').write('')
    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, project_folder)
    assert str(exc_info.value) == f"'target' should be a dir"

    custom_target_folder = project_folder.join('custom_target_folder')
    custom_target_folder.write('')
    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, project_folder, custom_target_folder)
    assert str(exc_info.value) == f"'{custom_target_folder}' should be a dir"


def test_upload_fails_without_manifest_json(mock_post, project_folder, dbt_project_yml, target_folder):
    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, project_folder)
    assert str(exc_info.value) == f"Unable to locate 'manifest.json' in the path - '{target_folder}'"


def test_upload_fails_without_run_results_json(mock_post, project_folder, dbt_project_yml, target_folder,
                                               manifest_json):
    with pytest.raises(ValueError) as exc_info:
        upload.upload(AUTH_TOKEN, project_folder)
    assert str(exc_info.value) == f"Unable to locate 'run_results.json' in the path - '{target_folder}'"
