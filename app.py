import streamlit as st
import speech_recognition as sr
import pywhatkit as pk
from gtts import gTTS
import os

st.title("🎙️ AI Voice Assistant")

recognizer = sr.Recognizer()

if st.button("Start Listening"):

    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)

        st.success(f"You said: {text}")

        if "play" in text:
            song = text.replace("play", "")

            st.write(f"Playing {song}")

            pk.playonyt(song)

    except:
        st.error("Could not understand audio")
