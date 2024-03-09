from dataclasses import dataclass

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder)
from langchain.schema import SystemMessage

from model import transcribe


st.set_page_config(page_title="VoiceGPT", page_icon="🎙️")


@dataclass
class ChatRecord:
    message: str
    role: str


def display_chat_record(record):
    with st.chat_message(record.role):
        st.write(record.message)


def display_history():
    for record in st.session_state.history:
        display_chat_record(record)


def record():
    audio = audio_recorder(text="", pause_threshold=5.0, icon_size="2x")
    if audio:
        st.audio(audio, format="audio/wav")
        return audio


st.header("VoiceGPT", divider=True)


if "history" not in st.session_state:
    st.session_state.history = []

if "llm" not in st.session_state:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="You are a helpful chatbot taking transcribed audio input from a human. Your name is VoiceGPT."
            ),
            MessagesPlaceholder(
                variable_name="memory"
            ),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
    )
    memory = ConversationBufferWindowMemory(memory_key="memory", k=50, return_messages=True)
    st.session_state.llm = LLMChain(llm=ChatOpenAI(temperature=0), prompt=prompt, memory=memory, verbose=True)

question_audio = record()

display_history()

if question_audio:
    transcription = transcribe(question_audio)["text"]
    transcription = transcription.strip()

    question_record = ChatRecord(transcription, "human")

    st.session_state.history.append(question_record)
    display_chat_record(question_record)

    response = st.session_state.llm.predict(question=transcription)
    response_record = ChatRecord(response, "ai")

    st.session_state.history.append(response_record)
    display_chat_record(response_record)
