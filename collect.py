"""
Collect status IDs and Text from an entire day

Built during 100DaysofCode.

Coded by: Preocts
    Discord: Preocts#8196
    GitHub: https://github.com/Preocts

Loop through results returned from our fetch() script and gather them into a
collection of statuses.

Store the results in a flat-file as JSON.
"""
import fetch
import eggTimer
import logging
import os
import dotenv
import time
import json
import argparse

logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)
timer = eggTimer.eggTimer('collect.py')  # Start timer for performance tracking


def search(searchTerm, sdate):
    """
    Use the 1.1/search/tweets.json end-point to get statuses (tweets)

    The search works backward from most recent to (sdate) in batches of 100
    results each loop.

    Uses application authentication so the ".env" file must contain all four
    tokens of authentication for this script to work. This script only
    requires read-only access.

        .env file format:
            tw_api=[Consumer Key]
            tw_api_secret=[Consumer Secret]
            tw_access=[Access Token Key]
            tw_access_secret=[Access Token Secret]
    """
    logger.debug(f'Search Term: {searchTerm}')
    logger.debug(f'since_date: {sdate}')
    # Load our secrets from .env file
    dotenv.load_dotenv()
    apiCode = os.getenv('tw_api')
    apiSecret = os.getenv('tw_api_secret')
    accessCode = os.getenv('tw_access')
    accessSecret = os.getenv('tw_access_secret')

    # Create API connection using Twitter library
    logger.info('Connecting to Twitter API')
    twapi = fetch.connect(apiCode, apiSecret, accessCode, accessSecret)
    # Make a call - Confirms auth and baselines rate limits
    try:
        twapi.InitializeRateLimit()
    except ValueError as err:
        logger.info(f'Exception: {err}')
        logger.critical('Authentication failed, check tokens.')
        exit()
    logger.info('Connection Complete')

    # Some needed vars
    lastID = 0  # Used to move search backward in time
    endpoint = 'https://api.twitter.com/1.1/search/tweets.json'  # Rate limit
    collection = {}  # Where we push memory to the limits!
    collection["collect"] = []
    totals = [0, 0]  # Total Pulled, Total Unique

    while True:  # This is a really bad way to loop

        # Pull statuses from Twitter
        raw_results = fetch.fetch(twapi, searchTerm, sdate, 100, lastID)
        if raw_results == 'err':
            break  # Error
        if not(len(raw_results['statuses'])):
            logger.info('That\'s all folks! No more results')
            break

        # Move ID backward
        lastID = fetch.lastID(raw_results)

        # Strip everything except ID, date, and text
        clean_results = fetch.filterResult(raw_results['statuses'])

        # Strip all retweets
        unique_results = fetch.stripRetweets(clean_results)

        # Tally the new total
        totals[0] += len(clean_results)
        totals[1] += len(unique_results)

        for r in unique_results:
            collection["collect"].append((r, unique_results.get(r)))

        logger.info('Current Counts: '
                    f'Total statuses: {totals[0]} | '
                    f'Total uniques: {totals[1]}')

        logger.debug(f'Segment time: {timer.mark()}')
        logger.debug(f'Rate Limit: {twapi.CheckRateLimit(endpoint)}')
        if twapi.CheckRateLimit(endpoint).remaining == 0:
            logger.warning('Rate Limit Reached! Program will pause and start '
                           'once the rate limit resets (>15min)')

    # Add some stats to our collection
    collection["Total"] = totals[0]
    collection["Unique"] = totals[1]

    # Create a filename with YYYY.MM.DD.HH.MM.SS-Search.josn formatted name
    filename = time.strftime('%Y.%m.%d.%H.%M.%S-Search')
    with open(filename + '.json', 'w') as outfile:
        outfile.write(json.dumps(collection))
        # outfile.write(str(collection))

    timer.stop()
    logger.debug(f'Start tic: {timer.tic}')
    logger.debug(f'End toc  : {timer.toc}')
    logger.debug(f'Run time : {timer.toc - timer.tic}')
    logger.info('End of Line.')
    timer.dumpTimes(filename + '.txt', 'w')


if __name__ == '__main__':
    # Command-line Args
    cmArgs = argparse.ArgumentParser(description="#100DaysofCode Project")
    cmArgs.add_argument("searchTerm", type=str,
                        help="String of what to search Twitter for")
    cmArgs.add_argument("sdate", type=str,
                        help="(YYYY-MM-DD) Date of when to search until")
    cmArgs.add_argument("--log", type=str, default="debug",
                        choices=['debug', 'info', 'warning',
                                 'error', 'critical'],
                        help="Logging level. Default: debug")

    args = cmArgs.parse_args()
    # Setup a quick console output for the logging
    # Yes, this is subjectively better than using print()
    console = logging.StreamHandler()
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        exit()
    console.setLevel(level=numeric_level)
    format = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    console.setFormatter(logging.Formatter(format))
    logger.addHandler(console)
    search(args.searchTerm, args.sdate)
