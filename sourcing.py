import requests
import os
from dotenv import load_dotenv

load_dotenv()


headers = {"X-API-Key": os.environ.get("YOUCOM_API_KEY", "")}

STATES = {
    "you_news": {
        "page_index": 0,
        "country": ""
    },
    "you_search": {
        "page_index": 0,
        "country": ""
    }
}


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

    response = requests.request("GET", url, headers=headers, params=query_args)

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
    STATES["you_search"] = {
        "page_index":  page_index,
        "country": country
    }
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

    response = requests.request("GET", url, headers=headers, params=query_args)
    results = []
    for line in response.json()["news"]["results"]:
        results.append(
            {"url": line["url"], "title": line["title"], "text": line["description"]}
        )
    STATES["you_news"] = {
        "page_index": page_index,
        "country": country
    }
    return results


def get_you_search(query: str):
    # TODO: pass the page here somehow
    return _get_you_search_impl(query, page_index=0, country="")


def get_you_news(query: str):
    # TODO: pass the page here somehow
    return _get_you_news_impl(query, page_index=0, country="")


def _you_next_state(you_state: dict) -> dict:
    new_state = you_state.copy()
    new_state["page_index"] = you_state["page_index"] + 1
    return new_state

###########################################################################
# Functions which iterate over the state (pagination, etc), e.g "GIVE MORE DATA"


def get_you_news_iter(query: str):
    state = _you_next_state(STATES["you_news"])
    return _get_you_news_impl(query, state["page_index"], state["country"])


def get_you_search_iter(query: str):
    state = _you_next_state(STATES["you_news"])
    return _get_you_search_impl(query, state["page_index"], state["country"])


SOURCES = {
    "you_news": get_you_news,
    "you_search":  get_you_search,
}


SOURCES_ITER = {
    "you_news": get_you_news_iter,
    "you_search":  get_you_search_iter,
}


def get_data(query: str):
    results = []
    for source, get_func in SOURCES.items():
        results.append({
            "source": source,
            "results": get_func(query)
        })
    return results


def get_data_iter(query: str):
    # "give me more data flow"
    results = []
    for source, get_func in SOURCES_ITER.items():
        results.append({"source": source, "results": get_func(query)})
    return results


if __name__ == '__main__':
    print(get_data_iter("Sam Altman"))
    # second time should have other set of articles
    print(get_data_iter("Sam Altman"))
