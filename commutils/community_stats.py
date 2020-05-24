#!/usr/bin/python3

import re
import json
import nltk
import argparse
import numpy as np
import matplotlib.pyplot as plt
from time import ctime
from string import punctuation
from pycountry import languages
from nltk.corpus import stopwords
from nltk.probability import FreqDist


# standard argument parser
def get_args():
    parser = argparse.ArgumentParser(description = "Tool to aide in the task of labeling communities "\
            "given by a file with user ID's in one line separated by tabs. Gathers stats from the tweets "\
            "of those users and shows aggregated stats as output. Made for the final project of Group 11 "\
            "for ID2211 at KTH", epilog = "Made by <pjan2@kth.se>")

    # path to file with all tweets
    parser.add_argument("-t", "--tweet-file", help = "Path to the file with all the tweets",
            required = True)

    # path to file with the community
    parser.add_argument("-c", "--comm-file", help = "Path to the file with a given community",
            required = True)

    # save stats into file instead of showing them on the run
    parser.add_argument("-s", "--save-stats", action = "store_true", help = "Save stats and plots into disk "\
                        "instead of showing them after each run")

    return parser.parse_args()


# parse community file and return as dict
def get_users(comm_path):
    users = {}
    with open(comm_path, 'r') as comm_f:
        user_list = comm_f.readline().strip('\n').split('\t')
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


# attempt to download used packages
def set_nltk_packages():
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
    except Exception as e:
        print(f"[!] Exception while downloading packages: {e}")
        exit(127)

    return


# get frequency of words from tokenized text
def get_freq(token_text):
    return nltk.FreqDist(token_text)


# get n most common words (10 by default)
def n_most_common_items(item_dict, limit = 10):
    most_common = {}
    sorted_items = sorted(item_dict.items(), key = lambda tup: tup[1], reverse = True)
    n_most_common = sorted_items[:limit]

    for w, f in n_most_common:
        w = "NULL" if w == "" else w
        most_common[w] = f

    return most_common


# get language name from ISO 639 2 or 1 code
def get_lang_name(iso_639_code):
    lan = languages.lookup(iso_639_code).name.lower()

    return lan


# get extended keywords
def get_keywords():
    keywds = ['covid 19', 'sars cov 2', 'coronavirus']
    new_keywds = []

    # extend with lowercase, uppercase and capitalized version
    for kw in keywds:
        tmp = [kw, kw.upper(), kw.lower(), kw.capitalize()]
        # extend joining if they have spaces
        new_keywds += tmp + list(map(lambda w: w.replace(" ", ""), tmp))

    return new_keywds


# remove noise chars and words from text and return cleaned word list
def filter_words(text, lan_code):
    cleaned_words = []

    # remove user mentions from text (handles)
    text_hfil = re.sub("(@[0-9A-Za-z_]+)", "", text)

    # remove punctuation chars from text
    text_pfil = text_hfil.translate(str.maketrans("", "", punctuation))

    # get tokenized version of text
    text_token = nltk.tokenize.word_tokenize(text_pfil)

    # remove keywords used to search for tweets
    for keywd in get_keywords():
        try:
            text_token.remove(keywd)
        except ValueError:
            pass

    try:
        # get common words in language given
        lan = get_lang_name(lan_code)
        stop_words = stopwords.words(lan)

        # ...and remove them
        for tok in text_token:
            if tok not in stop_words:
                cleaned_words.append(tok)

    except Exception as e:
        # return the previous tokenized version (language is not supported)
        cleaned_words = text_token

    return cleaned_words


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


# plotting function
def show_community_stats(comm_stats, saved):
    # setup size of figure (width, height)
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 15
    fig_size[1] = 7
    plt.rcParams["figure.figsize"] = fig_size

    # go through every metric
    for metr in comm_stats:
        x = comm_stats[metr].keys()
        y = comm_stats[metr].values()

        ax = plt.subplot(1,1,1, xlabel = metr, ylabel = "frequency",
                        title = f"20 most common for: \'{metr}\'")

        # standard width for regular metrics
        c_width = 0.65

        # get bigger gap between bins if we are dealing with troublesome metrics
        if metr in ['words', 'hashtag']:
            c_width = 0.3

        # bar plot
        ax.bar(x, y, width = c_width, color = "darkblue", alpha = 0.8)

        if saved:
            out_path = f"20_most_common-{metr}.png"
            plt.savefig(out_path)
            print(f"[+] Saved histogram for \'{metr}\' at \'{out_path}\'")
        else:
            plt.show()

    return


# save stats into file
def save_stats(comm_stats):
    out_path = "community_report.txt"
    # general strings used for every field
    ban_1 = "=" * 40
    ban_2 = "\n\t\t"
    ban_3 = "\n\n"

    with open(out_path, 'w+') as stat_f:
        # write title and current time it was created
        stat_f.write(f"{ban_1}{ban_2}Community Stats{ban_2[::-1]}{ban_1}\n")
        stat_f.write(f"Made on {ctime()}{ban_3}")

        # go through every metric gathering stats into a long string
        for metr in comm_stats:
            # banner for the metric name (acts as separator)
            banner = f"{ban_1}{ban_2}{metr.upper()}{ban_2[::-1]}{ban_1}{ban_3}"
            content = banner

            # get total freqs
            total_f = sum(comm_stats[metr].values())

            for item, freq in comm_stats[metr].items():
                # add it like a normalized histogram with frequency
                norm_f = round(freq * 100 / total_f)
                item_title = f"{item} ({freq}):".ljust(40)
                content += f"{item_title}{'#' * norm_f}\n"

            # and then write the string to file
            content += "\n\n"
            stat_f.write(content)

    print(f"[+] Written stats at \'{out_path}\'!")

    return


# main piece of code
if __name__ == "__main__":
    # get arguments
    args = get_args()

    # and throw them into vars
    tweet_f = args.tweet_file
    comm_f = args.comm_file
    saved = args.save_stats

    # set nltk if packages haven't been downloaded
    set_nltk_packages()

    # get all users from community and all tweets from file
    users = get_users(comm_f)
    users_tweets = get_all_tweets(tweet_f, users)

    # get fine-grained common metrics for users
    users = common_metrics(users, users_tweets)

    # aggregate these metrics
    comm_stats = aggregated_metrics(users)

    # plot or save the aggregated stats
    show_community_stats(comm_stats, saved)

    if saved:
        # save the aggregated stats
        save_stats(comm_stats)
