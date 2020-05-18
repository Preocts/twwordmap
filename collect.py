"""
Collect status IDs and Text from an entire day

Built during 100DaysofCode.

Coded by: Preocts
    Discord: Preocts#8196
    GitHub: https://github.com/Preocts

Loop through results returned from our fetch() script and gather them into a
large collection of statuses.  Store them into a JSON

The results are returned in JSON form and stored in a file for use later.
"""
import fetch
import eggTimer
import logging
import os
import dotenv
import time

logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)
timer = eggTimer.eggTimer('collect.py')  # Start timer for performance tracking


def main():
    # Load our secrets from .env file
    dotenv.load_dotenv()
    apiCode = os.getenv('tw_api')
    apiSecret = os.getenv('tw_api_secret')
    accessCode = os.getenv('tw_access')
    accessSecret = os.getenv('tw_access')

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

    # TO DO: argparse this on refactor
    # endpoint = 'https://api.twitter.com/1.1/search/tweets.json'
    lastID = 0  # Used to move search backward in time
    searchTerm = '#100DaysofCode'  # What are we looking for
    sdate = '2020-05-17'
    count = 100
    totals = [0, 0]  # Total Pulled, Total Unique

    # Create a filename with YYYY.MM.DD.HH.MM.SS-Search.josn formatted name
    filename = time.strftime('%Y.%m.%d.%H.%M.%S-Search.raw')
    with open(filename, 'w') as outfile:
        while True:  # This is a really bad way to loop

            # Pull statuses from Twitter
            raw_results = fetch.fetch(twapi, searchTerm, sdate, count, lastID)
            if raw_results == 'err':
                break  # Error
            if not(len(raw_results['statuses'])):
                logger.info('That\'s all folks! No more results')
                break

            # Move ID backward
            lastID = fetch.lastID(raw_results)

            # Strip everything except ID and text
            clean_results = fetch.filterResult(raw_results['statuses'])

            # Strip all retweets
            unique_results = fetch.stripRetweets(clean_results)

            # Tally the new total
            totals[0] += len(clean_results)
            totals[1] += len(unique_results)

            # Write segment out to file
            for t in unique_results:
                outfile.write(f'{t}:{unique_results[t].encode("utf-8")}\n')

            logger.info('State stored to file\n'
                        f'\tTotal statuses: {totals[0]} | '
                        f'Total uniques: {totals[1]}')

            # Add mark
            timer.mark('Search Loop')
            # print(twapi.CheckRateLimit(endpoint))
            # Loop

    timer.stop()
    logger.debug(f'Start tic: {timer.tic}')
    logger.debug(f'End toc  : {timer.toc}')
    logger.debug(f'Run time : {timer.toc - timer.tic}')
    logger.info('End of Line.')


if __name__ == '__main__':
    # Setup a quick console output for the logging
    # Yes, this is subjectively better than using print()
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    format = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    console.setFormatter(logging.Formatter(format))
    logger.addHandler(console)
    main()
