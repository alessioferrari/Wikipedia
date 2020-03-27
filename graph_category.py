import sys
import networkx as nx

from MySQLdb._exceptions import OperationalError
from connection_database import Connection
from graph_wikipedia import CategoryWikipedia
from graph_database import CategoryCrawler

# problem whit ' in the name
# python3 graph_category.py "Category:Tom_Clancy's_Net_Force" 4
# python3 graph_category.py "Category:Artificial intelligence" 4


def main():
    portal = sys.argv[1:][0]
    subcategory_depth = int(sys.argv[1:][1])
    try:
        c = Connection()
        d = CategoryCrawler(portal, c)
        try:
            d.search_and_store_graph(portal, subcategory_depth=subcategory_depth,parent_node="null", include_pages=True)
        except OperationalError as e:
            print(e)
            return -1
        finally:
            c.close()
    except OperationalError as e:
        d = CategoryWikipedia(portal)
        d.search_and_store_graph(portal, subcategory_depth=subcategory_depth, parent_node="null", include_pages=True)
    graph_file_name = portal + '_D' + str(subcategory_depth) + '_category_graph.graphml'
    nx.write_graphml(d.get_category_graph(), graph_file_name)
    print('Cytoscape graph saved in ' + graph_file_name)


if __name__ == "__main__":
    main()
