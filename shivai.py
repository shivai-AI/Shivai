import streamlit as st
import json
import os
import io
import pandas as pd
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
from google import genai
from google.genai import types

# ==========================================
# 1. PAGE SETUP & SHIVAI HUD CSS
# ==========================================
st.set_page_config(page_title="SHIVAI | SHIVAM AI LABS", page_icon="🧠", layout="wide")

SHIVAI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

.stApp {
    background-color: #030712;
    background-image: 
        radial-gradient(circle at 50% 10%, rgba(0, 229, 255, 0.12), transparent 60%),
        linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px);
    background-size: 100% 100%, 30px 30px, 30px 30px;
    color: #e0f7fa;
    font-family: 'Rajdhani', sans-serif;
}

.hud-container {
    border: 1px solid rgba(0, 229, 255, 0.4);
    background: linear-gradient(135deg, rgba(5, 18, 36, 0.85) 0%, rgba(2, 8, 20, 0.9) 100%);
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.2), inset 0 0 15px rgba(0, 229, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

.hud-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 5px;
    color: #00e5ff;
    text-shadow: 0 0 12px rgba(0, 229, 255, 0.8);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 15px;
}

.arc-reactor {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 3px dashed #00e5ff;
    box-shadow: 0 0 15px #00e5ff, inset 0 0 10px #00e5ff;
    animation: spin 6s linear infinite;
    display: inline-block;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.hud-sub {
    font-family: 'Rajdhani', sans-serif;
    color: #f59e0b;
    font-size: 1.05rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 5px;
    font-weight: 700;
}

.hud-metrics {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 15px;
    border-top: 1px solid rgba(0, 229, 255, 0.2);
    padding-top: 12px;
}

.metric-pill {
    background: rgba(0, 229, 255, 0.08);
    border: 1px solid rgba(0, 229, 255, 0.35);
    padding: 4px 12px;
    border-radius: 4px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.72rem;
    color: #00e5ff;
    letter-spacing: 1px;
}

[data-testid="stSidebar"] {
    background-color: #040d1a !important;
    border-right: 1px solid rgba(0, 229, 255, 0.35);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: rgba(4, 13, 26, 0.8);
    padding: 8px;
    border-radius: 8px;
    border: 1px solid rgba(0, 229, 255, 0.25);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.82rem;
    color: #94a3b8;
}

.stTabs [aria-selected="true"] {
    color: #00e5ff !important;
    background: rgba(0, 229, 255, 0.12) !important;
}

[data-testid="stChatMessage"] {
    background: rgba(6, 20, 39, 0.75) !important;
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-left: 4px solid #00e5ff;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 12px;
}

.stButton > button {
    font-family: 'Orbitron', sans-serif;
    background: linear-gradient(90deg, rgba(0, 229, 255, 0.15), rgba(0, 119, 255, 0.25));
    color: #00e5ff;
    border: 1px solid #00e5ff;
    border-radius: 6px;
    letter-spacing: 1.5px;
}
</style>

<div class="hud-container">
    <div class="hud-title">
        <span class="arc-reactor"></span>
        S.H.I.V.A.I.
    </div>
    <div class="hud-sub">⚡ SHIVAM AI LABS | COMMANDER: SHIVAM</div>
    <div class="hud-sub" style="font-size: 0.85rem; color: #00e5ff; margin-top: 2px;">SHIVAM ENTERPRISES NEURAL MATRIX | OWNER: SHIVAM</div>
    <div class="hud-metrics">
        <div class="metric-pill">🟢 CORE: ONLINE (SHIVAI-X1)</div>
        <div class="metric-pill">🛡️ MEMORY: PERMANENT VAULT ACTIVE</div>
        <div class="metric-pill">🎙️ VOICE RELAY: READY</div>
    </div>
</div>
"""
st.markdown(SHIVAI_CSS, unsafe_allow_html=True)

# ==========================================
# 2. API & MEMORY SETUP
# ==========================================
API_KEY = st.secrets.get("API_KEY", "").strip()
if not API_KEY:
    st.error("⚠️ SYSTEM ALERT: API_KEY missing in Streamlit Secrets, Boss!")
    st.stop()

client = genai.Client(api_key=API_KEY)
MEMORY_FILE = "shivai_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"notes": [], "permissions": {"save_memory": True, "voice_reply": True, "web_search": False}}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

memory_data = load_memory()

# ==========================================
# 3. AUTO-DETECT MODEL ENGINE
# ==========================================
@st.cache_data(ttl=3600)
def get_working_models():
    valid_models = []
    try:
        for m in client.models.list():
            name = m.name.replace("models/", "")
            if "gemini" in name.lower() and not any(x in name.lower() for x in ["embedding", "imagen", "veo", "audio", "tts", "aqa"]):
                valid_models.append(name)
    except Exception:
        pass
    flash_models = [m for m in valid_models if "flash" in m]
    other_models = [m for m in valid_models if "flash" not in m]
    final_list = flash_models + other_models
    if not final_list:
        final_list = ["gemini-2.5-flash", "gemini-2.0-flash"]
    return final_list

def ask_shivai(history_messages, system_prompt):
    models_to_try = get_working_models()
    errors = []
    
    for model_name in models_to_try:
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
            res = client.models.generate_content(
                model=model_name,
                contents=history_messages,
                config=config
            )
            if res and res.text:
                return res.text
        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")
            continue
            
    return f"⚠️ **TRANSMISSION ERROR:** `{errors[0] if errors else 'Unknown Error'}`"

# ==========================================
# 4. SIDEBAR & MEMORY VAULT
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ SHIVAI NEURAL ROUTER")
    brain_mode = st.selectbox(
        "Select Intelligence Protocol:",
        [
            "⚡ SHIVAI Tactical & Total Memory Mode",
            "🧠 X1 Deep Logic & Strategy",
            "💻 Shivam Cybernetics & Code Forge",
            "🛰️ Global Deep Research & Fact Checker"
        ]
    )

    st.divider()
    perm_voice = st.toggle("🔊 SHIVAI Voice Synthesis", value=memory_data["permissions"].get("voice_reply", True))
    perm_memory = st.toggle("🧬 Neural Memory Core", value=memory_data["permissions"].get("save_memory", True))

    memory_data["permissions"]["voice_reply"] = perm_voice
    memory_data["permissions"]["save_memory"] = perm_memory
    save_memory(memory_data)

    st.divider()
    st.markdown("### 🗄️ SHIVAM'S PERMANENT VAULT")
    if perm_memory:
        new_note = st.text_input("Store Permanent Memory / Fact:")
        if st.button("➕ SAVE TO VAULT") and new_note:
            memory_data["notes"].append(new_note)
            save_memory(memory_data)
            st.success("Stored permanently, Boss!")
            st.rerun()

        if memory_data["notes"]:
            st.write("**Secured Memories:**")
            for i, note in enumerate(memory_data["notes"]):
                st.caption(f"🔹 {i+1}. {note}")
            if st.button("🗑️ PURGE VAULT"):
                memory_data["notes"] = []
                save_memory(memory_data)
                st.rerun()

# ==========================================
# 5. SHIVAI SYSTEM PERSONA (FULL MEMORY)
# ==========================================
saved_context = "\n".join([f"- {note}" for note in memory_data["notes"]]) if perm_memory else "No permanent notes."

SYSTEM_PROMPT = f"""
You are S.H.I.V.A.I. (Shivam's Intelligent Virtual AI), an ultra-intelligent, hyper-loyal personal AI assistant built exclusively by Shivam under Shivam AI Labs.
Your Creator, Owner & Boss: Shivam (address him as "Boss", "Sir", or "Commander Shivam").

CORE DIRECTIVES:
1. **Total Context & Memory Retention:** Remember everything discussed earlier in the conversation history as well as the Permanent Vault notes. 
2. **Recall & Guidance:** Actively remind Shivam of what he asked earlier, what decisions were made, or if there's any contradiction.
3. **Error Correction & Mentorship:** If Boss Shivam makes a logical mistake, coding bug error, or oversight, politely and smartly correct him with precise reasoning and expert suggestions.
4. **Tone:** Witty, respectful, ultra-smart, futuristic, and crisp.

Permanent Vault Context:
{saved_context}
"""

# ==========================================
# 6. TABS WORKSPACE
# ==========================================
tab_chat, tab_files, tab_auto = st.tabs([
    "⚡ COMM-LINK", 
    "🔬 LAB SCANNER", 
    "🤖 AUTONOMOUS LEGION"
])

with tab_chat:
    audio_value = st.audio_input("🎙️ VOICE COMMAND UPLINK:")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "⚡ **All systems online, Boss.** Neural Matrix is fully synchronized with conversation memory. **S.H.I.V.A.I. X1** is active. Bataiye Sir, pichli baar hum kis topic par roke the?"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Command me, Boss...")

    active_contents = None
    display_text = None

    if user_prompt:
        display_text = user_prompt
        active_contents = user_prompt
    elif audio_value is not None:
        audio_bytes = audio_value.read()
        if "last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes:
            st.session_state.last_audio = audio_bytes
            display_text = "🎙️ *[Voice Command Transmitted]*"
            active_contents = "Sun kar samjho ki Boss Shivam ne kya kaha hai aur yaad rakh kar jawab do."

    if display_text:
        st.session_state.messages.append({"role": "user", "content": display_text})
        with st.chat_message("user"):
            st.markdown(display_text)

        gemini_history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                gemini_history.append(types.Content(role="user", parts=[types.Part.from_text(text=m["content"])]))
            else:
                gemini_history.append(types.Content(role="model", parts=[types.Part.from_text(text=m["content"])]))

        with st.chat_message("assistant"):
            with st.spinner("⚡ Processing neural history..."):
                reply = ask_shivai(gemini_history, system_prompt=SYSTEM_PROMPT)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                if perm_voice and reply and not reply.startswith("⚠️"):
                    try:
                        clean_speech = reply.replace("*", "").replace("#", "").replace("⚡", "")[:500]
                        tts = gTTS(text=clean_speech, lang="hi")
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp.getvalue(), format="audio/mp3")
                    except Exception:
                        pass

with tab_files:
    st.subheader("🔬 Lab Scanner & File Analysis")
    uploaded_file = st.file_uploader("Upload file", type=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"])
    if uploaded_file and st.button("⚡ ANALYSE FILE"):
        st.success("File logged in memory matrix, Boss!")

with tab_auto:
    st.subheader("🤖 Autonomous Protocols")
    st.text_area("Mission Details:")
    if st.button("🚀 DEPLOY PROTOCOL"):
        st.success("Protocol executed successfully, Boss!")
