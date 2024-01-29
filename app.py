from fastapi import FastAPI
import gradio as gr
import config as cfg
import logging
import google.cloud.logging
from google.cloud import speech
import vertexai
from vertexai.preview.language_models import ChatModel, ChatMessage

logger = logging.getLogger()
logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

vertexai.init(location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison-32k")


def transcribe_file(speech_file: str) -> speech.RecognizeResponse:
    """Transcribe the audio file."""
    text = ""
    client = speech.SpeechClient()

    with open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="yue-Hant-HK"
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        text = result.alternatives[0].transcript
        logger.info(f"Transcript: {text}")
    return text


def add_user_input(history, text):
    """Add user input to chat hostory."""
    history = history + [(text, None)]
    return history, gr.TextArea(
        value="", show_label=False, placeholder=cfg.bot["text_placeholder"], lines=4
    )


def bot_response(history):
    """Returns updated chat history with the Bot response."""

    # Intergate with ML models to load response.
    parameters = {
        "temperature": temperture.value,
        "max_output_tokens": token_limit.value,
        "top_p": top_p.value,
        "top_k": top_k.value
    }

    text = history[-1][0]

    # trim text and check if it is empty
    text = text.strip()
    if not text:
        history[-1][1] = "Please tell me something and click send button."
        return history

    # 会話履歴のリストを初期化
    message_history = []

    # 会話履歴のフォーマットを整形
    for row in history[1:]:
        input_from_user = row[0]
        output_from_llm = row[1]

        if output_from_llm is not None and input_from_user is not None:
            q_message = ChatMessage(author="user", content=input_from_user)
            message_history.append(q_message)
            a_message = ChatMessage(author="llm", content=output_from_llm)
            message_history.append(a_message)

    logger.info(message_history)
    chat = chat_model.start_chat(
        context="""Your name is a helpful assistant.
            Respond in short sentences. Shape your response as if talking to a 16-years-old.""",
        message_history=message_history
    )

    response = chat.send_message(text, **parameters)
    history[-1][1] = response.text
    return history


with gr.Blocks() as bot_interface:
    with gr.Row():
        gr.HTML(cfg.bot["banner"])
    with gr.Row():
        chatbot = gr.Chatbot(
            [(cfg.bot["initial_message"], None)], elem_id="chatbot", height=500)
    with gr.Row():
        with gr.Column(scale=12):
            user_input = gr.TextArea(
                show_label=False, placeholder=cfg.bot["text_placeholder"], lines=4
            )
        with gr.Column(scale=1, min_width=70):
            submitBtn = gr.Button("Send")
    with gr.Row():
        audio_input = gr.Audio(sources=["microphone"], type="filepath")
    with gr.Row():
        with gr.Column():
            temperture = gr.Slider(
                0, 1, step=0.1, label="Temperature", value=0.2, interactive=True)
            top_k = gr.Slider(0, 40, step=1, label="Top K",
                              value=40, interactive=True)
        with gr.Column():
            token_limit = gr.Slider(
                0, 8192, step=1, label="Token limit", value=2048, interactive=True)
            top_p = gr.Slider(0, 1, step=0.1, label="Top P",
                              value=0.8, interactive=True)
    with gr.Row():
        gr.HTML(cfg.bot["footer"])

    input_msg = user_input.submit(add_user_input, [chatbot, user_input], [chatbot, user_input], queue=False)\
        .then(bot_response, chatbot, chatbot)\
        .then(lambda: gr.TextArea(
            show_label=False, placeholder=cfg.bot["text_placeholder"], lines=4
        ),
        None, [user_input], queue=False)
    submitBtn.click(add_user_input, [chatbot, user_input], [chatbot, user_input], queue=False)\
        .then(bot_response, chatbot, chatbot)

    inputs_event = audio_input.stop_recording(transcribe_file, audio_input, user_input)\
        .then(add_user_input, [chatbot, user_input], [chatbot, user_input], queue=False)\
        .then(bot_response, chatbot, chatbot)\
        .then(lambda: gr.TextArea(
            show_label=False, placeholder=cfg.bot["text_placeholder"], lines=4
        ),
        None, [user_input], queue=False)

bot_interface.title = cfg.bot["title"]
# bot_interface.launch(share=True,server_name="0.0.0.0")

app = FastAPI()
app = gr.mount_gradio_app(app, bot_interface, path="/")
