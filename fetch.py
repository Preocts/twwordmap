"""
Fetch tweets of a specific hashtag.

Built during 100DaysofCode.

Coded by: Preocts
    Discord: Preocts#8196
    GitHub: https://github.com/Preocts

Uses the python-twitter library to authenticate with Twitter's API via
app authentication and performs an advanced search for a given searchTerm.

The results are returned in JSON form and stored in a file for use later.
"""
import os
import twitter
import json
import time
import logging
from dotenv import load_dotenv

logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)


def lastID(twlist=None):
    """ Returns the last ID (oldest) of a json search results"""
    if twlist is None:
        return None
    return twlist['statuses'][-1]['id'] - 1


def fetch(api, searchTerm, since_date, count=10, id=0):
    """
    Search for a given term from twitter since a given date.

    Args:
        api (object): twitter.Api() instance already init'ed
        searchTerm (str): String of what to search for
        since_date (str): "YYYY-MM-DD" formated date
        count (int): Number of statuses to return (default: 10 / max: 100)
        id (int): Snowflake of the max id value to return (default: 0)

    Returns: Search results as JSON
        {"statuses": []}

    Example Use:
        results = fetch(api, "#100DaysofCode", "2020-05-17")
        # Will return 100 of the most recent tweets containing "#100DaysofCode"

        results = fetch(api, "#100DaysofCode", "2020-05-17", 10, 1235446879)
        # Will return 10 tweets that happened since 2020-05-17 but before
        # a status id of 1235446879
    """
    logger.debug(f'Args: {(searchTerm, since_date, id, count)}')
    if count > 100:
        count = 100
        logger.warning('Max count return for fetch() is 100')
    return api.GetSearch(term=searchTerm,
                         max_id=id,
                         count=count,
                         result_type='recent',
                         include_entities=False,
                         return_json=True)


def connect(apiCode, apiSecret, accessCode, accessSecret, debug=False):
    """
    Creates a class instance of twitter.Api() for use

    This creates an instance using Bearer token authentication for
    an application. Debug flag is for HTTP.client debug levels

    Args:
        apiCode (str): Consumer Key
        apiSecret (str): Consumer Secret
        accessCode (str): Access Token Key
        accessSecret (str): Access Token Secret
        debug (bool): HTTP.client debug output

    Returns:
        Instance of twitter.Api()
    """
    return twitter.Api(consumer_key=apiCode,
                       consumer_secret=apiSecret,
                       access_token_key=accessCode,
                       access_token_secret=accessSecret,
                       application_only_auth=True,
                       debugHTTP=debug)


def filterResult(statuses):
    """
    Create a dictionary of just id and text from a list of Twitter statuses

    Args:
        statuses (list) : A list of Twitter statuses dictionaries from fetch()

    Returns:
        { "[id]": "[text]" }
    """
    logger.debug(f'Filtering {len(statuses)} statuses')
    results = {}
    for s in statuses:
        results[s['id']] = s['text']
    return results


def stripRetweets(statuses):
    """
    Create a dictionary that contains only unique statuses

    Removes any status that starts with "RT"

    Args:
        statuses (dict) : A dict of Twitter statuses from filterResult()

    Returns:
        { "[id]": "[text]" }
    """
    logger.debug(f'Stripping retweets from {len(statuses)} statuses')
    results = {}
    for id in statuses.keys():
        if statuses[id][:2] == 'RT':
            continue
        results[id] = statuses[id]
    return results


def main():
    # Performance measuring
    tic = time.perf_counter()

    # Load our secrets from .env file
    load_dotenv()
    apiCode = os.getenv('tw_api')
    apiSecret = os.getenv('tw_api_secret')
    accessCode = os.getenv('tw_access')
    accessSecret = os.getenv('tw_access')

    # Create API connection using Twitter library
    logger.info('Connecting to Twitter API')
    twapi = connect(apiCode, apiSecret, accessCode, accessSecret)
    # Make a call - Confirms auth and baselines rate limits
    try:
        twapi.InitializeRateLimit()
    except ValueError as err:
        logger.info(f'Exception: {err}')
        logger.critical('Authentication failed, check tokens.')
        exit()
    logger.info('Connection Complete')

    raw_results = fetch(twapi, '#100DaysofCode', '2020-05-17', 100, 0)
    clean_results = filterResult(raw_results['statuses'])
    unique_results = stripRetweets(clean_results)
    retweet_count = len(clean_results) - len(unique_results)
    retweet_perc = (retweet_count / len(clean_results)) * 100

    logger.info(f'From a batch of {len(clean_results)} statuses there were:\n'
                f'\tUnique statuses    : {len(unique_results)}\n'
                f'\tRetweeted statuses : {retweet_count}\n'
                f'\tRetween percentage : {retweet_perc}')

    # Create a filename with YYYY.MM.DD.HH.MM.SS-Search.josn formatted name
    # filename = time.strftime('%Y.%m.%d.%H.%M.%S-Search.json')
    # with open(filename, 'w') as outfile:
    #     outfile.write(json.dumps(bulkResults, indent=4))

    # Performance measuring
    toc = time.perf_counter()

    # Exit output
    logger.debug(f'Start tic: {tic}')
    logger.debug(f'End toc  : {toc}')
    logger.debug(f'Run time : {toc - tic}')
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
