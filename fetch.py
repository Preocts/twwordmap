"""
Fetch tweets of a specific hashtag.

Build for 100DaysofCode.

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
from dotenv import load_dotenv


def lastID(twlist=None):
    """ Returns the last ID (most recent) of a json search results"""
    if twlist is None:
        return None
    return twlist['statuses'][-1]['id'] - 1


def main():
    # Performance measuring
    tic = time.perf_counter()

    # Load our secrets from .env file
    load_dotenv()
    apiCode = os.getenv('tw_api')
    apiSecret = os.getenv('tw_api_secret')
    accessCode = os.getenv('tw_access')
    accessSecret = os.getenv('tw_access')

    # Some configuration options
    searchTerm = '#100DaysofCode'  # What are we looking for?
    count = 100  # API return size from Twitter. Max: 100
    loops = 200  # Number of times to pull from Twitter
    # loops * count = Total number of statuses pulled
    # Throttling for app authentication is 450 calls per 15 minutes

    # Create API connection using Twitter library
    twa = twitter.Api(consumer_key=apiCode,
                      consumer_secret=apiSecret,
                      access_token_key=accessCode,
                      access_token_secret=accessSecret,
                      application_only_auth=True,
                      debugHTTP=False)

    print('Starting Search')
    results = None
    bulkResults = {}
    bulkResults['statuses'] = []

    for x in range(0, loops):
        # Get results for '#100DaysofCode'
        print(f'Loop {x} of {loops}...')
        results = twa.GetSearch(term=searchTerm,
                                max_id=lastID(results),
                                count=count,
                                result_type='recent',
                                include_entities=False,
                                return_json=True)
        # Assemble the results 100 at a time
        bulkResults['statuses'].append(results['statuses'])

    print('Writing results to file...')

    # Create a filename with YYYY.MM.DD.HH.MM.SS-Search.josn formatted name
    filename = time.strftime('%Y.%m.%d.%H.%M.%S-Search.json')
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(bulkResults, indent=4))

    # Performance measuring
    toc = time.perf_counter()

    # Exit output
    print(f'Start tic: {tic}')
    print(f'End toc  : {toc}')
    print(f'Run time : {toc - tic}')
    print('End of Line.')


if __name__ == '__main__':
    main()
