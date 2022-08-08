import os
from posixpath import join as urljoin


class AirviewApiHelpers:
    URL_PREFIX_ENV_VAR_NAME="API_URL_PREFIX"

    @staticmethod
    def get_api_url_prefix(api_uri: str) -> str:
        url_prefix: str = os.getenv(AirviewApiHelpers.URL_PREFIX_ENV_VAR_NAME, "/")
        return urljoin(url_prefix, api_uri.lstrip("/"))
