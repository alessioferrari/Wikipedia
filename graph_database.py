import networkx as nx
MAX_DEPHT=10

class CategoryCrawler:

    def __init__(self, main_portal, connection):
        # This graph will include all the explored pages
        self.category_graph = nx.DiGraph()
        self.main_cat = main_portal
        self.connection_db = connection

    def get_category_graph(self):
        return self.category_graph

    def search_and_store_graph (self, category, subcategory_depth, parent_node, include_pages):
        """"
		Questa funzione e' chiamata ricorsivamente per esplorare l'albero delle categorie di wikipedia.
		:param category: nome della categoria da cercare
		:param cat_page_id: .
		:param subcategory_depth: profondita esplorazione albero categorie
		:param parent_node: genitore nel grafo
		:param: include_pages: Include le pagine nel grafo se e' vero
		:return: none
		"""

        title = category if category.startswith('Category:') else 'Category:' + category

        #errore, importare ewlinks table
        category_url = ('https://en.wikipedia.org/wiki/' + category.replace(" ", "_"))

        # indent based on the depth of the category: visualisation problems may occur if max_depth is not >>
        # subcategory_depth * 2
        print(" " * ((MAX_DEPHT) - (subcategory_depth * 2)) + category + " URL: " + category_url)

        # adding the category to the graph
        category_node = category_url

        self.category_graph.add_node(title, type='cat')
        if parent_node != 'null':
            self.category_graph.add_edge(parent_node, title)

        new_parent_node = title

        # =========Adding the pages to the categories, if required (generates a very large graph)====

        if include_pages:

            query = 'SELECT cl_from FROM categorylinks WHERE cl_type ="page" AND cl_to="' + (category[9:][0:]).replace(
                " ", "_") + '\"'
            page_results = self.connection_db.query_request(query)
            for page_result in page_results:
                query = "SELECT page_title FROM page WHERE page_id=" + str(page_result[0])
                title_result = self.connection_db.query_request(query)
                try:
                    page_title = str(title_result[0][0], 'utf-8')
                    page_url = 'https://en.wikipedia.org/wiki/' + page_title
                    page_node = "Page:" + page_title
                    print(" " * (MAX_DEPHT - (
                            (subcategory_depth - 1) * 2)) + "Page title: " + page_title + " URL: " + page_url)
                    self.category_graph.add_node(page_node, type='pag')

                    self.category_graph.add_edge(new_parent_node, page_node)
                except IndexError:
                    print(" " * (MAX_DEPHT - ((subcategory_depth - 1) * 2)) + "Document whit page id:" + (
                        str(title_result)[1:-2]) + " Not found!")

            # =======Adding and exploring the subcategories===
        if subcategory_depth > 0:

            search_title = (category[9:]).replace(" ", "_")
            query = 'SELECT cl_from FROM categorylinks WHERE cl_type ="subcat" AND cl_to="' + search_title + '\"'
            subcat_results = self.connection_db.query_request(query)
            for subcat_result in subcat_results:
                query = "SELECT page_title FROM page WHERE page_id=" + str(subcat_result[0])
                result = self.connection_db.query_request(query)
                try:
                    result = 'Category:' + str(result[0][0], 'utf-8')
                    self.search_and_store_graph(result, subcategory_depth - 1, new_parent_node, include_pages)
                except IndexError:
                    print(" " * (MAX_DEPHT - ((subcategory_depth - 1) * 2)) + "Document whit page id:" + (
                        str(subcat_result)[1:-2]) + " Not found!")
