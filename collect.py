"""
Collect up to seven days of tweets from a given search phrase
"""
import argparse
import json
import logging
import re
from datetime import datetime
from time import sleep
from typing import Dict
from typing import Tuple

from secretbox import SecretBox

from twitterapiv2.auth_client import AuthClient
from twitterapiv2.http import InvalidResponseError
from twitterapiv2.search_client import SearchClient


log = logging.getLogger("collect")


def run_search(search_string: str, start_at: datetime) -> Dict[str, str]:
    """Facilates search, return dict of tweets by tweet_id"""
    # Load client secrets and bearer token to environ
    secrets = SecretBox(auto_load=True)
    if not secrets.get("TW_BEARER_TOKEN"):
        AuthClient().set_bearer_token()

    client = SearchClient().start_time(start_at).max_results(100)
    tweets: Dict[str, str] = {}

    while True:
        log.info("Retrieving Tweets...")
        try:
            response = client.search(search_string, page_token=client.next_token)
        except InvalidResponseError as err:
            if "429" not in str(err):
                raise Exception() from err
            retry_handler(client)
            continue

        tweets.update({tweet.id: tweet.text for tweet in response.data})

        log.info("Pulled %s tweets, %s total", len(response.data), len(tweets))
        log.debug("Requests remaining: %s", client.limit_remaining)
        log.debug("ID start: %s - end: %s", response.data[0].id, response.data[-1].id)

        if not client.next_token:
            log.info("No additional pages to poll.")
            break

        if client.limit_remaining == 0:
            retry_handler(client)

    return tweets


def retry_handler(client: SearchClient) -> None:
    """Loops and holds for limit remaining to reset"""
    while datetime.utcnow() <= client.limit_reset:
        log.info(
            "Rate limit reached, restarting at: %s UTC - currently %s (next check in 30 seconds)",  # noqa
            client.limit_reset,
            datetime.utcnow(),
        )
        sleep(30)


def save_tweets(tweets: Dict[str, str]) -> None:
    """Save tweets to filename `tweetsYYYY.MM.DD.HH.MM.SS"""
    filename = datetime.utcnow().strftime("tweets%Y.%m.%d.%H.%M.%S")
    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(tweets, outfile, indent=4)
    log.info("Saved %s tweets to '%s'", len(tweets), filename)


def cli_args() -> Tuple[str, str, str]:
    """Control command line interface"""
    cmArgs = argparse.ArgumentParser(
        description="#100DaysofCode Project - 2021 rewrite"
    )
    cmArgs.add_argument(
        "search_term", type=str, help="String of what to search Twitter for"
    )
    cmArgs.add_argument(
        "start_date",
        type=str,
        help="YYYY-MM-DD Date of when to start search, 7 days max.",
    )
    cmArgs.add_argument(
        "--log",
        type=str,
        default="info",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level. Default: info",
    )
    args = cmArgs.parse_args()

    return args.search_term, args.start_date, args.log


def clean_search(search: str) -> str:
    """Trim and validate search, restrict to 512 characters"""
    search = search.strip()
    if len(search) > 512:
        log.warning("Search string greater than 512 character. It will be truncated.")
    return search[:512]


def clean_start_date(start_date: str) -> datetime:
    """Validate and convert to ISO8601 format at 00:00 UTC"""
    match = re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", start_date)
    if match is None:
        log.error("Invalid date format given. Must be YYYY-MM-DD: '%s'", start_date)
        raise SystemExit(1)
    return datetime.strptime(f"{start_date}T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")


if __name__ == "__main__":
    search, start_date, log_level = cli_args()
    logging.basicConfig(level=log_level.upper())
    search = clean_search(search)
    start_at = clean_start_date(start_date)
    tweets = run_search(search, start_at)
    save_tweets(tweets)
    raise SystemExit(0)
