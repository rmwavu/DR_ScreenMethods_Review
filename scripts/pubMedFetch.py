from pymed import PubMed

import json

import pydoi


class PubMedCore:
	"""
	Will manage data feteching from the pub med site
	"""

	def listStringMerger(self, dataList):
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

	def generateFullDocumentLink(self, doiValue):
		"""
		Generates the full link to the document based on the document
		object identifier
		"""

		generated_url = "Missing"

		link_fetch_status = False

		try:
			# get the url
			generated_url = pydoi.get_url(doiValue)

			link_fetch_status = True

		except:
			# alert missing
			pass


		return link_fetch_status, generated_url

	def generateAuthorNameList(self, authorObjects):
		"""
		Generate the list of the authors
		"""
		# collect the author names
		author_names = []

		for author_detail_object in authorObjects:
			# get the first name and last name
			author_first_name = author_detail_object['firstname']

			author_last_name = author_detail_object['lastname']

			# generate the full name
			author_full_name = "{} {}".format(author_first_name, author_last_name)

			# store the name
			author_names.append(author_full_name)


		# get the string list
		author_name_string = self.listStringMerger(author_names)

		return author_name_string



	def convertJsonStringToDataDictionary(self, jsonData):
		"""
		Converts json data into a dictionary
		"""

		# punch the data 
		punched_data = """{}""".format(jsonData)

		# convert the data
		converted_data = json.loads(punched_data)

		return converted_data

	
	def generateDoiValue(self, doiData):
		"""
		Generates the doi value
		Note: Its possible having more than one doi
		"""

		# check if the doi is none
		is_doi_valid = doiData is not None

		if is_doi_valid is True:

			# check if they are many doi's
			are_they_many = "\n" in doiData

			if are_they_many is True:
				# take the first split them
				split_data = doiData.split("\n")

				# string them
				doi_string = self.listStringMerger(split_data)

				first_doi_value = split_data[0]

			else:
				# return the provided
				doi_string = doiData

				first_doi_value = doi_string

		else:
			doi_string = 'Missing'

			first_doi_value = 'Missing'

		return is_doi_valid, doi_string, first_doi_value
			

		

	def parseAndextractKeyInfo(self, pubMedDataObject):
		"""
		Extracts and creates a relevant information object

		Returns a formatted pubmed object in the format
				journal name,
				journal title,
				publication date,
				document authors,
				full article link,
				pubmed lin,
				document object id,
				abstract
		"""

		# get the formatted data
		formatted_data = self.convertJsonStringToDataDictionary(pubMedDataObject)

		# abstract, authors, doi, full-article-link, publication-date, 
		# pubmed-link, journal-name, journal-title

		document_abstract = formatted_data['abstract']

		# get the names
		authors_object = formatted_data['authors']

		# string the names
		author_name_list = self.generateAuthorNameList(authors_object)

		# get the doi
		doi_data = formatted_data['doi']

		# get the doi value and a reference value to be used in full link generation
		doi_status, doi_value, reference_doi_value = self.generateDoiValue(doi_data)

		if doi_status is True:
			# full article link
			resolve_status, full_link = self.generateFullDocumentLink(reference_doi_value)

			if resolve_status is False:
				# alert missing link
				full_link = "Missing"

			else:
				pass

		else:
			full_link = "Missing"

		# publication date
		publication_date = formatted_data['publication_date']

		# get the ids
		id_object = formatted_data['pubmed_id']

		pubmed_id = id_object if "\n" not in id_object else id_object.split()[0]

		# pubmed - link
		pubmed_link = 'https://pubmed.ncbi.nlm.nih.gov/{}/'.format(pubmed_id)

		# get the journal name
		journal_name = formatted_data['journal'] if 'journal' in formatted_data else "Missing"

		# get the journal name
		journal_title = formatted_data['title'] if 'title' in formatted_data else "Missing"

		# create pubmed data object
		pubmed_data_object = {
			'journal name': journal_name,
			'journal title': journal_title,
			'publication date': publication_date,
			'document authors': author_name_list,
			'full article link': full_link,
			'pubmed link': pubmed_link,
			'document object identifier (doi)': doi_value,
			'abstract': document_abstract
		}


		return pubmed_data_object






	def searchPubMed(self, whatToFetch, howManyResults=20):
		"""
		Performs a simple query for the data

		Note: Default number of results returned is 20
		"""

		# store the results
		collected_pubmed_results = []

		# track those that failed
		failed_objects = 0

		# create instance
		pubmed_instance =  PubMed()

		# get the results
		results = pubmed_instance.query(whatToFetch, max_results=howManyResults)

		# print("Fetched Total:", len(results))

		for article in results:

			# view the article type
			# print(article)

			raw_data = article.toJSON()

			# get relevant information out of the object
			prepared_pubmed_object = self.parseAndextractKeyInfo(raw_data)

			if prepared_pubmed_object is None:
				# track
				failed_objects = failed_objects + 1

			else:
				# store the data
				collected_pubmed_results.append(prepared_pubmed_object)


		# debug point
		print("\nParsed Total:", len(collected_pubmed_results))

		print("\nFailed Total:", failed_objects)

		return collected_pubmed_results



# make a search
# data = PubMedTools().searchPubMed('machine learning and diabetic retinopathy', 2)


# print(data)









