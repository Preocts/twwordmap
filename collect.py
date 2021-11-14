"""
Collect up to seven days of tweets from a given search phrase
"""
import argparse
import logging
import re
from argparse import Namespace
from datetime import datetime
from time import sleep

from secretbox import SecretBox

from datastore import DataStore
from twitterapiv2.auth_client import AuthClient
from twitterapiv2.exceptions import InvalidResponseError
from twitterapiv2.exceptions import ThrottledError
from twitterapiv2.search_client import SearchClient

# Number of seconds to sleep while between throttle checks
SLEEP_TIME = 60
log = logging.getLogger("collect")


def run_search(
    search_string: str,
    start_at: datetime,
    dbclient: DataStore,
) -> None:
    """Facilates search, saving tweets into data store"""
    # Load client secrets and bearer token to environ
    secrets = SecretBox(auto_load=True)
    if not secrets.get("TW_BEARER_TOKEN"):
        AuthClient().set_bearer_token()

    total = 0
    client = (
        SearchClient().start_time(start_at).max_results(100).tweet_fields("created_at")
    )

    while True:
        log.info("Retrieving Tweets...")
        try:
            response = client.search(search_string, page_token=client.next_token)
        except InvalidResponseError as err:
            log.critical("Invalid response from HTTP: '%s'", err)
            break
        except ThrottledError:
            throttle_handler(client)
            continue

        total += len(response.data)
        log.info("Pulled %s tweets, %s total", len(response.data), total)
        log.debug("Requests remaining: %s", client.limit_remaining)
        log.debug("ID start: %s - end: %s", response.data[0].id, response.data[-1].id)

        dbclient.insert_rows(response.data)

        if not client.next_token:
            log.info("No additional pages to poll.")
            break

        if client.limit_remaining == 0:
            throttle_handler(client)


def throttle_handler(client: SearchClient) -> None:
    """Loops and holds for limit remaining to reset"""
    log.info("Rate limit reached, resets at: %s UTC", client.limit_reset)
    while datetime.utcnow() <= client.limit_reset:
        log.info("Waiting for limit reset, currently: %s UTC...", datetime.utcnow())
        sleep(SLEEP_TIME)


def cli_args() -> Namespace:
    """Control command line interface"""
    filename = datetime.utcnow().strftime("tweets%Y.%m.%d.%H.%M.%S.db")
    cmArgs = argparse.ArgumentParser(
        description="#100DaysofCode Project - 2021 rewrite"
    )
    cmArgs.add_argument(
        "search_term",
        type=str,
        help=(
            "Define the search query, up to 512 characters. Be specific! "
            "Highly recommended to use `-is:retweet` to drastically reduce "
            "the number of results. Applications have a 500,000 **monthly** "
            "limit (per tweet, not request!)."
        ),
    )
    cmArgs.add_argument(
        "start_date",
        type=str,
        help=(
            "YYYY-MM-DD Date of when to start search, 7 days max. Tweets are "
            "pulled from current time backward to this date."
        ),
    )
    cmArgs.add_argument(
        "--name",
        type=str,
        metavar=filename,
        default=filename,
        help="sqlite3 file to store results in",
    )
    cmArgs.add_argument(
        "--log",
        type=str,
        default="info",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level. Default: INFO",
    )
    return cmArgs.parse_args()


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
    args = cli_args()
    logging.basicConfig(level=args.log.upper())
    datastore = DataStore(args.name)
    search = clean_search(args.search_term)
    start_at = clean_start_date(args.start_date)

    with datastore.connection() as dbclient:
        run_search(search, start_at, dbclient)

    raise SystemExit(0)
