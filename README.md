# twWordMap

A side-project for the 100 Days of Code challenge.

Created by Preocts

[preocts@preocts.com](mailto:preocts@preocts.com) | Preocts#8196 Discord | [Github](https://github.com/Preocts)

---

### Requirements:

- [Python 3.8.1](https://www.python.org/)
- [python-twitter](https://python-twitter.readthedocs.io/en/latest/installation.html)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

### Status:

- Early stages - no version or release

**fetch.py**

A collection of functions to connect and auth to Twitter's API as an application and pull results from the search end-point.

**collect.py**

Core script - Define a search string, a since_date, and let it go. Will pull the most recent tweets, moving backward through the timeline, until it runs out of results. 7 day limit on the "since_date" and throttled to 450 requests per fifteen minutes.


**eggTimer.py**

A side-project within a side-project! A class definition that starts a perf_counter() timer, allows marks to be made with descriptions, and stores the results in a dictionary.

Working on this but you should be able to create easy, detailed, time measurements with it.
