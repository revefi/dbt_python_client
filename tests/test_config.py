from revefi_dbt_client.config import Config


def test_get_api_endpoint():
    assert Config.get_api_endpoint() == "https://gateway.revefi.com/api/uploadFile"
