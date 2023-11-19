import requests
import os
from dotenv import load_dotenv
from newspaper import Article
from chatting import chat_inference, ChatMessage, get_openAI_client, Role
import json

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
    for _ in range(1):
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
    for _ in range(1):
        results.extend(_get_newsapi_impl(query, page_index=0))
    return results


SOURCES = {
    "you_news": get_you_news,
    # "you_search":  get_you_search,
    # "news_api": get_newsapi_news,
}


def get_page_text(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception:
        return ""


def scrape_data(articles_data: list[dict]):
    for article in articles_data:
        parsed_text = get_page_text(article["url"])
        if parsed_text:
            article["text"] = article["text"] + " ." + parsed_text


def filter_urls(urls):
    client = get_openAI_client()

    with open('news_sources.json', 'r') as file:
        data = json.load(file)

    json_string = json.dumps(data[0], indent=4)

    messages_list = [
        ChatMessage(
            role=Role.SYSTEM,
            content=f"""User will send you list of URLs. Based on your knowledge and the "categories" below, assign URLs to the listed categories:

            Categories: {json_string}

            Return JSON format:
            "sources": {{
                "left": [<items>],
                "lean left": [<items>],
                "center": [<items>],
                "lean right": [<items>],
                "right": [<items>],
                "any": [<items>]
            }}

            Don't miss elements of URLs list. Assign to "any" if no better option
            """
        ),
        ChatMessage(role=Role.USER, content=f"""URLs: {urls}"""),
    ]

    assistant_answer = chat_inference(
        client=client,
        messages=messages_list
    )
    try:
        parsed_json = json.loads(assistant_answer)
    except json.JSONDecodeError as e:
        parsed_json = {"sources": {"any": urls}}
    results = []
    for key, value in parsed_json["sources"].items():
        results.extend(value[:10])
    return results


def get_data(query: str):
    results = []
    for source, get_func in SOURCES.items():
        results.extend(get_func(query))
    urls = [r["url"] for r in results]
    urls_filtered = set(filter_urls(urls))
    results_filtered = [r for r in results if r["url"] in urls_filtered]
    scrape_data(results_filtered)
    return results_filtered


if __name__ == '__main__':
    print(get_data("Xi Jinping in San Francisco"))
