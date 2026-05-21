import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import tempfile
from pydub import AudioSegment

st.set_page_config(page_title="AI Voice Assistant")

st.title("🎙️ AI Voice Assistant")

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹️ Stop Recording",
    just_once=True
)

if audio:

    st.audio(audio["bytes"])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio["bytes"])
        temp_audio_path = temp_audio.name

    recognizer = sr.Recognizer()

    with sr.AudioFile(temp_audio_path) as source:

        audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            if "play" in text.lower():

                song = text.lower().replace("play", "")

                youtube_url = f"https://www.youtube.com/results?search_query={song}"

                st.link_button("▶ Open YouTube", youtube_url)

        except Exception as e:
            st.error(f"Recognition Error: {e}")
