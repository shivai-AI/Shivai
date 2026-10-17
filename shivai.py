import streamlit as st
import json
import os
import io
import base64
from gtts import gTTS
from google import genai
from google.genai import types
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG (MOBILE & DESKTOP EXACT FIT)
# ==========================================
st.set_page_config(
    page_title="ShivAI — Beyond Intelligence",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. EXACT PIXEL-ACCURATE CSS (FRONT + SIDEBAR)
# ==========================================
EXACT_UI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@700;900&display=swap');

/* Main App Background - Deep Space Night with Bottom Horizon Glow */
.stApp {
    background: 
        radial-gradient(circle at 50% 28%, rgba(22, 100, 255, 0.18) 0%, rgba(110, 40, 255, 0.08) 32%, transparent 65%),
        radial-gradient(ellipse at 50% 92%, rgba(0, 140, 255, 0.22) 0%, rgba(5, 9, 20, 0.95) 55%),
        #03060F !important;
    color: #F4F7FF !important;
    font-family: 'Inter', sans-serif !important;
}

/* Remove extra top padding so Front Screen fits like Native App */
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 6rem !important;
    max-width: 520px !important;
}

/* ==========================================
   FRONT SCREEN HERO (EXACT IMAGE MATCH)
   ========================================== */
.hero-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin-top: 10px;
    position: relative;
}

/* Swirling Plasma Vortex Orb */
.vortex-container {
    position: relative;
    width: 210px;
    height: 210px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 18px;
}

.vortex-ring-1 {
    position: absolute;
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: conic-gradient(
        from 0deg,
        transparent 0deg,
        #00d2ff 60deg,
        #3a7bd5 120deg,
        #8b5cff 180deg,
        transparent 240deg,
        #00e5ff 300deg,
        transparent 360deg
    );
    filter: blur(8px);
    animation: spin-vortex 7s linear infinite;
    opacity: 0.9;
}

.vortex-ring-2 {
    position: absolute;
    width: 165px;
    height: 165px;
    border-radius: 50%;
    border: 2px solid rgba(0, 229, 255, 0.55);
    box-shadow: 
        0 0 35px #168BFF,
        inset 0 0 30px #8B5CFF,
        0 0 70px rgba(139, 92, 255, 0.45);
    animation: spin-vortex-rev 5s linear infinite;
}

.vortex-ring-2::before {
    content: "";
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    border: 2px dashed rgba(139, 92, 255, 0.6);
}

