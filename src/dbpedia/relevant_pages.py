import plac
from rdflib import Graph


def main(page_ids_ttl, page_links_ttl, out_csv):
    graph = Graph()
    graph.parse(page_ids_ttl, format="ttl")


if __name__ == "__main__":
    plac.call(main)
