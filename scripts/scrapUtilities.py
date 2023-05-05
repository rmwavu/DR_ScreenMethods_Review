import requests

import json

import pyexcel

import os

from pubMedFetch import PubMedCore


class PubMedUtilities:
	def __init__(self):
		pass

	def pubmedDataRetreiver(self, searchValue, volumeValue):
		"""
		Conducts the actual retreival of the data
		"""

		# set the fetch status
		# fetch_status = False

		try:
			# get the data
			found_data = PubMedCore().searchPubMed(searchValue, volumeValue)

			fetch_status = True

		except:
			# alert error
			found_data = None

			fetch_status = False
		
		return fetch_status, found_data


	def searchPubMeb(self, whatToSearch, resultVolume=20):
		"""
		Search pubmeb for the provided key
		Note: Default volume is 20 results, but you can change it
		"""
		
		# make the search
		fetch_validity, search_results  = self.pubmedDataRetreiver(whatToSearch, resultVolume)

		
		return fetch_validity, search_results





class ReportWriter:
	"""
	Writes the found records into an excel file
	"""
	def __init__(self):
		# create path to the desktop
		self.desktop_path = os.path.join(os.path.expanduser('~'), "Desktop\\ScrapReports")

		if os.path.exists(self.desktop_path):
			pass

		else:
			# create the folder
			os.mkdir(self.desktop_path)


	def writeReport(self, reportFeedData):
		"""
		Generates a report name out of the data
		"""

		report_name = "{} - {}.xlsx".format(reportFeedData['key'].lower(), reportFeedData['count'])

		# generate absolute path
		absolute_path = os.path.join(self.desktop_path, report_name)

		# get the data
		report_data = reportFeedData['data']

		# write the data
		pyexcel.save_as(records=report_data, dest_file_name=absolute_path)

		return

class ScienceDirectUtilities:
	"""
	Author: Grace Peter Mutiibwa

	This module provides access to the science direct resource based on a search query
	"""
	def __init__(self):
		pass



	def generateAuthorList(self, authorObjects):
		"""
		Generates a string of the authors names
		"""
		# check the type
		is_bundle_list = isinstance(authorObjects, list)

		# print('found:', authorObjects)

		if is_bundle_list is True:

			# get the names from the object
			extracted_author_names = [list(each_author_object.values())[0] for each_author_object in authorObjects]

			# store the names as a string
			author_list_string = ""

			for track_index, author_name in enumerate(extracted_author_names):
				if track_index == 0:
					author_list_string = author_list_string + author_name

				else:
					author_list_string = author_list_string + ", " + author_name

		else:
			# its just a name
			author_list_string = authorObjects


		return author_list_string



	def extractAndCleanResultData(self, dataObjects):
		"""
		Wille parse all data items and extract the needed information

		returns: a list of extracted data objects that will be feed values for data templates
		"""

		# collect parsed data
		parsed_filtered_data = []

		for each_data_record in dataObjects:
			# extract out the necessary details
			article_url = each_data_record["link"][1]["@href"]

			# document title
			document_title = each_data_record["dc:title"]

			# publication name
			publication_name = each_data_record["prism:publicationName"]

			# volume of the document
			document_volume = each_data_record["prism:volume"] if "prism:volume" in each_data_record else "Not Sepcified"


			publication_date = each_data_record["prism:coverDate"]
			
			# access
			is_free_to_acess = each_data_record["openaccess"]

			# list of authors
			author_list = self.generateAuthorList(each_data_record["authors"]["author"])

			# create a document detail
			# link, title, name, volume, access-status, authors
			document_detail = {
				'link': article_url,
				'title': document_title,
				'name': publication_name,
				'volume': document_volume,
				'access': is_free_to_acess,
				'authors': author_list,
				'publication date': publication_date
			}

			# store detail
			parsed_filtered_data.append(document_detail)


		return parsed_filtered_data



	def parseAndFilterSearchResults(self, referenceSearchResults):
		"""
		Goes through the search results and extracts the necessary information
		"""

		# get the results number
		total_results_count = int(referenceSearchResults["opensearch:totalResults"])

		# search terms
		search_terms_used = referenceSearchResults["opensearch:Query"]["@searchTerms"]

		# get the data items
		needed_data_items = referenceSearchResults["entry"]

		# parse the data items and attain the necessary data
		feed_data_objects = self.extractAndCleanResultData(needed_data_items)


		# draft sessin report
		session_report = {
			'count': total_results_count,
			'key': search_terms_used,
			'data': feed_data_objects
			}


		return session_report



	def generateAccessUrl(self, searchData):
		"""
		Generates an access url based on the search data
		"""
		# prepare access details
		api_key = "7f59af901d2d86f78a1fd60c1bf9426a"

		# prepare an access url for the resource
		derived_access_url = "https://api.elsevier.com/content/search/sciencedirect?query={}&apiKey={}".format(searchData, api_key)

		return derived_access_url



	def fetchRemoteResource(self, fetchUrl):
		"""
		Grabs the resource from the provided url
		"""
		# create request headers
		headers = {
		    'Accept': 'application/json'
		    }


		# default fetch status and result initialization
		access_status = False

		search_results = None


		try:
			# access the data
			api_response = requests.get(fetchUrl, headers=headers)

			# get the status code
			api_status_code = api_response.status_code

			# initialize the access status, data list and the store
			access_status = True if api_status_code == 200 else False

			# validate fetch session
			if access_status is True :
				# get data as json: dictionary
				data_content = api_response.json()

			    # access search results: 'search-results' as key for the dictionary above
				search_results = data_content['search-results']
				
			else:
				pass

		except:
			pass


		return access_status, search_results


	def prettifyDataBundle(self, dataBundle):
		"""
		Formats the dictionary data using an indent level of 2
		"""
		# get the pretty version
		pretty_version = json.dumps(dataBundle, indent=2)

		return pretty_version


	def fetchDataSet(self, searchKeyWord):
		"""
		Attains search results from science direct based on the search key provided

		Returns: 
				fetch_status(Boolean) - True (valid fetch), False (Invalid Fetch)
				data_list  (Boolean) - True (If there is content), False - If there is no content
				-> data_store (List of Dicts) - Contains the Filtered Information

		Note: 
			If the fetch_status is False it means access was invalid
			If data_list is False, it means the data store is empty
		"""

		# get the access url
		generated_url = self.generateAccessUrl(searchKeyWord)

		# get the data
		fetch_status, data_bundle =  self.fetchRemoteResource(generated_url)

		return fetch_status, data_bundle





