"""
Process

Built during 100DaysofCode.

Coded by: Preocts
    Discord: Preocts#8196
    GitHub: https://github.com/Preocts
"""

import re
import sys
import json
import string
import logging
import stopwords
import argparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def isInt(n):
    try:
        int(n)
    except ValueError:
        return False
    return True


def noPunc(w):
    punc = ('.', '!', '?')
    for p in punc:
        w = w.rstrip(p)
    return w


def getwords(filename: str) -> dict:
    """ Parses a collect.py output file and returns a dict

    Strips the following (feel free to adjust as you like):
        Words less than 2 characters long
        Words longer than 42 characters
        Hashtags (starts with #)
        URLS (starts with HTTP)
        Leading and trailing puncuation
        All unencode characters
        Words that do not start with or end with ascii letters
        Any word found in stopwords.py

    Args:
        filename(str): Path and filename of input file

        Input should be formated as:
        {
            "collect": [
                [id, text]
            ]
        }

    Returns: two dicts by word/hashtag with count from provided input
    {"[word]": 0}, {"[hashtag]": 0}
"""
    with open(filename, 'r') as file:
        rawread = r"{}".format(file.read())
    logger.debug(f'Loaded file: {filename} ({sys.getsizeof(rawread)} bytes)')
    cleanread = re.sub(r'\\u[a-z|0-9]{4}', '', rawread)  # Remove unicoding
    jsonDict = json.loads(cleanread)
    rawread = None
    logger.debug(f'Cleaned input: Count: {len(jsonDict["collect"])} '
                 f'({sys.getsizeof(jsonDict)} bytes)')

    hashtags = {}
    words = {}
    for id, text in jsonDict['collect']:
        slice = text.replace('\n', ' ').split(' ')
        for i, s in enumerate(slice):
            word = noPunc(s.lower())

            # Only track words > 2 and < 42 characters
            if not(len(word) > 1 and len(word) < 42):
                continue

            # Hashtags
            if word[0] == '#':
                hashtags[word] = hashtags.get(word, 0) + 1
                continue

            # Ignore links
            if word[:4] == 'http':
                continue

            # Ignore more things not starting with a ascii letter
            if not(word.startswith(tuple(string.ascii_letters))):
                continue

            if not(word.endswith(tuple(string.ascii_letters))):
                continue

            if word in stopwords.list:
                continue

            words[word] = words.get(word, 0) + 1
    logger.debug(f'Completed getting words. Total: {len(words)}')
    logger.debug(f'Removed hashtags. Total: {len(hashtags)}')
    return words, hashtags


def simpleCloud(**kwargs):
    """ Outputs a basic HTML word cloud

    Keyword Args:
        filename(str): Location and name of HTML file to write
        total(int): Total number of words found
        shown(int): Total number of words shown
        cutoff(int): Lower percentage of word occurances to hide
        high(int): Highest word count (max)
        words(dict): Dict of words
        hashtag(dict): Dict of hashtags
    """
    logger.debug('Writing simple word cloud out...')
    filename = kwargs.get('filename', 'output.html')
    total = kwargs.get('total', 0)
    show = kwargs.get('show', 0)
    cutoff = kwargs.get('cutoff', 0)
    high = kwargs.get('high', 1)
    words = kwargs.get('words', {})
    hashtags = kwargs.get('hashtag', {})

    with open(filename, 'w') as outfile:
        outfile.write(''.join([
            '<HTML>',
            '<STYLE>',
            'body { background-color: #111111; font-size: 172px; }',
            'div { width: 80%; margin: 25px 10%; background-color: #DDDDDD; }',
            'p { margin: 0px; text-align: center; }',
            'span { margin: -15px; padding: 0px; }',
            '</STYLE>',
            '<BODY>',
            '<DIV>',
            '<P style="font-size: 36px;">twwrodmap - by Preocts</P>',
            '<P style="font-size: 18px;">Total words: ',
            str(total),
            ' | Total shown: ',
            str(show),
            '</P>',
            '<P style="font-size: 12px;">Showinig top ',
            str(100 - cutoff),
            '% by highest count.</P>',
            '<P>'
        ]))
        # Word Cloud
        for word in sorted(words):
            if round((words[word] / high) * 100) > cutoff:
                outfile.write(''.join([
                    '<span style="font-size: ',
                    str(round((words[word] / high) * 100)),
                    '%;">',
                    word,
                    '</span>\n'
                ]))
        # Hashtags found
        outfile.write(''.join([
            '</P>',
            '</DIV>',
            '<DIV>',
            '<P style="font-size: 12px">Hashtags: [("#HashTag", count)]</P>',
            '<P style="font-size: 12px">']))

        rawout = []
        for tag in sorted(hashtags):
            rawout.append((tag, hashtags[tag]))
        outfile.write(str(rawout))
        # Raw Data
        outfile.write(''.join([
            '</P>',
            '</DIV>',
            '<DIV>',
            '<P style="font-size: 12px">Raw data: [("word", count, %)]</P>',
            '<P style="font-size: 12px">']))

        rawout = []
        for word in sorted(words):
            rawout.append(
                (word, words[word], round((words[word] / high) * 100))
            )
        outfile.write(str(rawout))

        outfile.write(''.join([
            '</P>',
            '</DIV',
            '</BODY>',
            '</HTML>'
        ]))
    logger.debug('Writing completed.')
    return


if __name__ == '__main__':
    # Command-line Args
    cmArgs = argparse.ArgumentParser(description="#100DaysofCode Project")
    cmArgs.add_argument("filename", type=str,
                        help="Name of file being loaded")
    cmArgs.add_argument("cutoff", type=int,
                        help="Lower percent (0-100) to remove from output")

    args = cmArgs.parse_args()
    # Setup a quick console output for the logging
    # Yes, this is subjectively better than using print()
    console = logging.StreamHandler()
    format = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    console.setFormatter(logging.Formatter(format))
    logger.addHandler(console)
    words, hashtags = getwords(args.filename)

    total = len(words)
    high = 0
    show = 0
    cutoff = args.cutoff

    for word in words:
        if words[word] > high:
            high = words[word]  # Get our 100%
    logger.debug(f'Max count is: {high}')

    for word in words:
        if round((words[word] / high) * 100) > cutoff:  # gotta be top %
            show += 1
    logger.debug(f'Words above {cutoff}% cutoff: {show}')

    kwargs = {
        'filename': args.filename[0:-4] + 'html',
        'total': total,
        'show': show,
        'cutoff': cutoff,
        'high': high,
        'words': words,
        'hashtag': hashtags
    }

    simpleCloud(**kwargs)
