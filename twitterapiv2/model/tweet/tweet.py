from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from twitterapiv2.model.tweet.attachments import Attachments
from twitterapiv2.model.tweet.context_annotations import ContextAnnotations
from twitterapiv2.model.tweet.entities import Entities
from twitterapiv2.model.tweet.geo import Geo
from twitterapiv2.model.tweet.includes import Includes
from twitterapiv2.model.tweet.meta import Meta
from twitterapiv2.model.tweet.non_public_metrics import NonPublicMetrics
from twitterapiv2.model.tweet.organic_metrics import OrganicMetrics
from twitterapiv2.model.tweet.promoted_metrics import PromotedMetrics
from twitterapiv2.model.tweet.public_metrics import PublicMetrics
from twitterapiv2.model.tweet.referenced_tweets import ReferencedTweets
from twitterapiv2.model.tweet.withheld import Withheld


class Tweet:
    """Defines an empty Tweet object"""

    id: str
    text: str
    created_at: Optional[str]
    author_id: Optional[str]
    conversation_id: Optional[str]
    in_reply_to_user_id: Optional[str]
    referenced_tweets: List[ReferencedTweets]
    attachments: Optional[Attachments]
    geo: Optional[Geo]
    context_annotations: Optional[ContextAnnotations]
    entities: Optional[Entities]
    withheld: Optional[Withheld]
    public_metrics: Optional[PublicMetrics]
    non_public_metrics: Optional[NonPublicMetrics]
    organic_metrics: Optional[OrganicMetrics]
    promoted_metrics: Optional[PromotedMetrics]
    possibly_sensitive: Optional[bool]
    lang: Optional[str]
    reply_settings: Optional[str]
    source: Optional[str]
    includes: Optional[Includes]
    meta: Optional[Meta]
    errors: Optional[Dict[str, Any]]

    @classmethod
    def build_obj(cls, obj: Dict[str, Any]) -> "Tweet":
        """Builds object from dictionary"""
        tweet = cls()
        tweet.id = obj["id"]
        tweet.text = obj["text"]
        tweet.created_at = obj.get("created_at")
        tweet.author_id = obj.get("author_id")
        tweet.conversation_id = obj.get("conversation_id")
        tweet.in_reply_to_user_id = obj.get("in_reply_to_user_id")
        tweet.possibly_sensitive = obj.get("possibly_sensitive")
        tweet.lang = obj.get("lang")
        tweet.reply_settings = obj.get("replay_settings")
        tweet.source = obj.get("source")
        tweet.errors = obj.get("errors")

        tweet.referenced_tweets = [
            ReferencedTweets.build_obj(rt) for rt in obj.get("referenced_tweets", [])
        ]

        attachments = obj.get("attachments")
        tweet.attachments = Attachments.build_obj(attachments) if attachments else None

        geo = obj.get("geo")
        tweet.geo = Geo.build_obj(geo) if geo else None

        ctxa = obj.get("conext_annotations")
        tweet.context_annotations = ContextAnnotations.build_obj(ctxa) if ctxa else None

        ent = obj.get("ent")
        tweet.entities = Entities.build_obj(ent) if ent else None

        withheld = obj.get("withheld")
        tweet.withheld = Withheld.build_obj(withheld) if withheld else None

        pmet = obj.get("public_metrics")
        tweet.public_metrics = PublicMetrics.build_obj(pmet) if pmet else None

        npmet = obj.get("non_public_metrics")
        tweet.non_public_metrics = NonPublicMetrics.build_obj(npmet) if npmet else None

        omet = obj.get("organic_metrics")
        tweet.organic_metrics = OrganicMetrics.build_obj(omet) if omet else None

        promet = obj.get("promoted_metrics")
        tweet.promoted_metrics = PromotedMetrics.build_obj(promet) if promet else None

        includes = obj.get("includes")
        tweet.includes = Includes.build_obj(includes) if includes else None

        meta = obj.get("meta")
        tweet.meta = Meta.build_obj(meta) if meta else None

        return tweet
