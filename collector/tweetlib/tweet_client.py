# tweet functions related to the client side, what the client would use
# (both auths, argument parser, keyword expander)

import argparse
from twarc import Twarc
from collector.tweetlib import tweet_utils as tutils


# standard argparser function
def get_args():
    parser = argparse.ArgumentParser(description = "Retrieve tweets in fashion similar to\
            the arbitrary graph proposed by Group 11 for the course ID2211 at KTH",
            epilog = "Made by <pjan2@kth.se>")

    # number of seed tweets
    parser.add_argument("-s", "--seeds", type = int, help = "Define the number of seed \
            tweets to start the depth-search (Default: 10,000).", default = 10_000)

    # path to creds file
    parser.add_argument("-c", "--creds", help = "Path to the file with the Twitter API \
            Credentials", default = "")

    # maximum date to search for tweets
    parser.add_argument("-u", "--until", type = int, help = "Maximum number of days ago\
            from current day to search for tweets, like an 'until' to a certain date \
            (Between 1 and 6. Default: 1)", choices = range(1,7), default = 1)

    # parent file to check for traversed seeds
    parser.add_argument("-p", "--parent-file", help = "File with seed tweets (parents) to\
            to check for previously traversed seeds, saving space and time",
             default = "")

    return parser.parse_args()



# authenticate for both user and app version
def auth_ua(creds_path):
    # app auth can supposedly get 4 as much replies according to:
    #   https://github.com/DocNow/twarc/issues/323
    if creds_path == "":
        t_user = Twarc(app_auth = False)
        t_app = Twarc(app_auth = True)
    else:
        creds = tutils.retrieve_creds(creds_path)
        t_user = Twarc(creds[0], creds[1], creds[2], creds[3], app_auth = False)
        t_app = Twarc(creds[0], creds[1], creds[2], creds[3], app_auth = True)

    return t_user, t_app



# expand keywords for uppercase, capitalized one and hashtag version
def expand_keywds(keywds):
    new_keywds = []
    for kw in keywds:
        new_keywds += [kw, kw.upper(), kw.capitalize(), "#"+kw]

    return new_keywds
