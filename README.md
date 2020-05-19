# twWordMap

A side-project for the 100 Days of Code challenge.

Created by Preocts

Preocts#8196 Discord | [Github](https://github.com/Preocts)

---

### Requirements:

- [Python 3.8.1](https://www.python.org/)
- [python-twitter](https://python-twitter.readthedocs.io/en/latest/installation.html)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

To run you'll need to create a file in the working directory called ".env" and put the following lines into it:

```
tw_api=[Consumer Key]
tw_api_secret=[Consumer Secret]
tw_access=[Access Token Key]
tw_access_secret=[Access Token Secret]
```

---

### collect.py

```
usage: collect.py [-h] searchTerm sdate

#100DaysofCode Project

positional arguments:
  searchTerm  String of what to search Twitter for
  sdate       (YYYY-MM-DD) Date of when to search until

optional arguments:
  -h, --help  show this help message and exit
```

Search script - Define a search string, a since_date, and let it go. Will pull the most recent tweets, moving backward through the timeline, until it runs out of results. 7 day limit on the "since_date" and throttled to 450 requests per fifteen minutes.

This script will pause if it hits the rate limit and throws a WARNING in the logs letting you know that it will resume once the rate limit is reset.

Example use with trunc'ed output:

```
$ python collect.py #100DaysOfCode 2020-05-18 --log info

2020-05-18 20:53:04,327 - collect - INFO - Connecting to Twitter API
2020-05-18 20:53:04,825 - collect - INFO - Connection Complete
2020-05-18 20:53:05,226 - collect - INFO - Current Counts: Total statuses: 100 | Total uniques: 11
2020-05-18 20:53:05,230 - collect - INFO - End of Line.
````

File output is placed in the working directory. Two files are generated per execution, a JSON and a text file.  Each are named in the date/time format: *YYYY.MM.DD.HH.MM.SS-Search*.

JSON File output format:
```json
{
    "collect": [
        [Snowflake(int), "Text of tweet"(str)],
        [Snowflake(int), "Text of tweet"(str)]
    ],
    "total": (int),
    "unique" (int)
}
```

---

### fetch.py

A collection of functions to connect and auth to Twitter's API as an application and pull results from the search end-point. Basically my own wrapper around python-twitter library
