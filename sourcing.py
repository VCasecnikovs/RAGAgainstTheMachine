import requests
import os

headers = {"X-API-Key": os.environ.get("YOU_API_KEY", "")}


def _get_you_search_impl(query: str, page_index: int = 0, limit: int = 20, country: str = ""):
    url = "https://api.ydc-index.io/search"

    query_args = {
        "query": query
    }
    if page_index:
        query_args["offset"] = page_index
    if limit:
        query_args["count"] = limit
    if country:
        query_args["country"] = country

    response = requests.request("GET", url, headers=headers, params=query_args)

    results = []
    for line in response.json()["hits"]:
        snippets = " ".join(line["snippets"])
        description = ". ".join([line["title"], snippets])
        results.append({
            "url": line["url"],
            "title": line["title"],
            "text": description,
        })
    return results


def _get_you_news_impl(query: str, page_index: int = 0, limit: int = 20, country: str = ""):
    url = "https://api.ydc-index.io/news"
    query_args = {
        "q": query
    }
    if page_index:
        query_args["offset"] = page_index
    if limit:
        query_args["count"] = limit
    if country:
        query_args["country"] = country

    response = requests.request("GET", url, headers=headers, params=query_args)
    results = []
    for line in response.json()["news"]["results"]:
        results.append({
            "url": line["url"],
            "title": line["title"],
            "text": line["description"]
        })
    return results


def get_you_search(query: str):
    # TODO: pass the page here somehow
    return _get_you_search_impl(query, page_index=0, country="")


def get_you_news(query: str):
    # TODO: pass the page here somehow
    return _get_you_news_impl(query, page_index=0, country="")


SOURCES = {
    "you_news": get_you_news,
    "you_search": get_you_search,
}


def get_data(query: str):
    results = []
    for source, get_func in SOURCES.items():
        results.append({
            "source": source,
            "results": get_func(query)
        })
    return results


print(get_data("Xi Jinping"))
