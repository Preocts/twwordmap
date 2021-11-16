"""
Process collected tweets into word count
"""
import re
from argparse import ArgumentParser
from argparse import Namespace
from pathlib import Path
from string import ascii_letters
from typing import Dict
from typing import List

from datastore import DataStore
from skipwords import skip_words


class CountWords:
    def __init__(self) -> None:
        self.word_count: Dict[str, int] = {}
        self.hash_count: Dict[str, int] = {}
        self.skipped = 0

    def parse_tweet(self, text: str) -> None:
        """Adds words to count"""
        valid_start_letters = tuple(ascii_letters + "#")
        valid_end_letters = tuple(ascii_letters)
        text = re.sub(r"\\u[a-z|0-9]{4}", "", text)
        for word in text.replace("\n", " ").lower().split():
            if (
                len(word) < 1
                or len(word) > 42
                or re.match(r"^https?:\/\/.*$", word)
                or not word.startswith(valid_start_letters)
                or not word.endswith(valid_end_letters)
                or word in skip_words
            ):
                self.skipped += 1
                continue

            if word.startswith("#"):
                self.hash_count[word] = self.hash_count.get(word, 0) + 1
            else:
                self.word_count[word] = self.word_count.get(word, 0) + 1


def cli_args() -> Namespace:
    """Parse command line args"""
    args = ArgumentParser(description="#100DaysofCode Project - 2021 re-write")
    args.add_argument(
        "database_name",
        type=str,
        help="Sqlite3 database file to load.",
    )
    args.add_argument(
        "--cutoff",
        type=int,
        default=20,
        help="Lower percent (0-100) to remove from output. Default: 20",
    )
    return args.parse_args()


def load_tweets(filename: str) -> List[str]:
    """Read tweets from database, return just the text"""
    if not Path(filename).exists():
        raise FileNotFoundError(f"'{filename} not found")
    datastore = DataStore(filename)
    with datastore.connection() as dbconn:
        table_rows = dbconn.get_text()
    return [row[0] for row in table_rows]


if __name__ == "__main__":
    args = cli_args()
    counter = CountWords()
    all_tweets = load_tweets(args.database_name)

    for tweet in all_tweets:
        counter.parse_tweet(tweet)
