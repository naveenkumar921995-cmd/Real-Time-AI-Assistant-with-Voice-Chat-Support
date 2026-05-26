import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import tempfile
import os
import time

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Text & Voice Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>

/* ---------------------------------------------------
IMPORT FONT
--------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---------------------------------------------------
GLOBAL
--------------------------------------------------- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---------------------------------------------------
MAIN APP
--------------------------------------------------- */
.stApp {
    background:
        radial-gradient(circle at top left, #1E3A8A 0%, transparent 25%),
        radial-gradient(circle at bottom right, #0F766E 0%, transparent 25%),
        linear-gradient(135deg, #020617, #0F172A);
    color: white;
}

/* ---------------------------------------------------
TITLE
--------------------------------------------------- */
.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 700;
    margin-top: 15px;
    color: white;
}

.gradient-text {
    background: linear-gradient(90deg, #38BDF8, #00FFD1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ---------------------------------------------------
SUBTITLE
--------------------------------------------------- */
.sub-title {
    text-align: center;
    color: #CBD5E1;
    font-size: 18px;
    margin-bottom: 35px;
}

/* ---------------------------------------------------
SIDEBAR
--------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ---------------------------------------------------
USER CHAT
--------------------------------------------------- */
.user-chat {
    background: rgba(30, 41, 59, 0.75);
    backdrop-filter: blur(16px);
    padding: 16px;
    border-radius: 18px;
    margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
}

/* ---------------------------------------------------
AI CHAT
--------------------------------------------------- */
.ai-chat {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(18px);
    padding: 18px;
    border-radius: 18px;
    margin-bottom: 16px;
    border: 1px solid rgba(56, 189, 248, 0.25);
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
}

/* ---------------------------------------------------
BUTTONS
--------------------------------------------------- */
.stButton > button {
    width: 100%;
    border-radius: 14px;
    height: 52px;
    border: none;
    background: linear-gradient(90deg, #06B6D4, #3B82F6);
    color: red;
    font-size: 16px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(59,130,246,0.35);
}

/* ---------------------------------------------------
CHAT INPUT
--------------------------------------------------- */
.stChatInputContainer {
    background: rgba(15, 23, 42, 0.8);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* ---------------------------------------------------
DOWNLOAD BUTTON
--------------------------------------------------- */
.stDownloadButton > button {
    background: linear-gradient(90deg, #10B981, #06B6D4);
    color: white;
    border-radius: 14px;
    border: none;
    height: 50px;
    font-weight: 600;
}

/* ---------------------------------------------------
TABS
--------------------------------------------------- */
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
    color: #CBD5E1;
}

.stTabs [aria-selected="true"] {
    color: #38BDF8 !important;
}

/* ---------------------------------------------------
MOBILE
--------------------------------------------------- */
@media (max-width: 768px) {

.main-title {
    font-size: 36px;
}

.sub-title {
    font-size: 15px;
}

.user-chat,
.ai-chat {
    padding: 14px;
}

}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# API KEY CHECK
# ---------------------------------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("Groq API Key not found")
    st.stop()

# ---------------------------------------------------
# GROQ CLIENT
# ---------------------------------------------------
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.title("⚙️ Settings")

    model = st.selectbox(
        "Choose AI Model",
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

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.markdown(
    """
    <div class="main-title">
        <span class="gradient-text">AI Voice Assistant</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sub-title">
        Smart AI Assistant Powered by Groq
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# FUNCTION TO GET AI RESPONSE
# ---------------------------------------------------
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

# ---------------------------------------------------
# TABS
# ---------------------------------------------------
tab1, tab2 = st.tabs(["💬 Text Chat", "🎤 Voice Chat"])

# ---------------------------------------------------
# TEXT CHAT
# ---------------------------------------------------
with tab1:

    user_input = st.chat_input("Type your message here...")

    if user_input:

        st.markdown(
            f"""
            <div class="user-chat">
            <b>🧑 You:</b><br>{user_input}
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.spinner("Thinking..."):

            answer = get_ai_response(user_input)

        placeholder = st.empty()

        streamed_text = ""

        for char in answer:

            streamed_text += char

            placeholder.markdown(
                f"""
                <div class="ai-chat">
                <b>🤖 AI:</b><br>{streamed_text}
                </div>
                """,
                unsafe_allow_html=True
            )

            time.sleep(0.002)

# ---------------------------------------------------
# VOICE CHAT
# ---------------------------------------------------
with tab2:

    st.info("Use your microphone to talk with AI")

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

        # ------------------------------------------------
        # TRANSCRIBE AUDIO
        # ------------------------------------------------
        with st.spinner("Transcribing audio..."):

            with open(audio_path, "rb") as audio_file:

                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3"
                )

            voice_text = transcription.text

        st.success(f"🧑 You said: {voice_text}")

        # ------------------------------------------------
        # AI RESPONSE
        # ------------------------------------------------
        with st.spinner("Generating response..."):

            answer = get_ai_response(voice_text)

        st.markdown(
            f"""
            <div class="ai-chat">
            <b>🤖 AI:</b><br>{answer}
            </div>
            """,
            unsafe_allow_html=True
        )

        os.remove(audio_path)

# ---------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------
st.divider()

st.subheader("📜 Conversation History")

for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class="user-chat">
            <b>🧑 You:</b><br>{msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="ai-chat">
            <b>🤖 AI:</b><br>{msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------
# DOWNLOAD CHAT
# ---------------------------------------------------
st.divider()

chat_history = ""

for msg in st.session_state.messages:

    role = msg["role"].upper()

    content = msg["content"]

    chat_history += f"{role}: {content}\n\n"

st.download_button(
    label="📥 Download Chat History",
    data=chat_history,
    file_name="chat_history.txt",
    mime="text/plain"
)
