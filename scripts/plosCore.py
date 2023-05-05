from scrapUtilities import ReportWriter

from pubMedFetch import PubMedCore

from allofplos import Article

import os

from threading import Thread

class PlosUtilities:
	"""
	Provide the list of keywords to check against, a base keyword and the start year
	Note: all years before will be ignored
	"""

	def __init__(self, baseKeyWord, keyWordList, startYear):
		# get the path to the documents folder
		self.documents_folder_path = self.getDocumentsPath()

		# print("Found Path:", self.documents_folder_path)

		# base year
		self.base_year = startYear

		# base keyword
		self.base_key_word = baseKeyWord

		# initialize key words
		self.key_words_reference = [key_word.lower() for key_word in keyWordList]


	def determineIfBaseIsPresent(self, formattedTitle):
		"""
		Determine if the the keyword exists
		"""

		# split the key words
		split = self.base_key_word.split()

		# collect
		base_validity = []

		for each_base in split:
			# determine if its there
			presence_status = each_base in formattedTitle

			base_validity.append(presence_status)

		# check the count
		is_base_present = True in base_validity

		return is_base_present



	def determineIfKeyWordsExist(self, articleTitle):
		"""
		Determines if the article title contains the keywords provided
		"""

		# validity collector
		validity_pool = []

		for each_keyword in self.key_words_reference:
			# determine if it exists
			do_key_words_exist = self.determineIfBaseIsPresent(articleTitle) and (each_keyword in articleTitle)

			# store the result
			validity_pool.append(do_key_words_exist)


		# determine the validity status
		is_document_valid = True if True in validity_pool else False

		return is_document_valid


	def isArticleInRequiredCategory(self, fileName):
		"""
		Determine if the article is with in the required
		"""

		# initial
		article_validity = False

		try:
			# get the plos doi
			crafted_plos_doi = self.plosDoiCreator(fileName)

			# connect to the document
			article_instance = Article(crafted_plos_doi, self.documents_folder_path)

			# get the publication year and check if its within the range
			publication_date_validity = article_instance.pubdate.date().year >= self.base_year

			if publication_date_validity is True:
				# get the title
				article_title = article_instance.title.lower()

				# check if it contains the key words
				article_validity = self.determineIfKeyWordsExist(article_title)

			else:
				pass

		except:
			pass


		return article_validity

		



	def wipeArticleFile(self, articleName):
		"""
		Cleans the selected article file
		"""

		# get the full path
		article_to_wipe_path = self.createAbsolutePath(articleName)

		# delete the file
		os.remove(article_to_wipe_path)

		return


	def generateSliceRanges(self, articleTotal):
		"""
		Generates slice ranges that will be used by threads
		"""
		# generate bounds
		generated_bounds = [i for i in range(0, articleTotal+1, 10000)]

		# track previous index
		previous_index = 0

		# collect slices
		slice_collector = []

		for index, item in enumerate(generated_bounds):
		      if index == 0:
		            # 0, 100000
		            slice_range = (0, generated_bounds[index+1])

		      elif index == len(generated_bounds)-1:
		            # 10000, 
		            slice_range = (generated_bounds[index]+1, articleTotal)

		      else:
		          # get the slice range
		          slice_range = (generated_bounds[previous_index+1]+1, generated_bounds[index+1])


		      # store the slice
		      slice_collector.append(slice_range)


		      # set the current index as the previous
		      previous_index = index

		return slice_collector



	def fileCleanser(self, fileList, wipedCount, validFiles, dismissedFiles):
		"""
		Cleans the files and removes any un wanted files
		"""
		for each_document_name in fileList:

			# convert the name to lower case
			lower_case_name = each_document_name.lower()



			# check if its a correction file
			is_it_correction_file = 'correction' in lower_case_name

			if is_it_correction_file is True:
				# get rid of the file
				self.wipeArticleFile(each_document_name)

				# track
				wipedCount = wipedCount + 1

				print("File:{} - Deleted".format(each_document_name))

			else:
				# check if the file is within the desired category
				is_file_in_category = self.isArticleInRequiredCategory(each_document_name)

				if is_file_in_category is True:
					# track valid
					validFiles = validFiles + 1

					print("File:{} - Valid".format(each_document_name))

				else:
					# get rid of the file
					self.wipeArticleFile(each_document_name)

					# track dismissed
					dismissedFiles = dismissedFiles + 1

					print("File:{} - UnWanted".format(each_document_name))

			print("{} Match the Keywords, {} are Invalid and {} are Corrupt!".format(
			validFiles,
			dismissedFiles,
			wipedCount)
			)
		return



	def threadLoadManager(self, sliceObjects, fileData, wipedCount, validFiles, dismissedFiles):
		"""
		Create threads to manage the load
		"""

		# store the threads
		thread_pool = []

		for each_slice_object in sliceObjects:
			# get the data
			sliced_data = fileData[each_slice_object[0]:each_slice_object[1]]

			# create a thread
			worker_thread = Thread(target=self.fileCleanser, args=[sliced_data, wipedCount, validFiles, dismissedFiles])

			# start the thread
			worker_thread.start()

			# collect the threads
			thread_pool.append(worker_thread)


		for each_thread in thread_pool:
			# join them
			each_thread.join()


		return






	def cleanArticleFiles(self):
		"""
		Cleans the article files removing all those that are related to correction
		"""
		# track the wiped documents
		wiped_count = 0

		# track dismissed
		dismissed_files = 0

		# track valid
		valid_files = 0


		print("Parsing the Document Folder...\n")

		# get all the documents
		document_names_list = self.getAllPresentDocuments()[::-1]

		# get the total count
		total_count = len(document_names_list)

		print("Found : {} Articles \n".format(total_count))

		maximum_thread_number = total_count//1000

		# is it greater
		is_thread_count_larger = maximum_thread_number > 20

		if is_thread_count_larger is True:
			# get the slice objects
			slice_objects = self.generateSliceRanges(total_count)

			# create threads to manage the load
			self.threadLoadManager(slice_objects, document_names_list, wiped_count, valid_files, dismissed_files)

		else:
			# go a head and manage the load
			self.fileCleanser(document_names_list, wiped_count, valid_files, dismissed_files)


		return


	def createAbsolutePath(self, headerPath):
		"""
		Generates an absolute path using the header path
		"""

		# merge the paths
		derived_absolute_path = os.path.join(self.documents_folder_path, headerPath)

		return derived_absolute_path


	def getDocumentsPath(self):
		"""
		Get the path to the article xml folder
		"""
		# get the base path
		documents_base_path = os.path.abspath(".")

		# check path
		documents_root = "pool"

		# get the full path
		absolute_path = os.path.join(documents_base_path, documents_root)

		return absolute_path


	def getAllPresentDocuments(self):
		"""
		Retrieves all document names that are found in the all of plos folder
		"""
		# get all available documents
		document_header_names = os.listdir(self.documents_folder_path)

		return document_header_names


	def plosDoiCreator(self, fileName):
		"""
		Generates a plos doi given the file name
		"""
		# get the article header name like 
		# 'journal.pbio.0000002' from journal.pbio.0000002.xml
		actual_document_doi_header = fileName[0:fileName.rfind(".")]

		# format the doi
		generated_doi = "10.1371/{}".format(actual_document_doi_header)

		return generated_doi


	def determineDoiValidity(self, fileName):
		"""
		Determines if the doi header is a valid one and returns the status of the check
		and the url if gotten
		"""

		# formulate the plos doi for the document
		derived_plos_doi = self.plosDoiCreator(fileName)

		# get the status and the url found
		fetch_status, generated_url = PubMedCore().generateFullDocumentLink(derived_plos_doi)

		return fetch_status, generated_url





def plosFetch():
	# declare plos document name header
	document_name_header = 'journal.pbio.0000002'

	# get the status and url
	status_, url_ = PlosUtilities().determineDoiValidity(document_name_header)

	print("{}:{}".format(status_, url_))

# create keyword list
key_word_pool = ['machine learning', 'artificial intelligence', 'deep learning']

# base keyword
base_key_word = 'diabetic retinopathy'


# clean the plos file
PlosUtilities(base_key_word, key_word_pool, 2008).cleanArticleFiles()


