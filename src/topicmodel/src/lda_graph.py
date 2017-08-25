import codecs
import networkx as nx
from itertools import combinations

f = codecs.open('data/corpus/docs_topic.tsv', 'r', 'utf-8')
edges = []
nodes = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
         25,26]
# name = {
#     '0': 'Nagyobb csoportok',
#     '1': 'Kisebb csoportok: egyéni portrék, stb.',
#     '2': 'Úton',
#     '3': 'Kisebb csoportok: családok, egyének',
#     '4': 'Egyéni portrék, politikusok, stb.',
#     '5': 'Adatok',
#     '6': 'Átkelés'
# }

name = {}
for i in range(0,27):
    name[str(i).zfill(2)] = 'Topic ' + str(i).zfill(2)

nodes = [str(n).zfill(2) for n in nodes]
edge_counts = {}
possible_edges = list(combinations(nodes, 2))
for edge in possible_edges:
    edge_counts[edge] = 0

for l in f:
    l = l.strip().split('\t')
    ns = sorted(l[1].split('|'))
    combos = list(combinations(ns, 2))
    for combo in combos:
        if combo in edge_counts.keys():
            edge_counts[combo] += 1
        elif (combo[1], combo[0]) in edge_counts.keys():
            edge_counts[(combo[1], combo[0])]

G = nx.Graph()
for n in nodes:
    G.add_node(n, name=name[n])

for e in edge_counts:
    G.add_edge(e[0], e[1], weight=edge_counts[e])

nx.write_graphml(G, "data/corpus/topic_graph.graphml")