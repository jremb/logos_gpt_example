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

    def search_logos_library(self, query):
        return self.application.Library.GetResourcesMatchingQuery(query)
    
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
        result_dict = {"title": result.Title}
        result_list.append(result_dict)

    return json.dumps(result_list, ensure_ascii=False)