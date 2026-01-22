from urllib.parse import urlparse


def is_valid_base_url(url: str) -> bool:
    """
    Validates if the given string is a valid URL.
    :param url: the string to be validated
    :return: a boolean indicating if the given string is a valid URL
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Must have scheme and netloc
    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.netloc:
        return False

    # Path must be empty or "/"
    if parsed.path not in ("", "/"):
        return False

    # No query or fragment
    if parsed.query or parsed.fragment:
        return False

    return True
