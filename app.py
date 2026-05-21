import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os

st.set_page_config(page_title="AI Voice Assistant")

st.title("🎙️ AI Voice Assistant")

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹️ Stop Recording",
    just_once=True
)

if audio:

    st.audio(audio["bytes"])

    # Save WEBM audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:

        temp_webm.write(audio["bytes"])

        webm_path = temp_webm.name

    # Convert WEBM to WAV
    sound = AudioSegment.from_file(webm_path)

    wav_path = webm_path.replace(".webm", ".wav")

    sound.export(wav_path, format="wav")

    recognizer = sr.Recognizer()

    try:

        with sr.AudioFile(wav_path) as source:

            audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            if "play" in text.lower():

                song = text.lower().replace("play", "")

                youtube_url = f"https://www.youtube.com/results?search_query={song}"

                st.link_button("▶ Open YouTube", youtube_url)

    except Exception as e:

        st.error(f"Recognition Error: {e}")

    # Cleanup
    os.remove(webm_path)

    os.remove(wav_path)
