# related to functions that check a condition to accept or prune tweets to traverse

import json


# check that parent file hasn't been traversed
def is_new_seed(seed, parent_path, trav):
    # check that we haven't traversed it already
    if seed['id'] in trav:
        return False

    # check that arg hasn't been setted and hasn't been traversed
    elif parent_path == "":
        return True

    # (pertaining to arg)
    with open(parent_path, "r") as parent_fd:
        # check we aren't traversing from a previously processed seed written on file
        for line in parent_fd.readlines():
            par_seed = json.loads(line)
            if seed['id'] == par_seed['id']:
                return False

    return True



# check that traversing those tweets won't make us go into a cycle for level 1
def pass_pruning_lvl_1(par_tweet, ch_tweet, trav):
    # check that new tweet hasn't been traversed already
    if ch_tweet['id'] in trav:
        return False

    # check that the tweets are not the same (this condition is only useful once when searching for replies)
    if par_tweet['id'] == ch_tweet['id']:
        return False

    # check that the user replying/retweeting is not the same as the tweet author
    elif par_tweet['user']['id'] == ch_tweet['user']['id']:
        return False

    return True



# make corresponding checks to the possible level 2 tweets
def pass_pruning_lvl_2(tweet_l0, tweet_l1, tweet_l2, trav):
    rep_id_key = "in_reply_to_status_id"

    # check that this tweet hasn't been traversed yet
    if tweet_l2['id'] in trav:
        return False

    # check that level 2 tweets are not replies to the level 0 seed
    elif rep_id_key in tweet_l2.keys() and tweet_l2[rep_id_key] == tweet_l0['id']:
        return False

    # check that level 1 tweet is not the same as the level 2 one
    elif tweet_l1['id'] == tweet_l2['id']:
        return False


    return True
