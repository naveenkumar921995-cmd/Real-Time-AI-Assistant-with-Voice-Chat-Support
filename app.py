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
    page_title="AI Voice & Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0F172A, #1E293B);
    color: white;
}

/* Main Title */
.main-title {
    text-align: center;
    font-size: 50px;
    font-weight: bold;
    color: #00FFD1;
    margin-top: 10px;
}

.sub-title {
    text-align: center;
    color: #CBD5E1;
    font-size: 18px;
    margin-bottom: 30px;
}

/* User Chat */
.user-chat {
    background: #1E293B;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 12px;
    border-left: 5px solid #00FFD1;
}

/* AI Chat */
.ai-chat {
    background: #111827;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
    border-left: 5px solid #38BDF8;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 50px;
    font-size: 16px;
    font-weight: bold;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
}

/* Mobile Responsive */
@media (max-width: 768px) {

.main-title {
    font-size: 35px;
}

}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# API KEY CHECK
# ---------------------------------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("Groq API Key not found in Streamlit Secrets")
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
    '<div class="main-title">🤖 AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Text + Voice Assistant Powered by Groq</div>',
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
# TEXT CHAT TAB
# ---------------------------------------------------
with tab1:

    user_input = st.chat_input("Type your message here...")

    if user_input:

        # USER MESSAGE
        st.markdown(
            f"""
            <div class="user-chat">
            <b>🧑 You:</b><br>{user_input}
            </div>
            """,
            unsafe_allow_html=True
        )

        # AI RESPONSE
        with st.spinner("Thinking..."):

            answer = get_ai_response(user_input)

        # STREAMING EFFECT
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
# VOICE CHAT TAB
# ---------------------------------------------------
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

        # -----------------------------------------
        # TRANSCRIBE AUDIO USING GROQ WHISPER
        # -----------------------------------------
        with st.spinner("Transcribing audio..."):

            with open(audio_path, "rb") as audio_file:

                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3"
                )

            voice_text = transcription.text

        st.success(f"🧑 You said: {voice_text}")

        # -----------------------------------------
        # AI RESPONSE
        # -----------------------------------------
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

        # DELETE TEMP FILE
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
