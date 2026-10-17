import os
import io
import json
import base64
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
from google import genai
from google.genai import types

# =====================================================================
# 1. APPLICATION CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="ShivAI — Beyond Intelligence",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# 2. SECURE API GATEWAY (HIDDEN CREDENTIAL MANAGEMENT)
# =====================================================================
def _resolve_hidden_api_key() -> str:
    # Priority 1: Check Streamlit Cloud Secrets silently
    for secret_name in ("API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        try:
            if secret_name in st.secrets:
                val = str(st.secrets[secret_name]).strip()
                if val:
                    return val
        except Exception:
            pass

    # Priority 2: Check Server Environment Variables
    for env_name in ("API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = os.environ.get(env_name, "").strip()
        if val:
            return val

    # Priority 3: Check Encrypted Session Vault (Temporary Masked Input)
    return st.session_state.get("_vault_runtime_key", "").strip()


def get_secure_ai_client():
    raw_key = _resolve_hidden_api_key()
    if not raw_key:
        return None
    try:
        return genai.Client(api_key=raw_key)
    except Exception:
        return None


# =====================================================================
# 3. PERSISTENT KNOWLEDGE VAULT (LOCAL JSON STORAGE)
# =====================================================================
MEMORY_FILE = "shivai_memory.json"

def load_vault_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            pass
    return {
        "notes": [],
        "permissions": {
            "save_memory": True,
            "voice_reply": True
        }
    }


def save_vault_memory(data: dict) -> None:
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception:
        pass


vault_data = load_vault_memory()

if "active_view" not in st.session_state:
    st.session_state.active_view = "New Chat"
if "messages" not in st.session_state:
    st.session_state.messages = []


# =====================================================================
# 4. DESIGN SYSTEM & PIXEL-ACCURATE CSS (NO TRIPLE QUOTES)
# =====================================================================
UI_STYLESHEET = [
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@700;900&display=swap');",
    ".stApp { background: radial-gradient(circle at 50% 28%, rgba(22, 100, 255, 0.18) 0%, rgba(110, 40, 255, 0.08) 32%, transparent 65%), radial-gradient(ellipse at 50% 92%, rgba(0, 140, 255, 0.22) 0%, rgba(5, 9, 20, 0.95) 55%), #050914 !important; color: #F4F7FF !important; font-family: 'Inter', sans-serif !important; }",
    ".block-container { padding-top: 1.5rem !important; padding-bottom: 6rem !important; max-width: 500px !important; }",
    ".hero-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 8px; }",
    ".vortex-container { position: relative; width: 200px; height: 200px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }",
    ".vortex-ring-1 { position: absolute; width: 190px; height: 190px; border-radius: 50%; background: conic-gradient(from 0deg, transparent 0deg, #00d2ff 60deg, #3a7bd5 120deg, #8b5cff 180deg, transparent 240deg, #00e5ff 300deg, transparent 360deg); filter: blur(8px); animation: spin-vortex 7s linear infinite; opacity: 0.9; }",
    ".vortex-ring-2 { position: absolute; width: 156px; height: 156px; border-radius: 50%; border: 2px solid rgba(0, 229, 255, 0.55); box-shadow: 0 0 35px #168BFF, inset 0 0 30px #8B5CFF, 0 0 65px rgba(139, 92, 255, 0.45); animation: spin-vortex-rev 5s linear infinite; }",
    ".vortex-core { position: relative; width: 102px; height: 102px; border-radius: 50%; background: radial-gradient(circle, #06132e 0%, #02050d 85%); box-shadow: inset 0 0 22px rgba(0, 210, 255, 0.7), 0 0 25px rgba(0, 170, 255, 0.6); display: flex; align-items: center; justify-content: center; z-index: 3; }",
    ".vortex-s { font-family: 'Orbitron', sans-serif; font-size: 3.2rem; font-weight: 900; background: linear-gradient(180deg, #9beeff 0%, #168BFF 55%, #6342ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 0 12px rgba(0, 210, 255, 0.85)); }",
    "@keyframes spin-vortex { 0% { transform: rotate(0deg) scale(1); } 50% { transform: rotate(180deg) scale(1.04); } 100% { transform: rotate(360deg) scale(1); } }",
    "@keyframes spin-vortex-rev { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }",
    ".shivai-logo-text { font-family: 'Inter', sans-serif; font-size: 3.2rem; font-weight: 800; letter-spacing: -1px; line-height: 1.05; margin: 0; }",
    ".shivai-logo-text .shiv-part { color: #FFFFFF; }",
    ".shivai-logo-text .ai-part { background: linear-gradient(180deg, #38B6FF 0%, #168BFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 0 15px rgba(22, 139, 255, 0.5)); }",
    ".beyond-subtitle { font-size: 1.15rem; font-weight: 400; color: #D6E2FF; margin-top: 6px; margin-bottom: 30px; }",
    ".personal-assistant-label { font-size: 0.95rem; font-weight: 500; color: #E2ECFF; margin-bottom: 10px; }",
    ".capabilities-row { font-size: 0.72rem; font-weight: 600; letter-spacing: 2.3px; color: #9AAAC4; text-transform: uppercase; margin-bottom: 20px; }",
    ".horizon-glow { width: 100%; height: 40px; background: radial-gradient(ellipse at 50% 0%, rgba(22, 160, 255, 0.45) 0%, transparent 70%); border-top: 1px solid rgba(56, 182, 255, 0.35); margin-top: 4px; margin-bottom: 8px; }",
    ".mode-pills { display: flex; justify-content: center; gap: 12px; margin-bottom: 8px; }",
    ".pill-active { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.2); color: #FFFFFF; padding: 6px 20px; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }",
    ".pill-inactive { color: #9AAAC4; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }",
    "[data-testid='stSidebar'] { background: linear-gradient(180deg, #050914 0%, #040812 100%) !important; border-right: 1px solid rgba(56, 182, 255, 0.18) !important; width: 305px !important; }",
    ".sb-header { display: flex; align-items: center; gap: 12px; padding-bottom: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 10px; }",
    ".sb-mini-orb { width: 42px; height: 42px; border-radius: 50%; background: radial-gradient(circle, #06152d 35%, #168BFF 75%, #8B5CFF 100%); box-shadow: 0 0 15px rgba(22, 139, 255, 0.8), inset 0 0 8px #00e5ff; display: flex; align-items: center; justify-content: center; font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 1.15rem; color: #FFFFFF; }",
    ".sb-title { font-size: 1.3rem; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin: 0; }",
    ".sb-title span { color: #168BFF; }",
    ".sb-sub { font-size: 0.74rem; color: #9AAAC4; margin: 2px 0 0 0; }",
    "[data-testid='stSidebar'] .stButton > button { background: transparent !important; color: #F4F7FF !important; border: none !important; border-radius: 10px !important; padding: 9px 12px !important; font-size: 0.9rem !important; font-weight: 500 !important; display: flex !important; align-items: center !important; justify-content: flex-start !important; width: 100% !important; box-shadow: none !important; margin-bottom: 2px !important; }",
    "[data-testid='stSidebar'] .stButton > button:hover { background: rgba(22, 139, 255, 0.14) !important; color: #FFFFFF !important; }",
    ".st-key-nav_new button::after { content: 'Ctrl + N'; margin-left: auto; color: #647794; font-size: 0.74rem; }",
    ".st-key-nav_voice button::after { content: 'Ctrl + V'; margin-left: auto; color: #647794; font-size: 0.74rem; }",
    ".st-key-nav_res button::after { content: 'Ctrl + R'; margin-left: auto; color: #647794; font-size: 0.74rem; }",
    ".st-key-nav_mod button::after { content: 'Ctrl + M'; margin-left: auto; color: #647794; font-size: 0.74rem; }",
    ".st-key-nav_proj button::after { content: 'Ctrl + P'; margin-left: auto; color: #647794; font-size: 0.74rem; }",
    ".st-key-nav_vault button::after { content: 'Ctrl + K'; margin-left: auto; color: #647794; font-size: 0.74rem; }",
    ".sb-section-label { font-size: 0.76rem; font-weight: 600; color: #9AAAC4; margin: 12px 0 8px 4px; }",
    ".sb-icon-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; text-align: center; margin-bottom: 12px; }",
    ".sb-icon-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align: center; margin-bottom: 14px; }",
    ".sb-tile { display: flex; flex-direction: column; align-items: center; gap: 4px; }",
    ".sb-tile-box { width: 42px; height: 42px; border-radius: 11px; background: #0B1628; border: 1px solid rgba(56, 182, 255, 0.22); display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }",
    ".sb-tile-name { font-size: 0.66rem; color: #C4D2EC; font-weight: 500; }",
    ".sb-footer { text-align: center; margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); }",
    ".sb-footer-text { font-size: 0.74rem; color: #9AAAC4; margin-bottom: 6px; }",
    ".sb-wave { height: 3px; width: 85px; margin: 0 auto; background: linear-gradient(90deg, transparent, #168BFF, #8B5CFF, transparent); border-radius: 3px; }",
    "[data-testid='stChatMessage'] { background: #0B1628 !important; border: 1px solid rgba(22, 139, 255, 0.25); border-radius: 14px; padding: 12px 15px; margin-bottom: 10px; }",
    "</style>"
]
st.markdown("\n".join(UI_STYLESHEET), unsafe_allow_html=True)


# =====================================================================
# 5. AI ORCHESTRATION & BOOSTED VOICE ENGINE
# =====================================================================
@st.cache_data(ttl=3600)
def get_available_models() -> list:
    client = get_secure_ai_client()
    if not client:
        return ["gemini-2.5-flash", "gemini-2.0-flash"]
    discovered = []
    try:
        for model in client.models.list():
            name = model.name.replace("models/", "")
            excluded = ("embedding", "imagen", "veo", "audio", "tts", "aqa")
            if "gemini" in name.lower() and not any(tag in name.lower() for tag in excluded):
                discovered.append(name)
    except Exception:
        pass
    flash_tier = [m for m in discovered if "flash" in m]
    pro_tier = [m for m in discovered if "flash" not in m]
    return (flash_tier + pro_tier) or ["gemini-2.5-flash", "gemini-2.0-flash"]


def generate_shivai_response(contents_payload, system_instruction: str) -> str:
    client = get_secure_ai_client()
    if not client:
        return "🔒 **Security Alert:** API key is not configured. Please add `API_KEY` in Streamlit Secrets or unlock it in the **Settings** menu."

    for model_id in get_available_models():
        try:
            config = types.GenerateContentConfig(system_instruction=system_instruction)
            response = client.models.generate_content(
                model=model_id,
                contents=contents_payload,
                config=config
            )
            if response and response.text:
                return response.text
        except Exception:
            continue
    return "⚡ **Neural Gateway Busy:** Unable to reach the AI core right now. Please retry in a few seconds."


def synthesize_boosted_voice(speech_text: str) -> None:
    try:
        clean_text = speech_text.replace("*", "").replace("#", "").replace("⚡", "")[:450]
        tts = gTTS(text=clean_text, lang="hi")
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        encoded_mp3 = base64.b64encode(audio_buffer.getvalue()).decode("utf-8")
        audio_script = [
            f"<audio id='shivai-voice' src='data:audio/mp3;base64,{encoded_mp3}' autoplay></audio>",
            "<script>",
            "(function() {",
            "  const el = document.getElementById('shivai-voice');",
            "  if (el) {",
            "    try {",
            "      const AudioCtx = window.AudioContext || window.webkitAudioContext;",
            "      const ctx = new AudioCtx();",
            "      const source = ctx.createMediaElementSource(el);",
            "      const gainNode = ctx.createGain();",
            "      gainNode.gain.value = 3.0;",
            "      source.connect(gainNode);",
            "      gainNode.connect(ctx.destination);",
            "      el.play();",
            "    } catch(err) { el.play(); }",
            "  }",
            "})();",
            "</script>"
        ]
        components.html("\n".join(audio_script), height=0)
    except Exception:
        pass


# =====================================================================
# 6. SIDEBAR DRAWER NAVIGATION
# =====================================================================
with st.sidebar:
    sidebar_brand = (
        "<div class='sb-header'>"
        "<div class='sb-mini-orb'>S</div>"
        "<div><div class='sb-title'>Shiv<span>AI</span></div>"
        "<div class='sb-sub'>Beyond Intelligence.</div></div>"
        "</div>"
    )
    st.markdown(sidebar_brand, unsafe_allow_html=True)

    if st.button("☑️   New Chat", key="nav_new"):
        st.session_state.active_view = "New Chat"
        st.session_state.messages = []
        st.rerun()

    if st.button("🎙️   Voice Mode", key="nav_voice"):
        st.session_state.active_view = "Voice Mode"
        st.rerun()

    if st.button("🔍   Research", key="nav_res"):
        st.session_state.active_view = "Research"
        st.rerun()

    if st.button("⚛️   AI Models", key="nav_mod"):
        st.session_state.active_view = "AI Models"
        st.rerun()

    if st.button("📁   Projects", key="nav_proj"):
        st.session_state.active_view = "Projects"
        st.rerun()

    if st.button("🛡️   Knowledge Vault", key="nav_vault"):
        st.session_state.active_view = "Knowledge Vault"
        st.rerun()

    if st.button("⚙️   Settings", key="nav_set"):
        st.session_state.active_view = "Settings"
        st.rerun()

    sidebar_widgets = [
        "<div style='border-top: 1px solid rgba(255,255,255,0.08); margin-top: 8px; padding-top: 4px;'>",
        "<div class='sb-section-label'>Connected AI Models</div>",
        "<div class='sb-icon-grid-5'>",
        "<div class='sb-tile'><div class='sb-tile-box'>🌀</div><div class='sb-tile-name'>GPT-4o</div></div>",
        "<div class='sb-tile'><div class='sb-tile-box'>✦</div><div class='sb-tile-name'>Gemini</div></div>",
        "<div class='sb-tile'><div class='sb-tile-box'>✴️</div><div class='sb-tile-name'>Claude</div></div>",
        "<div class='sb-tile'><div class='sb-tile-box'>♾️</div><div class='sb-tile-name'>Llama</div></div>",
        "<div class='sb-tile'><div class='sb-tile-box'>＋</div><div class='sb-tile-name'>More</div></div>",
        "</div></div>",
        "<div style='border-top: 1px solid rgba(255,255,255,0.08); padding-top: 4px;'>",
        "<div class='sb-section-label'>Live Tools</div>",
        "<div class='sb-icon-grid-4'>",
        "<div class='sb-tile'><div class='sb-tile-box'>🔍</div><div class='sb-tile-name'>Web Search</div></div>",
        "<div class='sb-tile'><div class='sb-tile-box'>🖼️</div><div class='sb-tile-name'>Image Gen</div></div>",
        "<div class='sb-tile'><div class='sb-tile-box'>&lt;/&gt;</div><div class='sb-tile-name'>Code</div></div>",
        "<div class='sb-tile'><div class='sb-tile-box'>📝</div><div class='sb-tile-name'>Canvas</div></div>",
        "</div></div>",
        "<div class='sb-footer'><div class='sb-footer-text'>Smarter Tools. Bigger Dreams.</div><div class='sb-wave'></div></div>"
    ]
    st.markdown("\n".join(sidebar_widgets), unsafe_allow_html=True)


# =====================================================================
# 7. CORE SYSTEM DIRECTIVE
# =====================================================================
vault_notes_str = "\n".join([f"- {item}" for item in vault_data["notes"]]) if vault_data["notes"] else "No permanent notes stored."
SYSTEM_INSTRUCTION = (
    "You are ShivAI (Beyond Intelligence), a personal intelligence system created exclusively by Shivam. "
    "Address Shivam respectfully as Boss, Sir, or Commander Shivam. "
    "Maintain full context across the conversation history, proactively recall previous decisions, politely correct any mistakes, "
    "and provide strategic, high-ROI guidance for his technology projects and Shivam Tea Traders (Ballia). "
    f"Knowledge Vault Context:\n{vault_notes_str}"
)


# =====================================================================
# 8. MAIN APPLICATION VIEWS
# =====================================================================
current_view = st.session_state.active_view

if current_view == "New Chat":
    if len(st.session_state.messages) == 0:
        front_screen_html = [
            "<div class='hero-wrapper'>",
            "<div class='vortex-container'>",
            "<div class='vortex-ring-1'></div>",
            "<div class='vortex-ring-2'></div>",
            "<div class='vortex-core'><span class='vortex-s'>S</span></div>",
            "</div>",
            "<h1 class='shivai-logo-text'><span class='shiv-part'>Shiv</span><span class='ai-part'>AI</span></h1>",
            "<div class='beyond-subtitle'>Beyond Intelligence.</div>",
            "<div class='personal-assistant-label'>Your Personal AI Assistant</div>",
            "<div class='capabilities-row'>CHAT &nbsp;·&nbsp; RESEARCH &nbsp;·&nbsp; CREATE &nbsp;·&nbsp; AUTOMATE</div>",
            "<div class='horizon-glow'></div>",
            "<div class='mode-pills'><span class='pill-active'>Chat</span><span class='pill-inactive'>Task</span></div>",
            "</div>"
        ]
        st.markdown("\n".join(front_screen_html), unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    user_query = st.chat_input("Ask anything... (or type @ for tools)")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        formatted_history = [
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])]
            )
            for msg in st.session_state.messages
        ]

        with st.chat_message("assistant"):
            with st.spinner("⚡ ShivAI thinking..."):
                ai_reply = generate_shivai_response(formatted_history, system_instruction=SYSTEM_INSTRUCTION)
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                if vault_data["permissions"].get("voice_reply", True) and not ai_reply.startswith(("🔒", "⚡")):
                    synthesize_boosted_voice(ai_reply)
        st.rerun()

elif current_view == "Voice Mode":
    voice_screen_html = (
        "<div class='hero-wrapper'>"
        "<div class='vortex-container'><div class='vortex-ring-1'></div><di
