import os
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from twitterapiv2.http import Http
from twitterapiv2.model.recent.recent import Recent as SearchResponse

_BEARER_TOKEN = "TW_BEARER_TOKEN"


class SearchClient(Http):

    URL = "https://api.twitter.com/2/tweets/search/recent"

    def __init__(self, num_pools: int = 10) -> None:
        """
        Create Search Recent client. Use methods to build query a .search() to run

        The environment variable "TW_BEARER_TOKEN" is required; set with the
        applicaton bearer token. This can be set manually or loaded with the
        use of AuthClient.set_bearer_token().
        """
        super().__init__(num_pools=num_pools)
        self._fields: Dict[str, Any] = {}
        self._next_token: Optional[str] = None
        self._previous_token: Optional[str] = None

    @property
    def fields(self) -> Dict[str, Any]:
        """Returns fields that have been defined"""
        return {key: str(value) for key, value in self._fields.items() if value}

    @property
    def next_token(self) -> Optional[str]:
        """Return next_token for pagination or `None` when all results are polled"""
        return self._next_token

    @property
    def previous_token(self) -> Optional[str]:
        """Return previous_token for pagination or `None` when all results are polled"""
        return self._previous_token

    def start_time(self, start: Union[str, datetime, None]) -> "SearchClient":
        """Define start_time of query. YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339)"""
        if isinstance(start, datetime):
            start = self._to_ISO8601(start)
        self._fields["start_time"] = start if start else None
        return self._new_client()

    def end_time(self, end: Union[str, datetime, None]) -> "SearchClient":
        """
        Define end_time of query. YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339)

        NOTE: The end_time cannot be less than 10 seconds from "now"
        """
        if isinstance(end, datetime):
            end = self._to_ISO8601(end)
        self._fields["end_time"] = end if end else None
        return self._new_client()

    def since_id(self, since_id: Optional[str]) -> "SearchClient":
        """Define since_id of query. Returns results with a Tweet ID greater than"""
        self._fields["since_id"] = since_id if since_id else None
        return self._new_client()

    def until_id(self, until_id: Optional[str]) -> "SearchClient":
        """Define until_id of query. Returns results with a Tweet ID less than"""
        self._fields["until_id"] = until_id if until_id else None
        return self._new_client()

    def expansions(self, expansions: Optional[str]) -> "SearchClient":
        """
        Define expansions of query. Comma seperated with no spaces:
            attachments.poll_ids, attachments.media_keys, author_id,
            entities.mentions.username, geo.place_id, in_reply_to_user_id,
            referenced_tweets.id, referenced_tweets.id.author_id
        """
        self._fields["expansions"] = expansions if expansions else None
        return self._new_client()

    def media_fields(self, media_fields: Optional[str]) -> "SearchClient":
        """
        Define media_fields of query. Comma seperated with no spaces:
            duration_ms, height, media_key, preview_image_url,
            type, url, width, public_metrics, non_public_metrics,
            organic_metrics, promoted_metrics, alt_text
        """
        self._fields["media.fields"] = media_fields if media_fields else None
        return self._new_client()

    def place_fields(self, place_fields: Optional[str]) -> "SearchClient":
        """
        Define place_fields of query. Comma seperated with no spaces:
            contained_within, country, country_code, full_name,
            geo, id, name, place_type
        """
        self._fields["place.fields"] = place_fields if place_fields else None
        return self._new_client()

    def poll_fields(self, poll_fields: Optional[str]) -> "SearchClient":
        """
        Define poll_fields of query. Comma seperated with no spaces:
            duration_minutes, end_datetime, id, options, voting_status
        """
        self._fields["poll.fields"] = poll_fields if poll_fields else None
        return self._new_client()

    def tweet_fields(self, tweet_fields: Optional[str]) -> "SearchClient":
        """
        Define tweet_fields of query. Comma seperated with no spaces:
            attachments, author_id, context_annotations, conversation_id,
            created_at, entities, geo, id, in_reply_to_user_id, lang,
            non_public_metrics, public_metrics, organic_metrics,
            promoted_metrics, possibly_sensitive, referenced_tweets,
            reply_settings, source, text, withheld
        """
        self._fields["tweet.fields"] = tweet_fields if tweet_fields else None
        return self._new_client()

    def user_fields(self, user_fields: Optional[str]) -> "SearchClient":
        """
        Define user_fields of query. Comma seperated with no spaces:
            created_at, description, entities, id, location, name,
            pinned_tweet_id, profile_image_url, protected,
            public_metrics, url, username, verified, withheld
        """
        self._fields["user_fields"] = user_fields if user_fields else None
        return self._new_client()

    def max_results(self, max_results: Optional[int]) -> "SearchClient":
        """A number between 10 and 100. By default, set at 10 results"""
        self._fields["max_results"] = max_results if max_results else None
        return self._new_client()

    def search(
        self,
        query: str,
        *,
        page_token: Optional[str] = None,
    ) -> SearchResponse:
        """
        Search tweets from up to the last seven days. max size of results is 100

        For pagination; feed the `.next_token()` or `.previous_token()` property
        into the `next_token` parameter. These default to None and can be
        safely referenced prior to, and after, searches.
        """
        self._fields["query"] = query
        self._fields["next_token"] = page_token
        result = SearchResponse.build_obj(
            super().get(self.URL, self.fields, self._headers())
        )
        self._next_token = result.meta.next_token
        self._previous_token = result.meta.previous_token
        return result

    def _headers(self) -> Dict[str, str]:
        """Build headers with TW_BEARER_TOKEN from environ"""
        return {"Authorization": "Bearer " + os.getenv(_BEARER_TOKEN, "")}

    def _new_client(self) -> "SearchClient":
        """Used to create a new client with attributes carried forward"""
        new_client = SearchClient()
        new_client._fields.update(self._fields)
        return new_client

    @staticmethod
    def _to_ISO8601(dt: datetime) -> str:
        """Convert datetime object to ISO 8601 standard UTC string"""
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
