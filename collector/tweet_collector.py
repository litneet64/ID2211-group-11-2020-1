#!/usr/bin/python3

import __init__
from collector.tweetlib import tweet_client as tclient
from collector.tweetlib import tweet_graph as tgraph
from collector.tweetlib import tweet_utils as tutils
from collector.globals.tweet_globals import *

# main piece of code
if __name__ == "__main__":
    # get the arguments
    args = tclient.get_args()

    # path for creds, number of seed tweets, travsersed seeds file and days of difference
    c_path = args.creds
    p_file = args.parent_file
    s_nodes = args.seeds
    d_diff = args.until


    # filename for seed tweets
    level0_filename = tutils.get_par_fname()

    # basic keywords to search for and expanded ones
    keywords = KEYWORDS
    keywords = tclient.expand_keywds(keywords)

    # get them as twitter query
    t_query = tutils.get_seed_query(keywords, d_diff)

    # authenticate as user and also as app (makes searching for replies faster)
    t_user, t_app = tclient.auth_ua(c_path)

    # traversed nodes dict
    traversed = {}

    # call the main traverse through seeds method
    tgraph.traverse_lvl0(t_user, t_app, t_query, s_nodes, level0_filename, p_file, traversed)

    print("[+] Done!")
