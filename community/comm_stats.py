#!/usr/bin/python3

import __init__
import community.commlib.ui as cui
import community.commlib.utils as cutils
import community.commlib.nlp as cnlp
import community.commlib.tweet_stats as ctstats


# main piece of code
if __name__ == "__main__":
    # get arguments
    args = cui.get_args()

    # and throw them into vars
    tweet_f = args.tweet_file
    comm_f = args.comm_file
    saved = args.save_stats

    # set nltk if packages haven't been downloaded
    cnlp.set_nltk_packages()

    # get all users from community and all tweets from file
    users = cutils.get_users(comm_f)
    users_tweets = cutils.get_all_tweets(tweet_f, users)

    # get fine-grained common metrics for users
    users = ctstats.common_metrics(users, users_tweets)

    # aggregate these metrics
    comm_stats = ctstats.aggregated_metrics(users)

    # plot or save the plots for the aggregated stats
    cui.show_community_stats(comm_stats, saved)

    if saved:
        # save the aggregated stats
        cui.save_stats(comm_stats)
