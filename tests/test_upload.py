from unittest.mock import Mock

import pytest
import requests

from revefi_dbt_client import upload
from revefi_dbt_client.api_helper import ApiError

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


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture(scope='function')
def fake_clock(monkeypatch):
    clock = FakeClock()
    monkeypatch.setattr('time.monotonic', clock.monotonic)
    monkeypatch.setattr('time.sleep', clock.sleep)
    return clock


@pytest.fixture(scope='function')
def fixed_jitter(monkeypatch):
    """Makes the retry jitter deterministic: always half of the jitter range."""
    monkeypatch.setattr('random.uniform', lambda low, high: (low + high) / 2)


@pytest.fixture(scope='function')
def flaky_post(monkeypatch):
    """Fails the first `failures` calls with a 500, then succeeds."""
    state = {'calls': 0, 'failures': 0}

    def mock_response(*args, **kwargs):
        state['calls'] += 1
        response = Mock()
        response.status_code = 500 if state['calls'] <= state['failures'] else 200
        response.text = 'server error' if response.status_code == 500 else 'ok'
        return response

    monkeypatch.setattr(requests, 'post', mock_response)
    return state


def test_upload_retries_until_success(fake_clock, flaky_post, valid_project_folder):
    flaky_post['failures'] = 2
    upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=3)
    assert flaky_post['calls'] == 3
    assert len(fake_clock.sleeps) == 2


def test_upload_uses_exponential_backoff_with_jitter(fake_clock, fixed_jitter, flaky_post, valid_project_folder):
    flaky_post['failures'] = 100
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=4)
    # exponential backoff of 1, 2, 4, 8 seconds plus 2.5s of jitter
    assert fake_clock.sleeps == [3.5, 4.5, 6.5, 10.5]


def test_upload_jitter_varies_retry_waits(fake_clock, flaky_post, valid_project_folder):
    flaky_post['failures'] = 100
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=20)
    backoffs = [min(2 ** attempt, 30) for attempt in range(20)]
    jitters = [sleep - backoff for sleep, backoff in zip(fake_clock.sleeps, backoffs)]
    assert all(0 <= jitter <= 5 for jitter in jitters)
    # jitter is randomly generated, so it should differ between retries
    assert len(set(jitters)) > 1


def test_upload_backoff_is_capped_at_30_seconds(fake_clock, fixed_jitter, flaky_post, valid_project_folder):
    flaky_post['failures'] = 100
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=10)
    # the 30s cap applies to the backoff including jitter
    assert max(fake_clock.sleeps) == 30


def test_upload_stops_after_max_retries(fake_clock, flaky_post, valid_project_folder):
    flaky_post['failures'] = 100
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=2)
    assert flaky_post['calls'] == 3


def test_upload_without_retries(fake_clock, flaky_post, valid_project_folder):
    flaky_post['failures'] = 100
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=0)
    assert flaky_post['calls'] == 1
    assert fake_clock.sleeps == []


def test_upload_stops_after_max_retry_wait_seconds(fake_clock, fixed_jitter, flaky_post, valid_project_folder):
    flaky_post['failures'] = 100
    # backoff sleeps 3.5, 4.5, 6.5 -> elapsed 14.5s after the 4th attempt, which exceeds the 10s budget
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=100, max_retry_wait_seconds=10)
    assert flaky_post['calls'] == 4
    assert fake_clock.now == 14.5


@pytest.mark.parametrize('error', [
    requests.ConnectionError("connection refused"),
    requests.Timeout("timed out"),
    OSError("network unreachable"),
    RuntimeError("unexpected"),
    Exception("Error uploading file"),
])
def test_upload_retries_non_value_errors(fake_clock, monkeypatch, valid_project_folder, error):
    calls = []

    def mock_api_call(*args, **kwargs):
        calls.append(args)
        if len(calls) <= 2:
            raise error

    monkeypatch.setattr(upload, 'MakeApiCall', mock_api_call)
    upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=5)
    assert len(calls) == 3


def test_upload_reraises_last_exception_when_retries_exhausted(fake_clock, monkeypatch, valid_project_folder):
    calls = []

    def mock_api_call(*args, **kwargs):
        calls.append(args)
        raise RuntimeError(f"failure {len(calls)}")

    monkeypatch.setattr(upload, 'MakeApiCall', mock_api_call)
    with pytest.raises(RuntimeError, match='failure 3'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=2)
    assert len(calls) == 3


def test_upload_does_not_retry_value_error(fake_clock, monkeypatch, valid_project_folder):
    calls = []

    def mock_api_call(*args, **kwargs):
        calls.append(args)
        raise ValueError("File size exceeds 64 MB. Please try again with a smaller file size")

    monkeypatch.setattr(upload, 'MakeApiCall', mock_api_call)
    with pytest.raises(ValueError, match='File size exceeds 64 MB'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=5)
    assert len(calls) == 1
    assert fake_clock.sleeps == []


def test_upload_does_not_retry_validation_errors(fake_clock, flaky_post, project_folder):
    with pytest.raises(ValueError):
        upload.upload(AUTH_TOKEN, project_folder, max_retries=5)
    assert flaky_post['calls'] == 0


