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
    active_users = set()
    mentioned_users = set()
    tweet_ids = set()

    # tweet counter
    c = 0

    # go through file
    with open(t_path, "r") as tweet_file:
        for raw_tweet in tweet_file:
            tweet = json.loads(raw_tweet)

            # get active users (the ones that made the tweets) and tweets
            tweet_ids.add(tweet['id'])
            active_users.add(tweet['user']['id'])

            # get all mentioned users
            for mentioned_user in tweet['entities']['user_mentions']:
                mentioned_users.add(mentioned_user['id'])

            c += 1

    # unique tweets, all mentioned users, all tweet authors and all users involved
    ut = len(tweet_ids)
    all_ment = len(mentioned_users)
    act_u = len(active_users)
    all_users = len(set.union(active_users, mentioned_users))

    # print results
    print(f"[+] Found {all_users} unique users ({act_u} active and {all_users - act_u} passive)...")
    print(f"[+] Found {act_u} unique tweet authors in {c} tweets...")
    print(f"[+] Found {all_ment} unique mentions in {c} tweets...")
    print(f"[+] Found {ut} unique tweets on {c} tweets ({c-ut} dups)...")
