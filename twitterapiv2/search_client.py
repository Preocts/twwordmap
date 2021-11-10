import logging
import os
from typing import Dict
from typing import List

from twitterapiv2.http import Http
from twitterapiv2.model.tweet.tweet import Tweet

_BEARER_TOKEN = "TW_BEARER_TOKEN"


class SearchClient(Http):
    def __init__(self, num_pools: int = 10) -> None:
        super().__init__(num_pools=num_pools)
        self.log = logging.getLogger(__name__)

    def _headers(self) -> Dict[str, str]:
        """Build headers with TW_BEARER_TOKEN from environ"""
        return {"Authorization": "Bearer " + os.getenv(_BEARER_TOKEN, "")}

    def search_recent(self) -> List[Tweet]:
        """Tweet from, up to, the last seven days matching parameters"""
        # TODO: pagination loop
        # result = self.http.request("GET")
        pass
