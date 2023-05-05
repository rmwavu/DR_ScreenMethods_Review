from serpapi import GoogleSearch

from scrapUtilities import ReportWriter

import json

def listStringMerger(dataList):
		"""
		Generates a string list out of the provided data
		"""
		generated_string = ""

		if len(dataList) > 0:
			# create string out of the data
			for track_index, data_item_name in enumerate(dataList):
				if track_index == 0:
					generated_string = generated_string + data_item_name

				else:
					generated_string = generated_string + ", " + data_item_name

		else:
			pass


		return generated_string


def extractRequiredInfor(dataObject):
    """
    Extracts the necessary information out of the page
    """
    title = dataObject['title']

    article_link = dataObject['link']

    abstract = dataObject['snippet'].encode('ascii', 'ignore').decode()

    publication_data = dataObject['publication_info']

    if 'authors' in publication_data:
        # get the authors
        author_data = publication_data ['authors']

        # create authors list
        authors_list = [each_author_object['name'] for each_author_object in author_data]

        # get author name list string
        author_string = listStringMerger(authors_list)

    else:
        author_string = 'Missing'

    # create data object
    scrapped_data_object = {
        'article title': title,
        'article link': article_link,
        'article abstract': abstract,
        'article authors': author_string

    }

    return scrapped_data_object


# declare data search fields
data_search_fields = [i for i in range(0, 301, 10)]

# store the attained data
data_attained = []

search_queries = ['machine learning', 'deep learning', 'artificial intelligence']

# select a search query
selected_query = search_queries[2]

print("Connecting to the Internet....\n")

for each_data_field in data_search_fields:
    print("Fetching ....{}\n".format(each_data_field))

    # add that to the query
    formulated_query = "{} and diabetic retinopathy".format(selected_query)

    # set the parameters
    params = {
        "q": formulated_query,
        'engine': 'google_scholar',
        'as_ylo': '2009',
        'as_yhi': '2023',
        'num': '20',
        'start': ''.format(each_data_field),
        "api_key": "fb65166cb165f560300c4326a92ef0b423ac3eee4e0f721b8267f38ce3c311ed"
        }

    # create a search instance
    search = GoogleSearch(params)

    # make the search
    search_details_size = search.get_dict()["search_information"]['total_results']

    # print("Found:", type(search_details))

    if search_details_size > 0:
        # get the results
        data_results = search.get_dict()["organic_results"]

        for each_data_object in data_results:
            # extract and filter the data
            composed_data_object = extractRequiredInfor(each_data_object)

            # store the data attained
            data_attained.append(composed_data_object)

        print("\nDone Fetching....{}".format(each_data_field))

    else:
        print("\nThere was no data for...{}".format(each_data_field))


if len(data_attained) > 0:
    ReportWriter().writeReport({
        'key': 'Google-scholar - {}'.format(formulated_query),
        'count': len(data_attained),
        'data': data_attained,

    })

else:
    pass

print("Done with the job...!")