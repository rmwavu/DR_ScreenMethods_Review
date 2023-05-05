from scrapUtilities import ScienceDirectUtilities, ReportWriter, PubMedUtilities


def displayTexts(displayTag, extraInfo=None):
    """
    Simple Display messages
    1- connecting, fetch status, done
    """
    if displayTag == 1:
        print("Trying to connect to the Internet...\n")

    elif displayTag == 2:
        print("Fetch Status:", extraInfo, "\n")

    else:
        print("Done!\n")


    return



def pubMedTools(searchWord, resultLimit):
    """
    Conducts a fetch, filter of pubmed data
    """
    displayTexts(1)

    # get data from the internet
    get_status, data_detail = PubMedUtilities().searchPubMeb(searchWord, resultLimit)

    displayTexts(2, get_status)

    if get_status is True:
        # check if there is something to write
        is_there_anything_to_write = len(data_detail) > 0

        if is_there_anything_to_write is True:
            # create a report object
            report_object = {
                'key': searchWord,
                'data': data_detail,
                'count': resultLimit
            }

            # save the data
            ReportWriter().writeReport(report_object)

        else:
            # ignore creating the report
            pass

    else:
        pass

    displayTexts(3)


def scienceDirectTools(searchWord):
    """
    Conducts the fetch of the data, extraction and save of the data
    """
    displayTexts(1)

    # get data from the internet
    get_status, data_detail = ScienceDirectUtilities().fetchDataSet(searchWord)

    # print(ScienceDirectUtilities().prettifyDataBundle(data_detail))

    displayTexts(2, get_status)

    if get_status is True:
        # extract the required data
        extracted_data = ScienceDirectUtilities().parseAndFilterSearchResults(data_detail)

        # check if there is something to write
        is_there_anything_to_write = len(extracted_data['data']) > 0

        if is_there_anything_to_write is True:
            # save the data
            ReportWriter().writeReport(extracted_data)

        else:
            # ignore creating the report
            pass

    else:
        pass

    displayTexts(3)

    return