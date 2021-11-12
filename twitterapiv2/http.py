import json
import logging
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

import urllib3

from twitterapiv2.model.responseheader import ResponseHeader


class InvalidResponseError(Exception):
    ...


class Http:
    """
    Provides HTTPS connection pool and REST methods

    Raises:
        InvalidResponseError - Raised on all failed status codes
    """

    def __init__(self, num_pools: int = 10) -> None:
        self.log = logging.getLogger(__name__)
        self.http = self.connection(num_pools)
        self._last_response: Optional[ResponseHeader] = None

    @property
    def limit_remaining(self) -> int:
        """Number of calls remaining before next limit reset"""
        if self._last_response is None:
            return 1
        else:
            return int(self._last_response.x_rate_limit_remaining)

    @property
    def limit_reset(self) -> datetime:
        """Datetime of next limit reset"""
        if self._last_response is None:
            return datetime.now()
        else:
            return datetime.fromtimestamp(int(self._last_response.x_rate_limit_reset))

    def connection(self, num_pools: int = 10) -> urllib3.PoolManager:
        """Returns HTTP pool manager with retries and backoff"""
        return urllib3.PoolManager(
            num_pools=num_pools,
            retries=urllib3.Retry(
                total=3,
                backoff_factor=2,
                raise_on_status=True,
                raise_on_redirect=True,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            ),
        )

    def _data2dict(self, data: bytes) -> Dict[str, Any]:
        """Converts response data to a dict"""
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as err:
            self.log.error("Error converting data to dict: '%s'", err)
            return {"error": data}

    def get(
        self,
        url: str,
        fields: Dict[str, Any],
        headers: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Override for specific implementations"""
        resp = self.http.request("GET", url, fields, headers)
        self._last_response = ResponseHeader.build_from(resp)
        if resp.status not in range(200, 300):
            self.log.error("Failed: %s", resp.data)
            raise InvalidResponseError(f"{resp.status} on GET to {url}")
        return self._data2dict(resp.data)

    def post(self) -> None:
        """Override for specific implementations"""
        raise NotImplementedError

    def put(self) -> None:
        """Override for specific implementations"""
        raise NotImplementedError

    def patch(self) -> None:
        """Override for specific implementations"""
        raise NotImplementedError

    def delete(self) -> None:
        """Override for specific implementations"""
        raise NotImplementedError
