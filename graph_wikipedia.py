import networkx as nx
import requests
import wikipedia
from wikipedia.exceptions import PageError, DisambiguationError
#
API_URL = 'http://en.wikipedia.org/w/api.php'  # Wikipedia web
# WIKI_PAGE_PREFIX = 'https://en.wikipedia.org/'
MAX_DEPHT = 10


def _wiki_request(params):
    '''
    Make a request to the Wikipedia API using the given search parameters.
    Returns a parsed dict of the JSON response.
    '''

    params['format'] = 'json'
    if not 'action' in params:
        params['action'] = 'query'

    r = requests.get(API_URL, params=params)
    return r.json()


def _wiki_search_url_by_ID(page_ID):
    search_page_ID = {
        'prop': 'info',
        'pageids': page_ID,
        'inprop': 'url'
    }

    # return _wiki_request(search_page_ID)['query']['pages'][str(page_ID)]['fullurl']
    return _wiki_request(search_page_ID)['query']['pages']


def _wiki_search_cat_ID_by_name(cat_name):
    # Example: https://www.mediawiki.org/w/api.php?action=query&titles=Category:Artificial%20intelligence

    search_cat_ID = {
        'titles': cat_name
    }

    # This searches the first element in the returned json dictionary
    return next(iter(_wiki_request(search_cat_ID)['query']['pages']))


# This funciton search the URL of the main wikipedia page of a certain category
# by inspecting the content of the category page
def _wiki_search_main_page_for_cat(cat_ID):
    params_cat_content = {
        'action': 'parse',
        'pageid': cat_ID,
        'prop': 'text'
    }


class CategoryWikipedia:

    def __init__(self, main_portal):
        # This graph will include all the explored pages
        self.category_graph = nx.DiGraph()
        self.main_cat = main_portal

    def _get_main_page_from_category(self, category_name):

        # Note that the title of the page can be different from the category,
        # but (in most of the cases), the wikipedia API gets the right page.
        # in case it doesn't, we raise the error.

        try:
            if category_name.startswith('Category:'):
                wiki_page = wikipedia.page(category_name[len('Category:'):])
            else:
                wiki_page = wikipedia.page(category_name)
        except Exception:
            raise
        return wiki_page

    def get_category_graph(self):
        return self.category_graph

    def search_and_store_graph(self, category, subcategory_depth, parent_node, include_pages):
        '''
        This function is called recursively to explore the tree of categories from
        Wikipedia.
        :param category: category name to search
        :param cat_page_id: it is the ID of the category page. If unknown (at the beginning), the page will be searched by name. Otherwise the page is searched by ID.
        :param subcategory_depth: depth to explore in the tree of subcategories
        :param parent_node: parent node in the graph
        :param: include_pages: if True adds also the pages to the graph and not only the categories
        (may result in large graphs)
        :return: none
        '''
        category_url = ('https://en.wikipedia.org/wiki/' + category.replace(" ", "_"))
        # indent based on the depth of the category: visualisation problems may occur if max_depth is not >> 
        # subcategory_depth * 2 
        print(" " * ((MAX_DEPHT) - (subcategory_depth * 2)) + category + " URL: " + category_url)
        # adding the category to the graph
        category_node = category_url
        title = category if category.startswith('Category:') else 'Category:' + category
        new_parent_node = title


        # create Graph
        self.category_graph.add_node(title, type="cat", url=category_url)
        if parent_node != "null":
            self.category_graph.add_edge(parent_node, title, type='cat')

        # =========Adding the pages to the categories, if required (generates a very large graph)====
        # Check this website for param structure: https://www.mediawiki.org/wiki/API:Categorymembers
        if include_pages:
            search_params_pages = {
                'list': 'categorymembers',
                'cmtype': 'page',
                'cmprop': 'ids|title',
                'cmlimit': 500,
                'cmtitle': title}

            page_results = _wiki_request(search_params_pages)['query']['categorymembers']
            for i in range(len(page_results)):

                if (i == 0) | (i % 50 == 0):
                    page_id = str(page_results[i]['pageid'])
                else:
                    page_id = page_id + "|" + str(page_results[i]['pageid'])

                if (i > 0) & (i % 49 == 0) | (i == len(page_results) - 1):
                    page_info = _wiki_search_url_by_ID(page_id)
                    for page in page_info:
                        page_info_title = page_info[page]['title']
                        page_info_url = page_info[page]['fullurl']
                        page_info_id = page_info[page]['pageid']
                        # self.category_graph.add_node(page_info_title,attr_dict={'url': page_info_url, 'title':
                        # page_info_title, 'id': page_info_id},color_node="pag" + str(subcategory_depth),size=float(
                        # subcategory_depth))
                        self.category_graph.add_node(page_info_title, type="pag", url=page_info_url)
                        self.category_graph.add_edge(new_parent_node, page_info_title, type='page')
                        print(" " * (MAX_DEPHT - ((subcategory_depth - 1) * 2)) + "Page: " + page_info_title + " URL: " + page_info_url)

        # =======Adding and exploring the subcategories===
        if subcategory_depth > 0:

            search_params_subcat = {
                'list': 'categorymembers',
                'cmtype': 'subcat',
                'cmprop': 'ids|title',
                'cmlimit': 500,
                'cmtitle': title}

            subcat_results = _wiki_request(search_params_subcat)['query']['categorymembers']

            for subcat_result in subcat_results:
                self.search_and_store_graph(subcat_result['title'], subcategory_depth - 1, new_parent_node, include_pages)
