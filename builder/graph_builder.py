#!/usr/bin/python3

import json
import argparse
import networkx as nx


# standard argparser function
def get_args():
    parser = argparse.ArgumentParser(description = "Twitter User Relationship graph builder "\
            "for a given tweet input file in json, taking only user mentions (replies) and "\
            "retweets into account. Outputs a graph in several file formats in "\
            "undirected or directed and weighted or weightless version of the graph. Made "\
            "for the project of ID2211 at KTH.", epilog = "Made by <pjan2@kth.se>")

    # input file
    parser.add_argument("-i", "--input", help = "Path to the input file with all files",
            required = True)

    # output file
    parser.add_argument("-o", "--output", help = "Path to output file with graph",
            required = True)

    # outfile format
    parser.add_argument("-f", "--format", help = "Output file format (Default: GEXF)",
            choices = ["edgelist", "gexf", "dot", "gml"], default = "gexf")

    # get directed graph version
    parser.add_argument("--undirected", action = "store_true",
            help = "Get the undirected version of the user graph (Default is directed)")

    # get the weighted version
    parser.add_argument("--weighted", action = "store_true", help = "Get the "\
            "weighted version for the graph (Default is unweighted - W=1)")

    return parser.parse_args()


# add nodes and edges
def add_entities(G, from_user, to_user, weighted):
    # get id and handle from both users
    f_id, f_handle = from_user
    t_id, t_handle = to_user

    # add both nodes (doesn't create dups)
    G.add_node(f_id, screen_name = f_handle)
    G.add_node(t_id, screen_name = t_handle)

    # default weight
    w = 1

    if G.has_edge(f_id, t_id) and weighted:
        # sum up the previous weight and update
        w = G[f_id][t_id]['weight'] + 1

    # doesn't create dup edges
    G.add_edge(f_id, t_id, weight = w)

    return


# traverse tweets and populate graph
def populateGraph(G, in_path, weighted):
    # retweet key
    ret_id = 'retweeted_status'

    with open(in_path, 'r') as tweet_file:
        for raw_tweet in tweet_file.readlines():
            try:
                tweet = json.loads(raw_tweet)
            except Exception as e:
                print(f"[!] FATAL ERROR WHILE READING TWEETS: {e}")
                exit(127)

            # get user handle and user id as string
            user = tweet['user']['screen_name']
            user_id = tweet['user']['id_str']
            u_node = (user_id, user)

            # check if tweet is a reply (or mentions an user)
            if tweet.get('entities').get('user_mentions'):
                # collect entities (user ids and handles) and add nodes/edges
                for u in tweet['entities']['user_mentions']:
                    to_u_node = (u['id_str'], u['screen_name'])
                    add_entities(G, u_node, to_u_node, weighted)

            # check if tweet is a retweet
            elif tweet.get(ret_id):
                to_u_node = (tweet[ret_id]['user']['id_str'], tweet[ret_id]['user']['screen_name'])
                add_entities(G, tweet, to_u_node, weighted)

    return G


# make undirected version of graph summing both weights
def make_undirected(G, weighted):
    new_edges = {}

    # first check if we care about the weights
    if not weighted:
        new_G = nx.Graph(G)
        # otherwise just set them to 1 after making the graph undirected
        for a, b in new_G.edges():
            new_G[a][b]['weight'] = 1
            
        return new_G


    # get the sum of weights into new edges
    for a,b in G.edges():
        e1 = "{}-{}".format(a, b)
        e2 = "{}-{}".format(b, a)
        w = G[a][b]['weight']

        # if neither have been processed already
        if not new_edges.get(e1) and not new_edges.get(e2):
            new_edges[e1] = w
        # if the other version already exists we only need to add it with current one
        elif new_edges.get(e2):
            new_edges[e2] += w

    # add nodes to new graph
    new_G = nx.Graph()
    new_G.add_nodes_from(G)

    # add node attributes
    for node, all_attr in G.nodes.data():
        for attr in all_attr:
            new_G.nodes[node][attr] = G.nodes[node][attr]

    # add updated edges to graph
    for e in new_edges:
        a, b = e.split("-")
        new_G.add_edge(a, b, weight = new_edges[e])

    return new_G


# save file according to file format ending
def saveGraph(G, out_path, fmt, weighted):
    if fmt == "edgelist":
        if weighted:
            nx.write_weighted_edgelist(G, out_path + ".wedgelist")
        else:
            nx.write_edgelist(G, out_path + ".edgelist", data = False)

    elif fmt == "gexf":
        nx.write_gexf(G, out_path + ".gexf")

    elif fmt == "gml":
        nx.write_gml(G, out_path + ".gml")

    elif fmt == "dot":
        nx.nx_pydot.write_dot(G, out_path + ".dot")

    return


# main piece of code
if __name__ == "__main__":
    # get arguments
    args = get_args()

    # extract them into vars
    inp_p = args.input
    out_p = args.output
    undirected = args.undirected
    weighted = args.weighted
    fmt = args.format

    # create directed graph
    G = nx.DiGraph()

    # populate it with nodes and edges
    G = populateGraph(G, inp_p, weighted)

    # if directed is not set
    if undirected:
        # transform to undirected
        G = make_undirected(G, weighted)

    # save graph to output file
    saveGraph(G, out_p, fmt, weighted)

    print(f"[+] Graph written at \'{out_p}.{fmt}\'")
