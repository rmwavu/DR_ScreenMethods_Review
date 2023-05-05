import arcas, requests

from pubMedFetch import PubMedCore

from scrapUtilities import ReportWriter

class PlosTools:
    """
    Contains scripts to get and format plos data
    """

    def __init__(self):
        pass



    def extractReleventContentPlos(self, dataObject):
        """
        Extracts relevant data out of the object provided
        """
        # title
        article_title = dataObject['title_display']

        # doi
        doi_value = dataObject['id']

        # get the article link
        link_generation_status, gotten_link = PubMedCore().generateFullDocumentLink(doi_value)

        # craft link
        article_link = gotten_link if link_generation_status is True else 'Missing'

        # article ratings
        article_ratings = dataObject['score']

        # journal
        in_what_journal = dataObject['journal']

        # document raw date
        raw_date = dataObject['publication_date']

        # publication date
        publication_date = raw_date[:raw_date.find("T")]

        # authors
        author_names = dataObject['author_display']

        # generate author name list
        author_name_list = PubMedCore().listStringMerger(author_names)

        # article abstract
        article_abstract = dataObject['abstract'][0].strip()


        generated_object = {
            'title': article_title,
            'article doi': doi_value,
            'link': article_link,
            'rating': article_ratings,
            'journal': in_what_journal,
            'publication date': publication_date,
            'authors': author_name_list,
            'abstract': article_abstract
            }

        return generated_object

    def parseAndExtractDataObjects(self, dataBundle):
        """
        Generates or exhausts all data objects that can be gotten
        """
        found_data_objects = []

        for each_object in dataBundle:
            # get the relevant data
            relevant_data = self.extractReleventContentPlos(each_object)

            # store the object that results
            found_data_objects.append(relevant_data)

        
        return found_data_objects

    
    def generatePlosQueryUrl(self, searchWord, whereToStart, recordsCount, fetchYear, categoryIndex=0):
        """
        Generates a query url that will be used to fetch data records
        """
        # create api instance
        plos_api = arcas.Plos()

        # default category
        main_categories = ['machine learning', 'artificial intelligence', 'deep learning']

        # attain the category
        derived_category = main_categories[categoryIndex]

        # define parameters for the query
        if fetchYear is None:
            parameters = plos_api.parameters_fix(title='{}'.format(searchWord), start=whereToStart, records=recordsCount, category=derived_category)
        
        else:
            parameters = plos_api.parameters_fix(title='{}'.format(searchWord), start=whereToStart, records=recordsCount, year=fetchYear, category=derived_category)

        # get the url
        derived_url = plos_api.create_url_search(parameters)

        return derived_url


    def fetchRemoteResource(self, fetchUrl):
        """
        Fetch the data from the remote resource
        """

        # declare default responses
        fetch_status = False

        fetched_data = None

        # create headers
        fetch_headers = {
            'Accept': 'application/json'
        }

        try:
            # test out the api
            response = requests.get(fetchUrl, headers=fetch_headers)

            # check the status of the query
            fetch_status = response.status_code == 200

            if fetch_status is True:
                # get the data
                fetched_data = response.json()

            else:
                pass
        except:
            pass

        return fetch_status, fetched_data

    def executePlosQuery(self, searchKey):
        """
        Parse plos to attain any data related to a given keyword
        """
        # collect the resultant objects
        result_objects_pool = []

        # generate years to be used
        years_to_be_used = [i for i in range(2009, 2024)]
    
        # check for every year
        for each_year in years_to_be_used:
            # get the url
            resource_url = PlosTools().generatePlosQueryUrl(searchKey, 0, 50, each_year, keyword_index)

            print("Generated url for {}:".format(each_year), resource_url)

            # get the data
            data_get_status, data_ = PlosTools().fetchRemoteResource(resource_url)

            print("Data Fetch Status:{}".format(data_get_status))

            if data_get_status is True:
                # acces the records
                response_data = data_['response']

                # get the articles
                articles = response_data['docs']

                # check if there are articles
                are_there_articles = len(articles) > 0

                if are_there_articles is True:
                    # get the data objects found
                    data_objects_found = self.parseAndExtractDataObjects(articles)

                    # merge the results
                    for each_resultant_object in data_objects_found:
                        # store the object
                        result_objects_pool.append(each_resultant_object)

                    print("Articles discovered in {}:".format(each_year), len(data_objects_found))

                else:
                    # alert
                   print("Articles discovered in {}: 0".format(each_year))

            else:
                pass

        # size of results
        result_size = len(result_objects_pool)

        # size status
        is_result_available = result_size > 0

        # status, data
        print("Total number of articles found for {} are {}".format(searchKey, result_size))

        return is_result_available, result_objects_pool


    def manageReports(self, dataItems, keyTerm, termTag):
        """
        Responsible for generating reports
        """
        # map keys to the full query
        key_term_map = {
            0: 'machine learning',
            1: 'artificial intelligence',
            2: 'deep learning'
        }
        # full query
        full_query_name = "{} and {}".format(key_term_map[termTag], keyTerm)

        ReportWriter().writeReport({
        'key': 'plos-{}'.format(full_query_name),
        'count': len(dataItems),
        'data': dataItems,
        })

        return




# define search parameters
search_query = 'diabetic retinopathy'


for keyword_index in range(3):

    # get the data
    get_status, associated_data = PlosTools().executePlosQuery(search_query)

    # debug point
    print(associated_data)

    if get_status is True:
        # create a report of the data
        PlosTools().manageReports(associated_data, search_query, keyword_index)

        print("Done writing the report.... for {}".format(keyword_index))

    else:
        pass
    