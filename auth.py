import os

_API_KEY = os.environ.get('API_KEY')


def access_api_key(api_key=None) -> bool:
    if check_environ is False or api_key == _API_KEY:
        return True
    else:
        return False


def check_environ():
    if _API_KEY is not None:
        return True
    else:
        return False
