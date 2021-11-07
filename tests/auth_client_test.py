import os
from unittest.mock import patch

from twitterapiv2.auth_client import AuthClient


MOCK_KEY = "xvz1evFS4wEEPTGEFPHBog"
MOCK_SECRET = "L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg"
MOCK_CRED = "eHZ6MWV2RlM0d0VFUFRHRUZQSEJvZzpMOHFxOVBaeVJnNmllS0dFS2hab2xHQzB2SldMdzhpRUo4OERSZHlPZw=="  # noqa


def test_encoded_credentials() -> None:
    client = AuthClient()
    env = {
        "TW_CONSUMER_KEY": MOCK_KEY,
        "TW_CONSUMER_SECRET": MOCK_SECRET,
    }
    with patch.dict(os.environ, env):
        result = client.encoded_credentials()
        assert result == MOCK_CRED


def test_set_bearer_token() -> None:
    client = AuthClient()

    # TODO: Mock this. In the meantime run a live test with valid creds
    from secretbox import SecretBox

    SecretBox(auto_load=True)

    with patch.dict(os.environ):
        # Remove any pre-loaded value for sanitary test
        os.environ.pop("TW_BEARER_TOKEN", None)

        client.set_bearer_token()

        assert os.environ["TW_BEARER_TOKEN"]