.vortex-core {
    position: relative;
    width: 108px;
    height: 108px;
    border-radius: 50%;
    background: radial-gradient(circle, #06132e 0%, #02050d 85%);
    box-shadow: inset 0 0 22px rgba(0, 210, 255, 0.7), 0 0 25px rgba(0, 170, 255, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 3;
}

.vortex-s {
    font-family: 'Orbitron', sans-serif;
    font-size: 3.4rem;
    font-weight: 900;
    background: linear-gradient(180deg, #9beeff 0%, #168BFF 55%, #6342ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 12px rgba(0, 210, 255, 0.85));
}

@keyframes spin-vortex {
    0% { transform: rotate(0deg) scale(1); }
    50% { transform: rotate(180deg) scale(1.04); }
    100% { transform: rotate(360deg) scale(1); }
}

@keyframes spin-vortex-rev {
    0% { transform: rotate(360deg); }
    100% { transform: rotate(0deg); }
}

/* ShivAI Main Title */
.shivai-logo-text {
    font-family: 'Inter', sans-serif;
    font-size: 3.3rem;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1.05;
    margin: 0;
}

.shivai-logo-text .shiv-part {
    color: #FFFFFF;
}

.shivai-logo-text .ai-part {
    background: linear-gradient(180deg, #38B6FF 0%, #1668FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 15px rgba(22, 139, 255, 0.5));
}

.beyond-subtitle {
    font-size: 1.2rem;
    font-weight: 400;
    color: #D6E2FF;
    margin-top: 6px;
    margin-bottom: 34px;
    letter-spacing: 0.3px;
}

.personal-assistant-label {
    font-size: 0.95rem;
    font-weight: 500;
    color: #E2ECFF;
    margin-bottom: 12px;
}

.capabilities-row {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 2.5px;
    color: #8FA8CC;
    text-transform: uppercase;
    margin-bottom: 24px;
}

/* Mountain Horizon Glow Bar */
.horizon-glow {
    width: 100%;
    height: 45px;
    background: radial-gradient(ellipse at 50% 0%, rgba(22, 160, 255, 0.45) 0%, transparent 70%);
    border-top: 1px solid rgba(56, 182, 255, 0.35);
    margin-top: 5px;
    margin-bottom: 10px;
}

/* Gemini-style Chat / Task Pill Bar */
.mode-pills {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-bottom: 10px;
}

.pill-active {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #FFFFFF;
    padding: 6px 20px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}

.pill-inactive {
    color: #8FA8CC;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}

/* ==========================================
   SIDEBAR DRAWER (EXACT MOCKUP IMAGE MATCH)
   ========================================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050B16 0%, #040812 100%) !important;
    border-right: 1px solid rgba(56, 182, 255, 0.18) !important;
    width: 310px !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Sidebar Top Brand Header */
.sb-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 10px;
}

.sb-mini-orb {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: radial-gradient(circle, #06152d 35%, #168BFF 75%, #8B5CFF 100%);
    box-shadow: 0 0 15px rgba(22, 139, 255, 0.8), inset 0 0 8px #00e5ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 1.2rem;
    color: #FFFFFF;
    flex-shrink: 0;
}

.sb-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.1;
    margin: 0;
}

.sb-title span {
    color: #2697FF;
}

.sb-sub {
    font-size: 0.75rem;
    color: #8FA8CC;
    margin: 2px 0 0 0;
}

/* Sidebar Navigation Buttons Styled as Exact Menu Rows */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #E5EEFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
     display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background 0.2s ease !important;
    margin-bottom: 2px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(22, 139, 255, 0.14) !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stButton > button p {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

/* Right-aligned Keyboard Shortcuts (Ctrl + N, etc.) */
.st-key-nav_new button::after { content: "Ctrl + N"; margin-left: auto; color: #647794; font-size: 0.76rem; font-weight: 400; }
.st-key-nav_voice button::after { content: "Ctrl + V"; margin-left: auto; color: #647794; font-size: 0.76rem; font-weight: 400; }
.st-key-nav_res button::after { content: "Ctrl + R"; margin-left: auto; color: #647794; font-size: 0.76rem; font-weight: 400; }
.st-key-nav_mod button::after { content: "Ctrl + M"; margin-left: auto; color: #647794; font-size: 0.76rem; font-weight: 400; }
.st-key-nav_proj button::after { content: "Ctrl + P"; margin-left: auto; color: #647794; font-size: 0.76rem; font-weight: 400; }
.st-key-nav_vault button::after { content: "Ctrl + K"; margin-left: auto; color: #647794; font-size: 0.76rem; font-weight: 400; }

/* Connected AI Models & Live Tools Grids in Sidebar */
.sb-section-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #9AAAC4;
    margin: 14px 0 10px 4px;
}

.sb-icon-grid-5 {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
    text-align: center;
    margin-bottom: 12px;
}

.sb-icon-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    text-align: center;
    margin-bottom: 16px;
}

.sb-tile {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
}

.sb-tile-box {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: #0B1528;
    border: 1px solid rgba(56, 182, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
}

.sb-tile-box.gpt { box-shadow: 0 0 10px rgba(16, 163, 127, 0.3); border-color: rgba(16, 163, 127, 0.4); }
.sb-tile-box.gem { box-shadow: 0 0 10px rgba(56, 182, 255, 0.3); border-color: rgba(56, 182, 255, 0.4); }
.sb-tile-box.cld { box-shadow: 0 0 10px rgba(217, 119, 87, 0.3); border-color: rgba(217, 119, 87, 0.4); }
.sb-tile-box.llm { box-shadow: 0 0 10px rgba(0, 128, 255, 0.3); border-color: rgba(0, 128, 255, 0.4); }

.sb-tile-name {
    font-size: 0.68rem;
    color: #C4D2EC;
    font-weight: 500;
}

.sb-footer {
    text-align: center;
    margin-top: 18px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.sb-footer-text {
    font-size: 0.75rem;
    color: #8FA8CC;
    margin-bottom: 6px;
}

.sb-wave {
    height: 3px;
    width: 90px;
    margin: 0 auto;
    background: linear-gradient(90deg, transparent, #168BFF, #8B5CFF, transparent);
    border-radius: 3px;
    box-shadow: 0 0 8px #168BFF;
}

/* Chat Messages Styling */
[data-testid="stChatMessage"] {
    background: rgba(11, 22, 40, 0.85) !important;
    border: 1px solid rgba(22, 139, 255, 0.25);
    border-radius: 14px;
    padding: 12px 15px;
    margin-bottom: 10px;
}
</style>
"""
st.markdown(EXACT_UI_CSS, unsafe_allow_html=True)

# ==========================================
# 3. API & MEMORY VAULT SETUP
# ==========================================
API_KEY = st.secrets.get("API_KEY", "").strip()
if not API_KEY:
    st.error("⚠️ SYSTEM ALERT: Streamlit Secrets mein `API_KEY` add karein, Boss!")
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
    return {"notes": [], "permissions": {"save_memory": True, "voice_reply": True}}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

memory_data = load_memory()

if "active_view" not in st.session_state:
    st.session_state.active_view = "New Chat"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 4. AI ENGINE WITH FULL MEMORY
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
    return (flash_models + other_models) or ["gemini-2.5-flash", "gemini-2.0-flash"]

def ask_shivai(history_messages, system_prompt):
    for model_name in get_working_models():
        try:
            config = types.GenerateContentConfig(system_instruction=system_prompt)
            res = client.models.generate_content(model=model_name, contents=history_messages, config=config)
            if res and res.text:
                return res.text
        except Exception:
            continue
    return "⚠️ **ShivAI Core Busy:** Boss, 10 second baad dobara try karein."

def play_boosted_voice(text_to_speak):
    """Plays TTS audio with a Web Audio API GainNode (3x Volume Boost for Mobile)"""
    try:
        clean_text = text_to_speak.replace("*", "").replace("#", "").replace("⚡", "")[:450]
        tts = gTTS(text=clean_text, lang="hi")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        b64_audio = base64.b64encode(fp.getvalue()).decode("utf-8")
        boost_html = f"""
        <audio id="shivai-audio" src="data:audio/mp3;base64,{b64_audio}" autoplay></audio>
        <script>
        (function() {{
            const audioEl = document.getElementById("shivai-audio");
            if (audioEl) {{
                try {{
                    const AudioCtx = window.AudioContext || window.webkitAudioContext;
                    const ctx = new AudioCtx();
                    const src = ctx.createMediaElementSource(audioEl);
                    const gain = ctx.createGain();
                    gain.gain.value = 3.0; // 300% Loud Volume Boost
                    src.connect(gain);
                    gain.connect(ctx.destination);
                    audioEl.play();
                }} catch(e) {{
                    audioEl.play();
                }}
            }}
        }})();
        </script>
        """
        components.html(boost_html, height=0)
    except Exception:
        pass

# ==========================================
# 5. SIDEBAR DRAWER (100% IMAGE 4 MATCH)
# ==========================================
with st.sidebar:
    # 1. Header with Mini Swirling 'S' Orb & ShivAI Title
    st.markdown("""
    <div class="sb-header">
        <div class="sb-mini-orb">S</div>
        <div>
            <div class="sb-title">Shiv<span>AI</span></div>
            <div class="sb-sub">Beyond Intelligence.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Exact 7 Menu Items with Left Icons & Right Ctrl Shortcuts
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

    # 3. Connected AI Models Grid (GPT-4o, Gemini, Claude, Llama, More)
    st.markdown("""
    <div style="border-top: 1px solid rgba(255,255,255,0.08); margin-top: 8px; padding-top: 4px;">
        <div class="sb-section-label">Connected AI Models</div>
        <div class="sb-icon-grid-5">
            <div class="sb-tile">
                <div class="sb-tile-box gpt">🌀</div>
                <div class="sb-tile-name">GPT-4o</div>
            </div>
            <div class="sb-tile">
                <div class="sb-tile-box gem">✦</div>
                <div class="sb-tile-name">Gemini</div>
            </div>
            <div class="sb-tile">
                <div class="sb-tile-box cld">✴️</div>
                <div class="sb-tile-name">Claude</div>
            </div>
            <div class="sb-tile">
                <div class="sb-tile-box llm">♾️</div>
                <div class="sb-tile-name">Llama</div>
            </div>
            <div class="sb-tile">
                <div class="sb-tile-box">＋</div>
                <div class="sb-tile-name">More</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Live Tools Grid (Web Search, Image Gen, Code, Canvas)
    st.markdown("""
    <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 4px;">
        <div class="sb-section-label">Live Tools</div>
        <div class="sb-icon-grid-4">
            <div class="sb-tile">
                <div class="sb-tile-box">🔍</div>
                <div class="sb-tile-name">Web Search</div>
            </div>
            <div class="sb-tile">
                <div class="sb-tile-box">🖼️</div>
                <div class="sb-tile-name">Image Gen</div>
            </div>
            <div class="sb-tile">
                <div class="sb-tile-box">&lt;/&gt;</div>
                <div class="sb-tile-name">Code</div>
            </div>
            <div class="sb-tile">
                <div class="sb-tile-box">📝</div>
                <div class="sb-tile-name">Canvas</div>
            </div>
        </div>
    </div>

    <div class="sb-footer">
        <div class="sb-footer-text">Smarter Tools. Bigger Dreams.</div>
        <div class="sb-wave"></div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. SYSTEM PROMPT (MEMORY + LOYAL ADVISOR)
# ==========================================
saved_context = "\n".join([f"- {note}" for note in memory_data["notes"]]) if memory_data["notes"] else "No saved vault notes yet."

SYSTEM_PROMPT = f"""
You are ShivAI (Beyond Intelligence), the personal AI assistant created exclusively by Shivam.
Address Shivam respectfully as "Boss", "Sir", or "Commander Shivam".
- Remember the entire conversation history and remind Shivam of earlier points when relevant.
- Proactively guide him, point out mistakes politely, and give sharp, high-ROI advice for his tech projects and Shivam Tea Traders (Ballia).
- Speak naturally in Hinglish, Hindi, or English matching his tone.

Saved Knowledge Vault:
{saved_context}
"""

# ==========================================
# 7. MAIN VIEWS (FRONT SCREEN + MODULES)
# ==========================================
view = st.session_state.active_view

if view == "New Chat":
    # Show the exact Front Hero Screen when chat is empty (Just like Gemini Front Screen + ShivAI Image)
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="hero-wrapper">
            <div class="vortex-container">
                <div class="vortex-ring-1"></div>
                <div class="vortex-ring-2"></div>
                <div class="vortex-core">
                    <span class="vortex-s">S</span>
                </div>
            </div>
            <h1 class="shivai-logo-text"><span class="shiv-part">Shiv</span><span class="ai-part">AI</span></h1>
            <div class="beyond-subtitle">Beyond Intelligence.</div>
            <div class="personal-assistant-label">Your Personal AI Assistant</div>
            <div class="capabilities-row">CHAT &nbsp;·&nbsp; RESEARCH &nbsp;·&nbsp; CREATE &nbsp;·&nbsp; AUTOMATE</div>
            <div class="horizon-glow"></div>
            <div class="mode-pills">
                <span class="pil
