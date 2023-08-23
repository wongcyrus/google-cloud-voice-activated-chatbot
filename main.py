import time
import gradio as gr
import config as cfg
from google.cloud import speech
import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
from google.cloud import translate_v2 as translate

vertexai.init(project="cyrus-testing-2023", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison@001")
chat = chat_model.start_chat(
    context="""Your name is a helpful assistant.
            Respond in short sentences. Shape your response as if talking to a 16-years-old."""
)

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
        print(f"Transcript: {text}")
    return text

def add_user_input(history, text):    
    """Add user input to chat hostory."""
    history = history + [(text, None)]
    return history, gr.update(value="", interactive=True)
   

def bot_response(history):
    """Returns updated chat history with the Bot response."""

    # Intergate with ML models to load response.
    parameters = {
        "temperature": temperture.value,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }

    text = history[-1][0]

    # trim text and check if it is empty
    text = text.strip()
    if not text:        
        history[-1][1] = "Please tell me something and click send button."       
        return history
    
    # translate text to English
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language="en")
    text = result["translatedText"]
    print(f"Translated text: {text}")
    response = chat.send_message(text, **parameters)
    # response = cfg.bot["temp_response"]
    history[-1][1] = response.text    
    return history

with gr.Blocks() as bot_interface:
    with gr.Row():
        gr.HTML(cfg.bot["banner"])    
    with gr.Row(scale=1):
        chatbot=gr.Chatbot([(cfg.bot["initial_message"], None)], elem_id="chatbot").style(height=600)
    with gr.Row(scale=1):
        with gr.Column(scale=12):
            user_input = gr.Textbox(
                show_label=False, placeholder=cfg.bot["text_placeholder"],
            ).style(container=False)
        with gr.Column(min_width=70, scale=1):
            submitBtn = gr.Button("Send")
    with gr.Row(scale=1):
        audio_input=gr.Audio(source="microphone", type="filepath")
    with gr.Row(scale=1):
        with gr.Column(scale=1):
           temperture = gr.Slider(0, 1, step=0.1, label="Temperature", value=0.2, interactive=True)
           top_k = gr.Slider(0, 40, step=1, label="Top K", value=40, interactive=True)
        with gr.Column(scale=1):
           token_limit = gr.Slider(0, 1024, step=1, label="Token limit", value=256, interactive=True)
           top_p = gr.Slider(0, 1, step=0.1, label="Top P", value=0.8, interactive=True)
    with gr.Row():
        gr.HTML(cfg.bot["footer"])    
    
    input_msg = user_input.submit(add_user_input, [chatbot, user_input], [chatbot, user_input], queue=False).then(bot_response, chatbot, chatbot)
    submitBtn.click(add_user_input, [chatbot, user_input], [chatbot, user_input], queue=False).then(bot_response, chatbot, chatbot)
    input_msg.then(lambda: gr.update(interactive=True), None, [user_input], queue=False)
    inputs_event = audio_input.stop_recording(transcribe_file, audio_input, user_input)\
        .then(add_user_input, [chatbot, user_input], [chatbot, user_input], queue=False)\
            .then(bot_response, chatbot, chatbot)
    inputs_event.then(lambda: gr.update(interactive=True), None, [user_input], queue=False)

bot_interface.title = cfg.bot["title"]
bot_interface.launch(share=True)