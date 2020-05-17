# related to functions that check a condition to accept tweets to traverse

import json


# check that parent file hasn't been traversed
def is_new_seed(seed, parent_path):
    # check that arg has been setted, otherwise always return true
    if parent_path == "":
        return True

    with open(parent_path, "r") as parent_fd:
        # check we aren't traversing from a previously processed seed written on file
        for line in parent_fd.readlines():
            par_seed = json.loads(line)
            if seed['id'] == par_seed['id']:
                return False

    return True



# check that traversing those tweets won't make us go into a cycle for level 1
def pass_pruning_lvl_1(par_tweet, ch_tweet):
    # check that the tweets are not the same (this condition is only useful once when searching for replies)
    if par_tweet['id'] == ch_tweet['id']:
        return False

    # check that the user replying/retweeting is not the same as the tweet author
    elif par_tweet['user']['id'] == ch_tweet['user']['id']:
        return False

    return True



# make corresponding checks to the possible level 2 tweets
def pass_pruning_lvl_2(tweet_l0, tweet_l1, tweet_l2, trav_set):
    rep_id_key = "in_reply_to_status_id"

    # check that level 2 tweets are not replies to the level 0 seed
    if rep_id_key in tweet_l2.keys() and tweet_l2[rep_id_key] == tweet_l0['id']:
        return False

    # check that level 1 tweet is not the same as the level 2 one
    elif tweet_l1['id'] == tweet_l2['id']:
        return False

    # check that this tweet hasn't been traversed yet
    elif tweet_l2['id'] in trav_set:
        return False

    return True
