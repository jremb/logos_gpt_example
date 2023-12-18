import win32com.client
import time
import json

class LogosApplication:
    def __init__(self):
        self.launcher = win32com.client.Dispatch("LogosBibleSoftware.Launcher")
        self.launcher.LaunchApplication()
        while self.launcher.Application is None:
            time.sleep(1)  # Wait for the application to launch
        self.application = self.launcher.Application

    def search_logos_library(self, query: str):
        """
        Searches the LogosApplication library for a given query and returns a list of search results.

        Args:
            query (str): The search term to query in the LogosApplication library.

        Returns:
            LogosResourceInfo objects which have the following properties:
                - ResourceId
                - Version
                - Title
                - AbbreviatedTitle*
                - ResourceType
            
            * Not all objects will have the AbbreviatedTitle property.
        """
        return self.application.Library.GetResourcesMatchingQuery(query)
    
    def get_bible_passage(self, passage: str) -> str|None:
        """
        Returns the text of a Bible passage as a string. If the passage is not found, returns None.

        Args:
            passage (str): The Bible passage to retrieve. Can be more than a single verse: e.g., "John 3:16-17".

        Returns:
            str|None: The text of the Bible passage as a string. If the passage is not found, returns None.
        """
        data_types = self.application.DataTypes
        bible = data_types.GetDataType("Bible")
        references = bible.ScanForReferences(passage)
        try:
            ref = references[0]
            copy_bible_verses = self.application.CopyBibleVerses
            copy_req = copy_bible_verses.CreateRequest()
            copy_req.Reference = ref.Reference
            return copy_bible_verses.GetText(copy_req)
        except IndexError as e:
            print(f"[ERROR]: could not find reference matching '{passage}'")
            return None
    
def search_logos_library(query: str) -> str:
    """
    Searches the LogosApplication library for a given query and returns a JSON string of the search results.
    Each result is a dictionary with the title of the result.

    Args:
        query (str): The search term to query in the LogosApplication library.

    Returns:
        str: A JSON string of a list of dictionaries. Each dictionary contains the title of a search result.
    """
    logos = LogosApplication()
    results = logos.search_logos_library(query)
    result_list = []

    for result in results:
        result_dict = {
            "title": result.Title,
            "resource_id": result.ResourceId,
            "version": result.Version,
            "resource_type": result.ResourceType,
            "abbreviated_title": result.AbbreviatedTitle if hasattr(result, "AbbreviatedTitle") else "",
        }
        result_list.append(result_dict)

    return json.dumps(result_list, ensure_ascii=False)

def get_bible_passage(passage: str) -> str:
    """
    Returns the text of a Bible passage as a string. If the passage is not found, returns None.

    Args:
        passage (str): The Bible passage to retrieve. Can be more than a single verse: e.g., "John 3:16-17".

    Returns:
        str|None: The text of the Bible passage as a string. If the passage is not found, returns None.
    """
    logos = LogosApplication()
    return logos.get_bible_passage(passage)
