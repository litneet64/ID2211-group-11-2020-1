#!/usr/bin/python3

import __init__
import os
import re
import json
import requests
import argparse
import base64
import community.commlib.utils as cutils


# standard argument parser
def get_args():
    parser = argparse.ArgumentParser(description = "Tool to create a visual "\
            "representation for tweets from a json tweet file as an html, if "\
            "user file is passed then it attempts to retrieve all users tweets "\
            "from the first file to output. Based on the code for \'wall.py\' "\
            "on the twarc repo, however substantial modifications were made. Made "\
            "for the final project of Group 11 for ID2211 at KTH",
             epilog = "Made by <pjan2@kth.se>")

    # path to file with all tweets
    parser.add_argument("-t", "--tweet-file", help = "Path to the file with "\
            "all the tweets in json format", required = True)

    # path to file with users
    parser.add_argument("-u", "--user-file", help = "Path to the file with "\
            "users, separated with tabs and/or newlines", default = "")

    # output path to avatars and html file
    parser.add_argument("-o", "--out-path", help = "Path to output dir "\
            "(Default is current one)", default = "")

    return parser.parse_args()


# download any file from given url
def download_file(url, avatar_dir):
    # local filename, requests and output file
    local_fname = os.path.split(url)[1]
    res = requests.get(url, stream = True)
    out_path = os.path.join(avatar_dir, local_fname)

    # do not overwrite existent files with same name
    if os.path.isfile(out_path):
        return local_fname

    # write downloaded image into file
    with open(out_path, "+wb") as out_f:
        for chunk in res.iter_content(chunk_size = 1024):
            # filter out keep-alive chunks
            if chunk:
                out_f.write(chunk)
                out_f.flush()

    return local_fname


# retrieve text content from tweet
def get_text(tweet):
    # get all possible options to retrieve tweet content
    text_1 = tweet.get("full_text")
    text_2 = tweet.get("text")
    text_3 = tweet.get("extended_tweet", {}).get("full_text")

    return text_3 or text_2 or text_1


# create dir for output html and avatars if it does not exist
def setup_dirs(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)

    return


# get file path and avatars path
def get_paths(base_path):
    # dir for all related output
    final_path = os.path.join(base_path, "visual_tweets")

    # file path and avatar dir path
    out_file = os.path.join(final_path, "visual_tweets.html")
    avatar_dir = os.path.join(final_path, "avatars")

    # check dirs were created
    for dir in [final_path, avatar_dir]:
        setup_dirs(dir)

    return out_file, avatar_dir


# write part of the html header
def write_header(html_file):
    header = "PCFkb2N0eXBlIGh0bWw+CjxodG1sPgo8aGVhZD4KICA8bWV0YSBjaGFyc2V0PSJ1dGYtOCI+\
              CiAgPHRpdGxlPlR3aXR0ZXIgV2FsbCBWaXN1YWxpemF0aW9uPC90aXRsZT4KICA8c3R5bGU+\
              CiAgICBib2R5IHsKICAgICAgZm9udC1mYW1pbHk6IEFyaWFsLCBIZWx2ZXRpY2EsIHNhbnMtc\
              2VyaWY7CiAgICAgIGZvbnQtc2l6ZTogMTJwdDsKICAgICAgbWFyZ2luLWxlZnQ6IGF1dG87Ci\
              AgICAgIG1hcmdpbi1yaWdodDogYXV0bzsKICAgICAgd2lkdGg6IDk1JTsKICAgICAgYmFja2d\
              yb3VuZC1jb2xvcjogIzAwY2NmZjsKICAgIH0KICAgIGFydGljbGUudHdlZXQgewogICAgICBw\
              b3NpdGlvbjogcmVsYXRpdmU7CiAgICAgIGZsb2F0OiBsZWZ0OwogICAgICBib3JkZXI6IHRoa\
              W4gIzAwMDAwMCBzb2xpZDsKICAgICAgbWFyZ2luOiAxMHB4OwogICAgICB3aWR0aDogMjcwcH\
              g7CiAgICAgIHBhZGRpbmc6IDIwcHg7CiAgICAgIGhlaWdodDogMjIwcHg7CiAgICAgIGJhY2t\
              ncm91bmQtY29sb3I6ICNmZmZmZmY7CiAgICB9CiAgICAubmFtZSB7CiAgICAgIGZvbnQtd2Vp\
              Z2h0OiBib2xkOwogICAgfQogICAgaW1nLmF2YXRhciB7CiAgICAgICAgdmVydGljYWwtYWxpZ\
              246IG1pZGRsZTsKICAgICAgICBmbG9hdDogbGVmdDsKICAgICAgICBtYXJnaW4tcmlnaHQ6ID\
              EwcHg7CiAgICAgICAgYm9yZGVyLXJhZGl1czogNXB4OwogICAgICAgIGhlaWdodDogNDVweDs\
              KICAgIH0KICAgIC50d2VldCBmb290ZXIgewogICAgICBwb3NpdGlvbjogYWJzb2x1dGU7CiAg\
              ICAgIGJvdHRvbTogNXB4OwogICAgICBsZWZ0OiAxMHB4OwogICAgICBmb250LXNpemU6IHNtY\
              WxsZXI7CiAgICB9CiAgICAudHdlZXQgYSB7CiAgICAgIHRleHQtZGVjb3JhdGlvbjogbm9uZT\
              sKICAgIH0KICAgIC50d2VldCAudGV4dCB7CiAgICAgIGhlaWdodDogMTMwcHg7CiAgICAgIG9\
              2ZXJmbG93OiBhdXRvOwogICAgfQogICAgZm9vdGVyI3BhZ2UgewogICAgICBtYXJnaW4tdG9w\
              OiAxNXB4OwogICAgICBjbGVhcjogYm90aDsKICAgICAgd2lkdGg6IDEwMCU7CiAgICAgIHRle\
              HQtYWxpZ246IGNlbnRlcjsKICAgICAgZm9udC1zaXplOiAyMHB0OwogICAgICBmb250LXdlaW\
              dodDogaGVhdnk7CiAgICB9CiAgICBoZWFkZXIgewogICAgICB0ZXh0LWFsaWduOiBjZW50ZXI\
              7CiAgICAgIG1hcmdpbi1ib3R0b206IDIwcHg7CiAgICB9CiAgPC9zdHlsZT4KPC9oZWFkPgo8\
              Ym9keT4KICA8aGVhZGVyPgogIDxoMT5Ud2VldCBWaXN1YWxpemF0aW9uPC9oMT4KICA8ZW0+Q\
              mFzZWQgb24gd2FsbCB0b29sIGZyb20gdHdhcmM8L2VtPgogIDwvaGVhZGVyPgogIDxkaXYgaWQ\
              9InR3ZWV0cyI+Cg=="

    # decode base64 header and write it into file
    header = base64.b64decode(header.encode())
    html_file.write(header.decode())

    return


