import gradio as gr
import random
import time

from chatting import ChatMessage, chat_inference, get_openAI_client, Role

from sourcing import get_data


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

        messages_list = [
            ChatMessage(
                role=Role.SYSTEM,
                content="""User will send you a news. You need to find similarities and contradictions.
                You need to return JSON file. {
                "simmilarities" : [{"statement": "First simmilarity", "urls": ["source_url1", "source_url2", "source_url3"]}, {"statement": "Second simmilarity", "urls": ["source_url1", "source_url2", "source_url3"]},],
                "contradictions" : [{"contradictive statement": "Contradiction Descriptions", "urls": ["source_url1", "source_url2", "source_url3"]}, {"contradictive statement": "Contradiction Descriptions", "urls": ["source_url1", "source_url2", "source_url3"]}]
                Return only JSON File
                }""",
            ),
            ChatMessage(role=Role.SYSTEM, content=f"""News: {news_data}"""),
        ]

        assistant_answer = chat_inference(client=client, messages=messages_list)

        new_pair = [message, assistant_answer]

        chat_history.append(new_pair)
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

demo.launch(share=True)
