# functions related to natural language processing over tweet's content

import __init__
import re
import nltk
from string import punctuation
from nltk.corpus import stopwords
from pycountry import languages
from nltk.probability import FreqDist


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


# get language name from ISO 639 2 or 1 code
def get_lang_name(iso_639_code):
    lan = languages.lookup(iso_639_code).name.lower()

    return lan


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
