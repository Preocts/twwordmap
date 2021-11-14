# twwordmap

See `v1/` for the original attempt during #100DaysOfCode 2020

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

Rate limiting must be handled outside of the library. `SearchClient.limit_remaining` will be an `int` representing the number of API calls remaining for requests are refused. `SearchClient.limit_reset` is an unaware UTC `datetime` object of the next reset time (typically 15 minutes). If a search has not been invoked the `.limit_remaining` will default to `1` and `limit_reset` to `.utcnow()`.

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
        max_results=10,
        page_token=mysearch.next_token,
    )
    for tweet_text in result.data:
        print(tweet_text.text)
    if not mysearch.next_token:
        break

print(mysearch.limit_remaining)
print(mysearch.limit_reset)
```
