import requests
from bs4 import BeautifulSoup

university_search_url = "https://www.wlv.ac.uk/search/?collection=meta&query="


def search_uni_website(search_term):
    r = requests.get(university_search_url + search_term)
    page = BeautifulSoup(r.text, "html.parser")

    search_results = page.find_all("cite")

    links = []

    for result in search_results:
        if 'data-url' in result.attrs:
            links.append(result["data-url"])

    # Return a maximum of 3 links
    if len(links) > 2:
        return links[:3]

    return None
