import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import whisper
import tempfile
import os
import time

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0F172A, #1E293B);
    color: white;
}

.chat-user {
    background: #1E293B;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    border-left: 5px solid #00FFD1;
}

.chat-ai {
    background: #111827;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
    border-left: 5px solid #38BDF8;
}

.main-title {
    text-align: center;
    font-size: 50px;
    font-weight: bold;
    color: #00FFD1;
}

.subtitle {
    text-align: center;
    color: #CBD5E1;
    margin-bottom: 30px;
}

.stButton > button {
    border-radius: 12px;
    height: 50px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.markdown(
    '<div class="main-title">🤖 AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Text + Voice Powered by Groq</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# GROQ API
# -------------------------------------------------
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# -------------------------------------------------
# LOAD WHISPER MODEL
# -------------------------------------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_model = load_whisper()

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:

    st.title("⚙️ Settings")

    model = st.selectbox(
        "Choose Model",
        [
            "llama-3.3-70b-versatile",
            "llama3-8b-8192",
            "mixtral-8x7b-32768"
        ]
    )

    temperature = st.slider(
        "Creativity",
        0.0,
        1.0,
        0.7
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------
# FUNCTION TO GET AI RESPONSE
# -------------------------------------------------
def get_ai_response(user_input):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    response = client.chat.completions.create(
        model=model,
        messages=st.session_state.messages,
        temperature=temperature
    )

    answer = response.choices[0].message.content

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return answer

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2 = st.tabs(["💬 Text Chat", "🎤 Voice Chat"])

# -------------------------------------------------
# TEXT CHAT
# -------------------------------------------------
with tab1:

    text_input = st.chat_input("Type your message...")

    if text_input:

        st.markdown(
            f"""
            <div class="chat-user">
            <b>🧑 You:</b><br>{text_input}
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.spinner("Thinking..."):

            answer = get_ai_response(text_input)

        # Streaming Effect
        placeholder = st.empty()

        streamed = ""

        for char in answer:

            streamed += char

            placeholder.markdown(
                f"""
                <div class="chat-ai">
                <b>🤖 AI:</b><br>{streamed}
                </div>
                """,
                unsafe_allow_html=True
            )

            time.sleep(0.003)

# -------------------------------------------------
# VOICE CHAT
# -------------------------------------------------
with tab2:

    st.info("Record your voice below")

    audio = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="⏹️ Stop Recording",
        just_once=True,
        use_container_width=True
    )

    if audio:

        st.audio(audio["bytes"])

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_audio:

            temp_audio.write(audio["bytes"])

            audio_path = temp_audio.name

        # -----------------------------
        # TRANSCRIBE AUDIO
        # -----------------------------
        with st.spinner("Transcribing..."):

            result = whisper_model.transcribe(audio_path)

            voice_text = result["text"]

        st.success(f"🧑 You said: {voice_text}")

        # -----------------------------
        # GET AI RESPONSE
        # -----------------------------
        with st.spinner("Generating response..."):

            answer = get_ai_response(voice_text)

        st.markdown(
            f"""
            <div class="chat-ai">
            <b>🤖 AI:</b><br>{answer}
            </div>
            """,
            unsafe_allow_html=True
        )

        os.remove(audio_path)

# -------------------------------------------------
# CHAT HISTORY
# -------------------------------------------------
st.divider()

st.subheader("📜 Conversation History")

for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-user">
            <b>🧑 You:</b><br>{msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="chat-ai">
            <b>🤖 AI:</b><br>{msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )
