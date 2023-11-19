import requests
import os
from dotenv import load_dotenv

load_dotenv()

YOU_HEADERS = {"X-API-Key": os.environ.get("YOUCOM_API_KEY", "")}

def _get_you_search_impl(
    query: str, page_index: int = 0, limit: int = 20, country: str = ""
):
    url = "https://api.ydc-index.io/search"

    query_args = {"query": query}
    if page_index:
        query_args["offset"] = page_index
    if limit:
        query_args["count"] = limit
    if country:
        query_args["country"] = country

    response = requests.request("GET", url, headers=YOU_HEADERS, params=query_args)

    results = []
    for line in response.json()["hits"]:
        snippets = " ".join(line["snippets"])
        description = ". ".join([line["title"], snippets])
        results.append(
            {
                "url": line["url"],
                "title": line["title"],
                "text": description,
            }
        )
    return results


def _get_you_news_impl(
    query: str, page_index: int = 0, limit: int = 20, country: str = ""
):
    url = "https://api.ydc-index.io/news"
    query_args = {"q": query}
    if page_index:
        query_args["offset"] = page_index
    if limit:
        query_args["count"] = limit
    if country:
        query_args["country"] = country

    response = requests.request("GET", url, headers=YOU_HEADERS, params=query_args)
    results = []
    for line in response.json()["news"]["results"]:
        results.append(
            {"url": line["url"], "title": line["title"], "text": line["description"]}
        )
    return results


def get_you_search(query: str):
    # TODO: pass the page here somehow
    return _get_you_search_impl(query, page_index=0, country="")


def get_you_news(query: str):
    # TODO: pass the page here somehow
    results = []
    for _ in range(3):
        results.extend(_get_you_news_impl(query, page_index=0, country=""))
    return results


def _get_newsapi_impl(
    query: str, page_index: int = 0, limit: int = 20
):
    url = "https://newsapi.org/v2/everything"
    query_args = {
        "q": query,
        "apiKey": os.environ.get("NEWSAPI_API_KEY")
    }
    if page_index:
        query_args["page"] = page_index+1
    if limit:
        query_args["pageSize"] = limit

    response = requests.request("GET", url, params=query_args)
    results = []
    for line in response.json()["articles"]:
        results.append(
            {"url": line["url"], "title": line["title"], "text": line["description"] + " " + line["content"]}
        )
    return results


def get_newsapi_news(query: str):
    results = []
    for _ in range(3):
        results.extend(_get_newsapi_impl(query, page_index=0))
    return results


SOURCES = {
    "you_news": get_you_news,
    "you_search":  get_you_search,
    "news_api": get_newsapi_news,
}


def get_data(query: str):
    results = []
    for source, get_func in SOURCES.items():
        results.append(get_func(query))
    return results


if __name__ == '__main__':
    print(get_data("Xi Jinping in San Francisco"))
