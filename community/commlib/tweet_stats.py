# related to stats and metrics associated with tweets (e.g that can be found inside tweets)
# (single and multi item metrics from tweets, like common words, hashtags and also the bulk stats aggregator)


import __init__
from community.commlib.utils import n_most_common_items
from community.commlib.nlp import *



# get all hashtags from list
def get_hashtags(h_list):
    hashtags = {}
    for h in h_list:
        h_tag = "#" + h['text']
        hashtags[h_tag] = 1

    return hashtags


# get specified singular metric from tweet (only one per tweet)
# (location freq, language freq, and so on)
def get_single_metric(metr_val, metr_name, u, u_metrics):
    # check if metric dict already exists
    if not u_metrics[u].get(metr_name):
        u_metrics[u][metr_name] = {}

    # check if user already has this field inside certain metric
    if not u_metrics[u][metr_name].get(metr_val):
        u_metrics[u][metr_name][metr_val] = 0
    u_metrics[u][metr_name][metr_val] += 1

    return


# get specified multiple metric from tweet (many per tweet)
# (common words, hashtags used)
def get_multi_metric(metr_values, metr_name, u, u_metrics):
    # check special case
    if metr_name == "hashtag":
        metr_values = get_hashtags(metr_values)

    # check if metric dict already exists
    if not u_metrics[u].get(metr_name):
        u_metrics[u][metr_name] = metr_values
    else:
        for item, f in metr_values.items():
            # if it exists check if given item also exist, if it does, add frequency to prev one
            if not u_metrics[u][metr_name].get(item):
                u_metrics[u][metr_name][item] = 0
            u_metrics[u][metr_name][item] += f

    return


# get the most common words used in given tweet
def get_most_common_words(full_text, lang_code, u, u_metrics):
    # reduce noise from the text, get frequency of remaining words
    # and get the 200 most common ones used
    filt_words = filter_words(full_text, lang_code)
    word_freqs = get_freq(filt_words)
    common_words  = n_most_common_items(word_freqs, 200)

    # get multi metrics from all words
    get_multi_metric(common_words, 'words', u, u_metrics)

    return


# get metrics for users to help identify communities
def common_metrics(users, users_tweets):
    # go through every user's tweet and grab the languages used
    for u in users:
        for tweet in users_tweets[u]:
            # attempt to recover the full name for this language
            try:
                lang = get_lang_name(tweet['lang'])
            except Exception as e:
                lang = tweet['lang']
                print(f"[!] ISO-639 language code \'{lang}\' not found (user \'{u}\')...")

            # get languages used from tweets made by this user
            get_single_metric(lang, 'language', u, users)

            # get all locations for this user (sometimes can be blank)
            get_single_metric(tweet['user']['location'], 'location', u, users)

            # get all hashtags made by this user (sometimes can be blank)
            get_multi_metric(tweet['entities']['hashtags'], 'hashtag', u, users)

            # get most common words used by this user
            get_most_common_words(tweet['full_text'], tweet['lang'], u, users)


    return users


# get aggregated metrics for a community
def aggregated_metrics(users):
    community = {}

    # go through every user and metric
    for u in users:
        for metr in users[u]:
            # check if given metric is not present and add it
            if not community.get(metr):
                community[metr] = users[u][metr]
            else:
                # otherwise just check if inside values exist and add their frequencies
                for val, freq in users[u][metr].items():
                    if not community[metr].get(val):
                        community[metr][val] = 0
                    community[metr][val] += freq

    # get only the 20 most common words, langs and locs for the whole community
    for metr in community.keys():
        community[metr] = n_most_common_items(community[metr], 20)

    return community
