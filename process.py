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

        # Skip retweets (shouldn't be searched for!)
        if text.startswith("RT "):
            return None

        # Strip unicode from text
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
        default=5,
        help="Lower percent (0-100) to remove from output. Default: 5",
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


def create_wordmap(filename: str, words: Dict[str, int], cutoff: int) -> None:
    """Creates HTML file"""
    high = max(list(words.values()))
    show = {wrd: val for wrd, val in words.items() if (val / high) * 100 >= cutoff}
    show = {wrd: show[wrd] for wrd in sorted(show)}
    with open(filename, "w", encoding="utf-8") as outfile:
        outfile.write(
            "<HTML><STYLE>"
            "body { background-color: #111111; font-size: 172px; }"
            "div { width: 80%; margin: 25px 10%; background-color: #DDDDDD; }"
            "p { margin: 0px; text-align: center; }"
            "span { margin: -15px; padding: 0px; }"
            "</STYLE><BODY><DIV>"
            '<p style="font-size: 36px;">twwrodmap - by Preocts</p>'
            f'<p style="font-size: 18px;">Total words: {len(words)} '
            f"| Total shown {len(show)}</p>"
            '<p style="font-size: 12px;">'
            f"Showinig top {100 - cutoff}% by highest count.</p><p>"
        )
        for word, count in show.items():
            outfile.write(
                f'<span style="font-size: {round((count / high) * 100, 0)}%;">'
                f"{word}</span>\n"
            )
        outfile.write("</p></div></body></html>")


if __name__ == "__main__":
    args = cli_args()
    counter = CountWords()
    all_tweets = load_tweets(args.database_name)

    for tweet in all_tweets:
        counter.parse_tweet(tweet)

    create_wordmap(args.database_name + ".words.html", counter.word_count, args.cutoff)
    create_wordmap(args.database_name + ".htags.html", counter.hash_count, args.cutoff)
