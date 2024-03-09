from transformers import pipeline


def transcribe(audio):
    transcriber = pipeline(model="openai/whisper-base")
    return transcriber(audio)
