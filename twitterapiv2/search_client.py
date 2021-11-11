import logging
import os
from datetime import datetime
from typing import Dict
from typing import Optional

from twitterapiv2.http import Http
from twitterapiv2.model.recent.recent import Recent
from twitterapiv2.model.responseheader import ResponseHeader

_BEARER_TOKEN = "TW_BEARER_TOKEN"


class SearchClient(Http):

    RECENT = "https://api.twitter.com/2/tweets/search/recent"

    def __init__(self, num_pools: int = 10) -> None:
        super().__init__(num_pools=num_pools)
        self.log = logging.getLogger(__name__)
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

    def _headers(self) -> Dict[str, str]:
        """Build headers with TW_BEARER_TOKEN from environ"""
        return {"Authorization": "Bearer " + os.getenv(_BEARER_TOKEN, "")}

    def search_recent(
        self,
        query: str,
        *,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        expansions: Optional[str] = None,
        media_fields: Optional[str] = None,
        place_fields: Optional[str] = None,
        poll_fields: Optional[str] = None,
        tweet_fields: Optional[str] = None,
        user_fields: Optional[str] = None,
    ) -> Recent:
        """Search tweets from up to the last seven days matching parameters"""
        fields = {
            "query": query,
            "max_results": max_results,
            "next_token": next_token,
            "start_time": str(start_time),
            "end_time": str(end_time),
            "since_id": since_id,
            "until_id": until_id,
            "expansions": expansions,
            "media.fields": media_fields,
            "place.fields": place_fields,
            "poll.fields": poll_fields,
            "tweet.fields": tweet_fields,
            "user.fields": user_fields,
        }
        clean_fields = {key: value for key, value in fields.items() if value}

        result = self.http.request("GET", self.RECENT, clean_fields, self._headers())
        self._last_response = ResponseHeader.build_from(result)

        return Recent.build_obj(self.data2dict(result.data))


if __name__ == "__main__":
    from twitterapiv2.auth_client import AuthClient
    from secretbox import SecretBox

    SecretBox(auto_load=True)
    logging.basicConfig(level="DEBUG")

    auth = AuthClient()
    client = SearchClient()

    auth.set_bearer_token()
    result = client.search_recent("#NaNoWriMo", max_results=10)
    print(client.limit_remaining)
    print(client.limit_reset)