def test_upload_uses_config_defaults_for_retries(monkeypatch, valid_project_folder):
    captured = {}

    class FakeUploader:
        def __init__(self, *args):
            captured['args'] = args

        def upload(self):
            pass

    monkeypatch.setattr(upload, 'Uploader', FakeUploader)
    upload.upload(AUTH_TOKEN, valid_project_folder)
    assert captured['args'] == (AUTH_TOKEN, valid_project_folder, None, None, 30, 10 * 60)


def test_upload_uses_backoff_and_jitter_from_config(fake_clock, fixed_jitter, flaky_post, monkeypatch,
                                                    valid_project_folder):
    monkeypatch.setattr(upload.Config, 'get_retry_backoff_min_seconds', staticmethod(lambda: 2))
    monkeypatch.setattr(upload.Config, 'get_retry_backoff_max_seconds', staticmethod(lambda: 10))
    monkeypatch.setattr(upload.Config, 'get_retry_max_jitter_seconds', staticmethod(lambda: 1))
    flaky_post['failures'] = 100
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=4)
    # backoff of 2, 4, 8, 16 seconds plus 0.5s of jitter, capped at 10 seconds
    assert fake_clock.sleeps == [2.5, 4.5, 8.5, 10]


@pytest.fixture(scope='function')
def server_down_for(fake_clock, monkeypatch):
    """Server returns 503 until `seconds` have elapsed on the fake clock, emulating a deployment."""
    state = {'seconds': 0, 'calls': 0}

    def mock_response(*args, **kwargs):
        state['calls'] += 1
        response = Mock()
        response.status_code = 503 if fake_clock.now < state['seconds'] else 200
        response.text = 'service unavailable' if response.status_code == 503 else 'ok'
        return response

    monkeypatch.setattr(requests, 'post', mock_response)
    return state


@pytest.mark.parametrize('deployment_seconds', [6 * 60, 9 * 60])
def test_upload_with_default_config_survives_deployment(fake_clock, server_down_for, valid_project_folder,
                                                        deployment_seconds):
    server_down_for['seconds'] = deployment_seconds
    upload.upload(AUTH_TOKEN, valid_project_folder)
    # the client resumes within one capped backoff (30s) of the server coming back
    assert deployment_seconds <= fake_clock.now < deployment_seconds + 30


def test_upload_with_default_config_gives_up_after_10_minutes(fake_clock, server_down_for, valid_project_folder):
    server_down_for['seconds'] = 60 * 60
    with pytest.raises(Exception, match='Error uploading file'):
        upload.upload(AUTH_TOKEN, valid_project_folder)
    assert 10 * 60 <= fake_clock.now < 10 * 60 + 30
    # the retry window, not the attempt count, stops the retries
    assert server_down_for['calls'] < 30 + 1


@pytest.fixture(scope='function')
def failing_post(monkeypatch):
    """Fails the first `failures` calls with `status_code`, then succeeds."""
    state = {'calls': 0, 'failures': 0, 'status_code': 500}

    def mock_response(*args, **kwargs):
        state['calls'] += 1
        response = Mock()
        response.status_code = state['status_code'] if state['calls'] <= state['failures'] else 200
        response.text = 'error' if response.status_code != 200 else 'ok'
        return response

    monkeypatch.setattr(requests, 'post', mock_response)
    return state


@pytest.mark.parametrize('status_code', [429, 500, 501, 502, 503, 504, 505, 599])
def test_upload_retries_transient_status_codes(fake_clock, failing_post, valid_project_folder, status_code):
    failing_post.update(failures=2, status_code=status_code)
    upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=5)
    assert failing_post['calls'] == 3


@pytest.mark.parametrize('status_code', [400, 401, 404, 413, 422, 499, 600])
def test_upload_does_not_retry_permanent_status_codes(fake_clock, failing_post, valid_project_folder, status_code):
    failing_post.update(failures=100, status_code=status_code)
    with pytest.raises(ApiError) as exc_info:
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=5)
    assert exc_info.value.status_code == status_code
    assert failing_post['calls'] == 1
    assert fake_clock.sleeps == []


def test_upload_uses_retryable_status_codes_from_config(fake_clock, failing_post, monkeypatch, valid_project_folder):
    monkeypatch.setattr(upload.Config, 'get_retryable_status_codes', staticmethod(lambda: (401,)))
    failing_post.update(failures=2, status_code=401)
    upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=5)
    assert failing_post['calls'] == 3

    failing_post.update(calls=0, failures=100, status_code=500)
    with pytest.raises(ApiError):
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=5)
    assert failing_post['calls'] == 1


def test_api_error_keeps_message_and_status_code(fake_clock, failing_post, valid_project_folder):
    failing_post.update(failures=100, status_code=401)
    with pytest.raises(ApiError) as exc_info:
        upload.upload(AUTH_TOKEN, valid_project_folder, max_retries=0)
    assert exc_info.value.args == ("Error uploading file", {'error': 'error'})
    assert exc_info.value.status_code == 401
