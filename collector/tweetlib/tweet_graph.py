# related to graph traversal and node processing

from collector.tweetlib import tweet_checks as tcheck
from collector.tweetlib import tweet_utils as tutils
from collector.globals.tweet_globals import *


# process a node, either level-0, level-1 or level-2
def process_node(**kwargs):
    # get keyword arguments
    tweet = kwargs.pop("tweet")             # the tweet object
    level_fname = kwargs.pop("filename")    # filename to save tweet
    level_name = kwargs.pop("lvl")          # level name (0, 1 or 2)
    seed_tweet = kwargs.pop("seed", 0)      # the seed tweet
    auth = kwargs.pop("auth", 0)            # twitter auth (app or user)
    tweet_type = kwargs.pop("type", 0)      # tweet type (reply or retweet)
    child_c = kwargs.pop("c_count", 0)      # child counter
    total_c = kwargs.pop("t_count", 0)      # total tweet counter
    trav = kwargs.pop("trav", 0)            # set of traversed nodes

    # traverse seed node and save tweets while reporting progress
    if level_name == 0:
        print(f"[+] Going through seed tweet {child_c + 1} of {total_c}...")
        tutils.save_tweet(tweet, level_fname)
        traverse_to_lvl1(auth, tweet, child_c)
        child_c += 1

    # traverse children and save tweets while giving progress output
    elif level_name == 1:
        print(f"\r[+] Going through level-1 {tweet_type} {child_c + 1}"\
                f" (from tweet {total_c + 1})...", end = "")
        tutils.save_tweet(tweet, level_fname)
        traverse_to_lvl2(auth, seed_tweet, tweet, trav, child_c, total_c)
        child_c += 1

    # just save tweets for now
    elif level_name == 2:
        tutils.save_tweet(tweet, level_fname)

    return child_c



# traverse through all level 0 (seeds) nodes
def traverse_lvl0(t_user, t_app, t_query, s_nodes, filename, p_file):
    # seed tweet counter
    c = 0

    # traverse n seed nodes (mix between most popular and recent)
    for tweet in t_user.search(t_query, result_type='mixed'):
        if c == s_nodes:
            break

        # if arg exists and is a new seed not previously processed
        if tcheck.is_new_seed(tweet, p_file):
            c = process_node(auth = t_app, tweet = tweet, filename = filename,
                            lvl = 0, c_count = c, t_count = s_nodes)

    return



# traverse through seed node getting lvl 1 components
def traverse_to_lvl1(t_app, seed, t_cnt):
    seed_id = seed['id']
    level1_filename = DATADIR + "tweet_{}@{}.json".format(t_cnt, seed_id)
    traversed = set()
    c_cnt = ret_cnt = rep_cnt = 0


    # get replies as a generator and save them (seed comes in this one)
    for rep in t_app.replies(seed, recursive = True):
        try:
            # if reply limit has been reached
            if rep_cnt == REP_CAP:
                break
            # traverse and save only if they are useful to us
            if tcheck.pass_pruning_lvl_1(seed, rep):
                c_cnt = process_node(auth = t_app, tweet = rep, c_count = c_cnt,
                                    seed = seed, t_count = t_cnt, filename = level1_filename,
                                    lvl = 1, type = "reply", trav = traversed)
                rep_cnt += 1
        except Exception as e:
            print(f"[+] Exception: {e}")

    print("")
    # get and store retweets
    for ret in t_app.retweets(seed_id):
        try:
            # if retweet limit has been reached
            if ret_cnt == RET_CAP:
                break
            # ignore if it's not useful to us
            elif tcheck.pass_pruning_lvl_1(seed, ret):
                c_cnt = process_node(auth = t_app, tweet = ret, c_count = c_cnt,
                                    seed = seed, t_count = t_cnt, filename = level1_filename,
                                    lvl = 1, type = "retweet", trav = traversed)
                ret_cnt += 1
        except Exception as e:
            print(f"[+] Exception: {e}")

    print("")

    return



# traverse through seed's children searching for tweets related to our keywords and seed child user
def traverse_to_lvl2(t_app, seed, child_seed, traversed, c_cnt, t_cnt):
    # get query for children and new filename where to store these tweets
    child_query = tutils.get_child_query(child_seed)
    level2_filename = DATADIR + "tweet_{}.{}@{}.json"
    level2_filename = level2_filename.format(t_cnt, c_cnt, child_seed['id'])
    ret_cnt = rep_cnt = search_c = 0


    # search for tweets following our crafted query (mix between popular and recent)
    for tweet in t_app.search(child_query, result_type='mixed'):
        # if we find a tweet check that it satisfies requirements
        if tcheck.pass_pruning_lvl_2(seed ,child_seed, tweet, traversed):
            # get and store replies
            for rep in t_app.replies(tweet, recursive = True):
                try:
                    # check if we haven't reached reply limit
                    if rep_cnt == REP_CAP:
                        break
                    # ignore the first element (it's always the original tweet)
                    elif rep['id'] == tweet['id']:
                        continue
                    process_node(tweet = rep, filename = level2_filename, lvl = 2)
                    rep_cnt += 1

                except Exception as e:
                    print(f"[+] Exception: {e}")

            # get and store retweets
            for ret in t_app.retweets(tweet['id']):
                try:
                    # check if we haven't passed the retweet cap
                    if ret_cnt == RET_CAP:
                        break
                    process_node(tweet = ret, filename = level2_filename, lvl = 2)
                    ret_cnt += 1

                except Exception as e:
                    print(f"[+] Exception: {e}")

            # add to the traversed set and exit loop (we only need to find 1 tweet)
            traversed.add(tweet['id'])
            break

        # add up to the searched counter
        search_c += 1
        # and check if we haven't reached the limit in 2 batches
        if search_c == 200:
            break

    return
