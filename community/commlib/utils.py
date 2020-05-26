# related to common usage functions

import __init__
import json


# parse community file and return as dict
def get_users(comm_path):
    users = {}
    with open(comm_path, 'r') as comm_f:
        for u_line in comm_f.readlines():
            user_list = u_line.strip('\n').split('\t')
            
            for u in user_list:
                users[u] = {}

    return users


# get all tweets made by users from tweet file
def get_all_tweets(tweet_path, users):
    print(f"[+] Retrieving all tweets for {len(users)} users...")
    users_tweets = {}

    with open(tweet_path, 'r') as t_file:
        for raw_tweet in t_file.readlines():
            tweet = json.loads(raw_tweet)
            curr_u = tweet['user']['id_str']

            # if we find user inside our dict
            if curr_u in users:
                # if tweet dict doesn't contain user entry
                if not users_tweets.get(curr_u):
                    users_tweets[curr_u] = []
                users_tweets[curr_u] += [tweet]

    # add all users that did not appear with empty lists
    for u in users:
        # and also print them out so user can notice
        if u not in users_tweets:
            users_tweets[u] = []
            print(f"[!] Couldn't find user '{u}' as author in any tweet...")

    return users_tweets



# get n most common items (10 by default)
def n_most_common_items(item_dict, limit = 10):
    most_common = {}
    sorted_items = sorted(item_dict.items(), key = lambda tup: tup[1], reverse = True)
    n_most_common = sorted_items[:limit]

    for w, f in n_most_common:
        w = "NULL" if w == "" else w
        most_common[w] = f

    return most_common
