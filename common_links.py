import sys
import networkx as nx
from MySQLdb._mysql import OperationalError

from connection_database import Connection
from graph_database import CategoryCrawler
from graph_wikipedia import CategoryWikipedia
'''
Possibili interzioni sono:
- (-c) Catgeorie in comune
- (-p) Pagine e categorie in comune
'''


def get_common_category(cat_source, cat_dest):
	pages_categories_map = {}
	pages_url_map = {}

	graph_nodes = nx.DiGraph(cat_source.get_category_graph())
	nodes_dest = graph_nodes.nodes
	nodes_source = nx.DiGraph(cat_dest.get_category_graph()).nodes
	nodes_dest_category_only = [n for n in nodes_dest if n.startswith('Category:')]
	nodes_source_category_only = [n for n in nodes_source if n.startswith('Category:')]
	nodes_set = set(nodes_dest_category_only).intersection(set(nodes_source_category_only))
	print("Pagine in comune")
	for node in (list(nodes_set)):
		print("Title:"+node+ "URL:"+ graph_nodes.node[node]['url'])

def get_common_page_category(cat_source, cat_dest):
	pages_categories_map = {}
	pages_url_map = {}

	graph_nodes = nx.DiGraph(cat_source.get_category_graph())
	nodes_dest = graph_nodes.nodes
	nodes_source = nx.DiGraph(cat_dest.get_category_graph()).nodes
	nodes_set = set(nodes_dest).intersection(set(nodes_source))
	print("Pagine in comune")
	for node in (list(nodes_set)):
		print("Title:"+node+ "URL:"+ graph_nodes.node[node]['url'])

#Esempio: python3 common_links.py "Category:Emerging technologies" "Category:Artificial intelligence" 1 -c
def main():
	category_1 = sys.argv[1:][0]
	category_2=sys.argv[1:][1]
	subcategory_depth = int(sys.argv[1:][2])
	mode= sys.argv[1:][3]
	if(mode =="-c"):
		include_pages=False;
	elif(mode =="-p"):
		include_pages=True;
	else:
		return -1

	try:
		c = Connection()
		g_1 = CategoryCrawler(category_1, c)
		g_2 = CategoryCrawler(   category_2, c)
		try:
			g_1.search_and_store_graph(category_1, subcategory_depth=subcategory_depth,parent_node="null", include_pages=include_pages)
			g_2.search_and_store_graph(category_2, subcategory_depth=subcategory_depth,parent_node="null", include_pages=include_pages)
		except OperationalError as e:
			print(e)
			return -1
		finally:
			c.close()
	except OperationalError as e:
		g_1 = CategoryWikipedia(category_1)
		g_2 = CategoryWikipedia(category_2)
		g_1.search_and_store_graph(category_1, subcategory_depth=subcategory_depth, parent_node="null", include_pages=include_pages)
		g_2.search_and_store_graph(category_2, subcategory_depth=subcategory_depth, parent_node="null", include_pages=include_pages)
	if(include_pages):
		get_common_page_category(g_1,g_2)
	else:
		get_common_category(g_1, g_2)

if __name__ == "__main__":
    main()
