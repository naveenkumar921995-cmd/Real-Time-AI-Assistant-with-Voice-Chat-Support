import streamlit as st
import speech_recognition as sr
import webbrowser

st.set_page_config(page_title="AI Voice Assistant")

st.title("🎙️ AI Voice Assistant")

recognizer = sr.Recognizer()

if st.button("Start Listening"):

    try:
        with sr.Microphone() as source:

            st.write("Listening...")
            audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio)

            text = text.lower()

            st.success(f"You said: {text}")

            if "play" in text:

                song = text.replace("play", "")

                st.write(f"Searching YouTube for: {song}")

                youtube_url = f"https://www.youtube.com/results?search_query={song}"

                st.link_button("Open YouTube", youtube_url)

    except Exception as e:
        st.error(f"Error: {e}")
