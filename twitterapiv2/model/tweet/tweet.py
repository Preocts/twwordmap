"""
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent#Default
"""
from typing import Any
from typing import Dict
from typing import List

from twitterapiv2.model.tweet.data import Data
from twitterapiv2.model.tweet.meta import Meta


class Tweet:
    """Defines an empty Tweet object"""

    data: List[Data]
    meta: Meta

    @classmethod
    def build_obj(cls, obj: Dict[str, Any]) -> "Tweet":
        """Builds object from dictionary"""
        tweet = cls()

        # TODO: We can protocol this out better
        # Process nested arrays
        nested_array: Dict[str, Any] = {
            "data": Data,
        }
        for key, model in nested_array.items():
            setattr(tweet, key, [model.build_obj(x) for x in obj.get(key, [])])

        # Process Nested Objects
        nested_obj: Dict[str, Any] = {
            "meta": Meta,
        }
        for key, model in nested_obj.items():
            content = obj.get(key)
            setattr(tweet, key, model.build_obj(content) if content else None)

        return tweet
