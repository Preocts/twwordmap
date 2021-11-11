import logging
import os
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from twitterapiv2.http import Http
from twitterapiv2.model.recent.recent import Recent

_BEARER_TOKEN = "TW_BEARER_TOKEN"


class SearchClient(Http):

    RECENT = "https://api.twitter.com/2/tweets/search/recent"

    def __init__(self, num_pools: int = 10) -> None:
        super().__init__(num_pools=num_pools)
        self.log = logging.getLogger(__name__)

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
        fields: Dict[str, Any] = {"query": query}
        fields.update({"max_results": max_results} if max_results else {})
        fields.update({"next_token": next_token} if next_token else {})
        fields.update({"start_time": str(start_time)} if start_time else {})
        fields.update({"end_time": str(end_time)} if end_time else {})
        fields.update({"since_id": since_id} if since_id else {})
        fields.update({"until_id": until_id} if until_id else {})
        fields.update({"expansions": expansions} if expansions else {})
        fields.update({"media.fields": media_fields} if media_fields else {})
        fields.update({"place.fields": place_fields} if place_fields else {})
        fields.update({"poll.fields": poll_fields} if poll_fields else {})
        fields.update({"tweet.fields": tweet_fields} if tweet_fields else {})
        fields.update({"user.fields": user_fields} if user_fields else {})

        result = self.http.request("GET", self.RECENT, fields, self._headers())

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
    for tweet in result.data:
        print(tweet.text)
