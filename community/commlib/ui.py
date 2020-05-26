# related to user interaction functions
# (argument parser, stats plotter and stats save to disk)


import __init__
import argparse
import numpy as np
import matplotlib.pyplot as plt
from time import ctime
from adjustText import adjust_text


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


# plotting function
def show_community_stats(comm_stats, saved):
    # setup size of figure (width, height)
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 15
    fig_size[1] = 7
    plt.rcParams["figure.figsize"] = fig_size

    # go through every metric
    for metr in comm_stats:
        x_labels = list(comm_stats[metr].keys())
        x = list(range(1, len(x_labels) + 1))
        y = list(comm_stats[metr].values())

        ax = plt.subplot(1,1,1, xlabel = metr, ylabel = "frequency",
                        title = f"20 most common for: \'{metr}\'")

        # standard width for regular metrics
        c_width = 0.65

        # get bigger gap between bins (less width for bins) if we are
        #    dealing with troublesome metrics
        if metr in ['words', 'hashtag']:
            c_width = 0.3

        # bar plot
        bars = ax.bar(x, y, tick_label = x, width = c_width, color = "darkblue", alpha = 0.8)
        texts = []

        # get coords for bars and append text
        # based on: https://github.com/Phlya/adjustText/blob/master/docs/source/Examples.ipynb
        for j,rect in enumerate(bars):
            left = rect.get_x() + 0.14
            top = rect.get_y() + rect.get_height() - 0.2
            texts.append(ax.text(left, top, f"{x_labels[j]}"))

        # move text as to remove overlapping labels (can take some time)
        adjust_text(texts, add_objects = bars, arrowprops=dict(arrowstyle='->', color="red"),
                    autoalign = 'x', only_move = {'points': 'y', 'text': 'y',
                    'objects': 'y'}, ha = "center", va = "bottom")

        # check if we want to show it or save it to file
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
    ban_1 = "=" * 80
    ban_2 = "\n\t\t\t\t"
    ban_3 = "\n\n"

    with open(out_path, 'w+', encoding="utf-8") as stat_f:
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