# write part of the html footer
def write_footer(html_file):
    footer = '</div><footer id="page"><hr>'\
             '</footer></body></html>'

    # write footer into file
    html_file.write(footer)

    return


# traverse through tweet file parsing tweet contents
def write_from_file(in_path, out_path, av_dir):
    # read all tweets from input file and write them to out file
    with open(in_path) as tweet_f:
        with open(out_path, "+w") as html_f:
            # write header for html file
            write_header(html_f)

            for raw_t in tweet_f.readlines():
                tweet = json.loads(raw_t)
                # get and write html for this tweet
                t_html = tweet_to_html(tweet, av_dir)
                html_f.write(t_html)

            # write footer for html file
            write_footer(html_f)

    return


# write tweets to html from a user-tweet data struct
def write_from_tweets(users_tweets, out_p, av_dir):
    with open(out_p, "w") as html_f:
        # write header for html file
        write_header(html_f)

        for u in users_tweets:
            for tweet in users_tweets[u]:
                t_html = tweet_to_html(tweet, av_dir)
                html_f.write(t_html)

        # write footer for html file
        write_footer(html_f)

    return


# get one tweet as html
def tweet_to_html(tweet, avatar_dir):
    # download avatar
    avatar_url = tweet["user"]["profile_image_url"]
    filename = download_file(avatar_url, avatar_dir)

    # get lastname for avatar dir
    avatar_dir = os.path.split(avatar_dir)[1]

    # parse tweet into custom dict
    t = {
            "created_at": tweet['created_at'],
            "name": tweet['user']['name'],
            "username": tweet['user']['screen_name'],
            "user_url": "http://twitter.com/{}".format(tweet['user']['screen_name']),
            "text": get_text(tweet),
            "avatar": "{}/{}".format(avatar_dir, filename),
            "url": "http://twitter.com/{}/status/{}".format(tweet['user']['screen_name'], tweet['id_str']),
            "retweet_count": tweet['retweet_count']
        }

    # single or plural form for 'retweet'
    t['retweet_string'] = "retweet" if t['retweet_count'] == 1 else "retweets"

    # get full urls if they tweeted one
    for url in tweet['entities']['urls']:
        link = f'<a href="{url["expanded_url"]}">{url["url"]}</a>'
        t['text'] = t['text'].replace(url['url'], link)

    # links to twitter handles/hashtags and their regexes
    twitt_hashs = [(" @([^ ]+)", " <a href=\"http://twitter.com/\g<1>\">@\g<1></a>"),
            (" #([^ ]+)", " <a href=\"https://twitter.com/search?q=%23\g<1>&src=hash\">#\g<1></a>")
            ]

    # if it finds handle or hashtag, add link to user/hashtag on the html
    for reg, url in twitt_hashs:
        t['text'] = re.sub(reg, url, t['text'])

    # get html version for tweet
    tweet_html = parse_tweet_html(t)

    return tweet_html


# create the html for this one tweet
def parse_tweet_html(t):
    html = f'<article class="tweet">\n'\
           f'<img class="avatar" src="{t["avatar"]}">\n'\
           f'<a href="{t["user_url"]}" class="name">{t["name"]}</a><br>\n'\
           f'<span class="username">{t["username"]}</span><br><br>\n'\
           f'<div class="text">{t["text"]}</div><br><footer>\n'\
           f'{t["retweet_count"]} {t["retweet_string"]}<br>\n'\
           f'<a href="{t["url"]}"><time>{t["created_at"]}</time></a>\n'\
           '</footer></article>\n'

    return html




# main piece of code
if __name__ == "__main__":
    # get args
    args = get_args()

    # pass them into vars
    tweet_p = args.tweet_file
    user_p = args.user_file
    out_p = args.out_path

    # get path for out file and avatar dir
    out_f, av_dir = get_paths(out_p)

    # get users from file if flag was passed and write them into html
    if user_p:
        users = cutils.get_users(user_p)
        tweets = cutils.get_all_tweets(tweet_p, users)
        write_from_tweets(tweets, out_f, av_dir)

    else:
        # otherwise traverse tweet file and write them
        write_from_file(tweet_p, out_f, av_dir)

    print(f"[+] HTML file written at \'{out_f}\'")
