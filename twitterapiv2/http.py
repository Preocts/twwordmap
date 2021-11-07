import json
import logging
from typing import Any
from typing import Dict

import urllib3


class Http:
    """Provides HTTPS connection pool and REST methods"""

    def __init__(self, num_pools: int = 10) -> None:
        self.log = logging.getLogger(__name__)
        self.http = self.connection(num_pools)

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

    def data2dict(self, data: bytes) -> Dict[str, Any]:
        """Converts response data to a dict"""
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as err:
            self.log.error("Error converting data to dict: '%s'", err)
            return {"error": data}

    def get(self) -> None:
        """Override for specific implementations"""
        raise NotImplementedError

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
