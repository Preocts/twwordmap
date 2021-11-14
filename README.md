# twwordmap - Re-write after 2 years of code

Preocts#8196 Discord | [Github](https://github.com/Preocts)

**See `v1/` for the original attempt during #100DaysOfCode 2020**

### Requirements:

- [Python>=3.8](https://www.python.org/)
- [secretbox>=2.1.0](https://pypi.org/project/secretbox/)
- [urllib3>=1.26.7](https://pypi.org/project/urllib3/)

### `.env` file setup

To run `collect.py` you will need authentication credentials from Twitter's v2 API for an application. Place these into an `.env` file in the project root. Note, if the bearer token is also included the secret and key are not needed.

```env
TW_CONSUMER_KEY=[client key]
TW_CONSUMER_SECRET=[client secret]
# Optional alternative: provide existing bearer token
TW_BEARER_TOKEN=[bearer token]
```

---

### collect.py (re-write)

```text
usage: collect.py [-h] [--name tweets2021.11.14.18.49.44.db] [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}] search_term start_date

#100DaysofCode Project - 2021 rewrite

positional arguments:
  search_term           Define the search query, up to 512 characters. Be specific! Highly recommended to use `-is:retweet` to drastically reduce the number of results. Applications have a 500,000 **monthly** limit (per tweet, not request!).
  start_date            YYYY-MM-DD Date of when to start search, 7 days max. Tweets are pulled from current time backward to this date.

optional arguments:
  -h, --help            show this help message and exit
  --name tweets2021.11.14.18.49.44.db
                        sqlite3 file to store results in
  --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level. Default: INFO
```

Data population: This script does the heavy lifting of polling Twitter's Recent Search API and collecting the results into the sqllite3 database.

This script will handle 429 throttles from Twitter by monitoring the response headers and pausing when needed. There is a 15-minute reset window for these limits. `INFO` level debugging has a regular output indicating when the script is still waiting.

**NOTE:** All tweets pulled are stored in the database as they are pulled. If you break from a throttle window, the tweets successfully pulled are not lost.

Example output with `DEBUG` log level:
```text
INFO:collect:Retrieving Tweets...
DEBUG:urllib3.connectionpool:https://api.twitter.com:443 "GET /2/tweets/search/recent?start_time=2021-11-13T00%3A00%3A00Z&max_results=100&tweet.fields=created_at&query=%23100DaysOfCode&next_token=b26v89c19zqg8o3fpdv9kz2d7cwclj6yfgts2hkddzed9 HTTP/1.1" 200 23279
INFO:collect:Pulled 100 tweets, 84953 total
DEBUG:collect:Requests remaining: 0
DEBUG:collect:ID start: 1459535890380902405 - end: 1459535502990888960
INFO:collect:Rate limit reached, resets at: 2021-11-14 17:11:53 UTC
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:00:52.159285 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:01:52.219622 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:02:52.279899 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:03:52.340215 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:04:52.400542 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:05:52.460912 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:06:52.521377 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:07:52.581821 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:08:52.642266 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:09:52.702683 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:10:52.762999 UTC...
INFO:collect:Waiting for limit reset, currently: 2021-11-14 17:11:52.823330 UTC...
INFO:collect:Retrieving Tweets...
DEBUG:urllib3.connectionpool:Resetting dropped connection: api.twitter.com
DEBUG:urllib3.connectionpool:https://api.twitter.com:443 "GET /2/tweets/search/recent?start_time=2021-11-13T00%3A00%3A00Z&max_results=100&tweet.fields=created_at&query=%23100DaysOfCode&next_token=b26v89c19zqg8o3fpdv9kz2d7c1leyi5jv2zz6tv9hcvx HTTP/1.1" 200 24445
INFO:collect:Pulled 100 tweets, 85053 total
DEBUG:collect:Requests remaining: 449
DEBUG:collect:ID start: 1459535501870960643 - end: 1459534944624128001
```

---

### datastore.py (new)

A small abstract layer for storing and retrieving tweet data from a SQLite3 database. Initializing the object sets the file name. Database calls are done within a context manager to ensure proper closing on exit. `:memory:` is a valid filename and will create a database that only exists in memory. All data will be lost on exit.

Example usage:
```py
from datastore import DataStore

mystore = DataStore("mydata.db")

with mystore.connection() as dbclient:
    # Reference CRUD methods via `dbclient`
    ...
```

---

### process.py (re-write)

**work pending**

---

# twitterapiv2 - Custom API wrapper

In this rewrite I ended up creating my own custom wrapper. I'll break this out into its own proper repo "soon".

### Authenticating with Twitter API v2 as an application

The authentication client of included in the `twitterapiv2/` library requires your applications consumer credentials to be loaded in the environment variables before an authentication attempt is made. The consumer credentials are your client key and client secret as found in the application dashboard of the Twitter Dev panel.

Create two environmental variables as follows:
```env
TW_CONSUMER_KEY=[client key]
TW_CONSUMER_SECRET=[client secret]
```

A 'TW_BEARER_TOKEN' will be created in the environment on successful authentication. This key should be stored securely and loaded to the environment on subsequent calls. When this token already exists, the request for a bearer token can be skipped.

Additional calls to the authentication process **will not** result in a new bearer token if the same consumer credentials are provided. The former bearer token must be invalided to obtain a new one.

### Search client

The search client performs a "Recent Search" from the Twitter V2 API. This search is limited to seven days of history and has a large number of inner objects to select from. By default, the search only returns the `text` of the tweet and the `id` of the tweet.

After declaring a base `SearchClient()` the fields of the search query can be set using the builder methods. These can be chained as they return a new `SearchClient` with the fields carried forward. When executing a `.search()` the `page_token` allows for pagination of results.

Rate limiting must be handled outside of the library. `SearchClient.limit_remaining` will be an `int` representing the number of API calls remaining for requests are refused. `SearchClient.limit_reset` is an unaware UTC `datetime` object of the next reset time (typically 15 minutes). If a search has not been invoked the `.limit_remaining` will default to `-1` and `limit_reset` to `.utcnow()`.

Full API details:

https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent#Default

Use example:
```py
from datetime import timedelta
from twitterapiv2.auth_client import AuthClient
from secretbox import SecretBox

SecretBox(auto_load=True)

auth = AuthClient()
auth.set_bearer_token()

mysearch = (
    SearchClient()
    .start_time("2021-11-10T00:00:00Z")
    .end_time(datetime.utcnow() - timedelta(seconds=10))
    .expansions("author_id,attachments.poll_ids")
)
while True:
    result = mysearch.search(
        "#100DaysOfCode",
        page_token=mysearch.next_token,
    )
    for tweet_text in result.data:
        print(tweet_text.text)
    if not mysearch.next_token:
        break

print(mysearch.limit_remaining)
print(mysearch.limit_reset)
```
