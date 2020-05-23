#!/usr/bin/python3

import json
import argparse


# argument parsers
def get_args():
    parser = argparse.ArgumentParser(description = "Counts Unique User IDs and duplicate tweets in a"\
            " file with tweets, made for the final project of Group 11 for ID2211 at KTH",
             epilog = "Made by <pjan2@kth.se>")

    # path to file with all tweets
    parser.add_argument("-f", "--file", help = "Path to the file with all the tweets to count dup tweets",
            required = True)

    return parser.parse_args()


# main function
if __name__ == "__main__":
    # parse args
    args = get_args()

    # get path
    t_path = args.file

    # user and tweet id set
    users = set()
    tweet_ids = set()

    # tweet counter
    c = 0

    # go through file
    with open(t_path, "r") as tweet_file:
        for raw_tweet in tweet_file:
            tweet = json.loads(raw_tweet)

            tweet_ids.add(tweet['id'])
            users.add(tweet['user']['id'])
            c += 1

    # unique tweets
    ut = len(tweet_ids)

    # print results
    print(f"[+] Found {len(users)} unique users in {c} tweets...")
    print(f"[+] Found {ut} unique tweets on {c} tweets ({c-ut} dups)...")
