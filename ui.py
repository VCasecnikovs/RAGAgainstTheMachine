import gradio as gr


from chatting import ChatMessage, chat_inference, get_openAI_client, Role

from sourcing import get_data


from pydantic import BaseModel


class Statement(BaseModel):
    statement: str
    urls: list[str]


def format_urls(urls: list[str]) -> str:
    formatted_urls = ""
    for i, url in enumerate(urls, start=1):
        formatted_urls += f"({i})[{url}] "
    return formatted_urls


class ArticleComparison(BaseModel):
    commonalities: list[Statement]
    divergencies: list[Statement]
    contradictions: list[Statement]

    def __str__(self):
        commonalities = "\n".join(
            [f"🔵 {c.statement} - {format_urls(c.urls)}\n" for c in self.commonalities]
        )
        divergencies = "\n".join(
            [f"🟠 {d.statement} - {format_urls(d.urls)}\n" for d in self.divergencies]
        )
        contradictions = "\n".join(
            [f"🔴 {c.statement} - {format_urls(c.urls)}\n" for c in self.contradictions]
        )

        return f"Commonalities:\n{commonalities}\n\nDivergencies:\n{divergencies}\n\nContradictions:\n{contradictions}"


def create_messages_list(chat_history, message):
    messages_list = []

    for message_pair in chat_history:
        user_message = message_pair[0]
        assistant_answer = message_pair[1]
        messages_list.append(ChatMessage(role=Role.USER, content=user_message))
        messages_list.append(ChatMessage(role=Role.ASSISTANT, content=assistant_answer))

    messages_list.append(ChatMessage(role=Role.USER, content=message))
    return messages_list


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message: str, chat_history: list[list[str]]):
        client = get_openAI_client()

        messages_list = create_messages_list(chat_history, message)

        news_data = get_data(message)
        print(news_data)

        messages_list = [
            ChatMessage(
                role=Role.SYSTEM,
                content="""User will send you news. You need to find commonalities, diversities and controversies.
                Commonalities - consensus points or shared facts among the articles.
                Divergencies - unique elements or differential aspects, distinct information or perpectives which are not commonly shared across the all articles.
                Controversies - contradictory points, it relates to any contradicting information or opposing views.
                
                Ignore unrelated sources.
                You need to return JSON file.
                
                Return JSON format:
                {
                "commonalities" : [{"statement": "First commonality", "urls": ["source_url1", "source_url2", "source_url3"]}, {"statement": "Second commonality", "urls": ["source_url1", "source_url2", "source_url3"]},],
                "divergencies" : [{"statement": "Divergency description", "urls": ["source_url1", "source_url2", "source_url3"]}, {"statement": "Divergency description", "urls": ["source_url1", "source_url2", "source_url3"]}]
                "contradictions" : [{"statement": "Contradiction Descriptions", "urls": ["source_url1", "source_url2", "source_url3"]}, {"statement": "Contradiction Descriptions", "urls": ["source_url1", "source_url2", "source_url3"]}]
                }            
                
                """,
            ),
            ChatMessage(role=Role.SYSTEM, content=f"""News: {news_data}"""),
        ]

        assistant_answer = chat_inference(client=client, messages=messages_list)
        print(assistant_answer)

        if assistant_answer is None:
            return "", chat_history

        parsed_answer = str(ArticleComparison.parse_raw(assistant_answer))

        new_pair = [message, parsed_answer]

        chat_history.append(new_pair)
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

demo.launch(share=True)
