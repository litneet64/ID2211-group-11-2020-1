# related to miscelaneous utils for simple stuff

import json
import time
from collector.globals.tweet_globals import *


# make an advanced search for the children (search original tweets from user)
def get_child_query(tweet):
    username = tweet['user']['screen_name']
    query = "{} from:{}"
    query = query.format(" OR ".join(KEYWORDS), username)

    return query



# make a query with advanced search of tweets for the seeds
def get_seed_query(keywds, day_diff):
    day, mon, year = get_past_date(day_diff)

    # based on: https://github.com/igorbrigadir/twitter-advanced-search/blob/master/README.md
    query = "{} until:{}-{}-{}"
    query = query.format(" OR ".join(keywds), year, mon, day)

    return query



# get the date of n day/s ago (used to leave room for replies and RTs to appear)
def get_past_date(n_day):
    ts = time.time()
    d_ago = n_day * 24 * 3600

    t = time.gmtime(ts - d_ago)
    day = "{:02}".format(t.tm_mday)
    mon = "{:02}".format(t.tm_mon)
    year = t.tm_year

    return day, mon, year



# create a unique filename for parent tweets
def get_par_fname():
    id_name = int(time.time())
    fname = DATADIR + "parent_tweets-{}.json".format(id_name)

    return fname



# retrieve tokens for the Twitter API from given file
def retrieve_creds(path):
    creds = []
    with open(path, 'r') as cred_file:
        for line in cred_file.read():
            if line[0] == '#' or line[0] == '\n':
                continue
            creds.append(line.strip())

    return creds



# write tweet and it's comments to file
def save_tweet(tweet, filename):
    with open(filename, "a+") as tweet_file:
        content = JS.encode(tweet) + "\n"
        tweet_file.write(content)

    return
