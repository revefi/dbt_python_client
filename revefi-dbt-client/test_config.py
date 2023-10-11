from upload import Config


def test_get_api_endpoint():
    assert Config.get_api_endpoint() == "https://gateway.revefi.com/api/uploadFile"


def test_get_chunk_size():
    assert Config.get_chunk_size() == 524288
