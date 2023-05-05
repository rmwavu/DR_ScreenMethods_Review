import requests

from pubMedFetch import PubMedCore

from scrapUtilities import ReportWriter

def generateUrlText(queryText):
	"""
	Creates a formatted piece of the url
	"""

	# break the text down into a list of strings
	split_text = queryText.split()

	if len(split_text) == 1:
		return queryText

	else:
		pass

	# create search query
	created_query = ""

	for word_index, each_word in enumerate(split_text):
		if word_index == 0:
			# just append the word
			created_query = created_query + each_word

		else:

			# create the query
			created_query = created_query + "+" + each_word


	return created_query


def fetchRemoteResource(fetchUrl):
    """
    Fetch the data from the remote resource
    """

    # declare default responses
    fetch_status = False

    fetched_data = None

    try:
        # test out the api
        response = requests.get(fetchUrl)

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


def extractReleventContentPlos(dataObject):
    """
    Extracts relevant data out of the object provided
    """
    # title
    article_title = dataObject['title']

    # doi
    doi_value = dataObject['doi']

    # get the article link
    link_generation_status, gotten_link = PubMedCore().generateFullDocumentLink(doi_value)

    # craft link
    article_link = gotten_link if link_generation_status is True else 'Missing'

    # article ratings
    article_ranking = dataObject['rank']

    # journal
    in_what_journal = dataObject['publication_title']

    # document raw date
    publication_date = dataObject['publication_date']

    # authors
    author_name_objects = dataObject['authors']['authors']

    # get the author names
    author_names = [each_author_object['full_name'] for each_author_object in author_name_objects]

    # generate author name list
    author_name_list = PubMedCore().listStringMerger(author_names)

    # article abstract
    article_abstract = dataObject['abstract']


    generated_object = {
        'title': article_title,
        'article doi': doi_value,
        'link': article_link,
        'ranking': article_ranking,
        'Conference / Journal': in_what_journal,
        'publication date': publication_date,
        'authors': author_name_list,
        'abstract': article_abstract
        }

    return generated_object


def parseAndExtractDataObjects(dataBundle, queryString):
    """
    Generates or exhausts all data objects that can be gotten
    """
    found_data_objects = []

    for each_object in dataBundle:
        # get the relevant data
        relevant_data = extractReleventContentPlos(each_object)

        # store the object that results
        found_data_objects.append(relevant_data)

    # save the data
    manageReports(found_data_objects, queryString)

    return


def manageReports(articlesObject, queryName):
    """
    Responsible for generating reports
    """

    # full query
    full_query_name = "IEEE - {}".format(queryName)

    ReportWriter().writeReport({
    'key': full_query_name,
    'count': len(articlesObject),
    'data': articlesObject,
    })

    return



# create title
query_titles = {
    0: 'machine learning and diabetic retinopathy',
    1: 'deep learning and diabetic retinopathy',
    2: 'artificial intelligence and diabetic retinopathy'
} 

for _, each_query in query_titles.items():
    # search query
    search_query_feed = generateUrlText(each_query)

    # diabetic+retinopathy
    url_path = 'http://ieeexploreapi.ieee.org/api/v1/search/articles?apikey=wcy3urx34jrkr4d9pay6j467&format=json&max_records=25&start_record=45&sort_order=asc&sort_field=article_number&article_title={}&start_year=2009&end_year=2023'.format(search_query_feed)

    # print("Full path:", url_path)

    # fetch the data
    get_status, fetched_data = fetchRemoteResource(url_path)

    if get_status is True:
        # print(fetched_data)
        # extract the relevant information

        if not 'articles' in fetched_data:
            continue
        
        else:
            pass
        article_data = fetched_data["articles"]

        # size
        found_article_size = len(article_data)

        # debug
        print("Articles Found: {} for {}".format(found_article_size, each_query))

        # check how many articles have been found
        are_there_articles = found_article_size > 0

        if are_there_articles is True:
            # get the articles and then write them
            parseAndExtractDataObjects(article_data, each_query)

            print("Done wrting for {} .....\n".format(each_query))

        else:
            pass


    else:
        print("\nFailed....!")