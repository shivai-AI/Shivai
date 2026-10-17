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
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE SETUP & SHIVAI UI DESIGN SYSTEM
# ==========================================
st.set_page_config(page_title="ShivAI — Beyond Intelligence", page_icon="⚡", layout="centered")

SHIVAI_UI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* Main App Canvas */
.stApp {
    background-color: #050914;
    background-image: 
        radial-gradient(circle at 50% 15%, rgba(22, 139, 255, 0.15), transparent 60%),
        linear-gradient(rgba(22, 139, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(22, 139, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 30px 30px, 30px 30px;
    color: #F4F7FF;
    font-family: 'Rajdhani', sans-serif;
}

/* Glowing Neural Orb */
.neural-orb-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 20px 0;
}

.neural-orb {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: radial-gradient(circle, #168BFF 0%, #8B5CFF 65%, #050914 100%);
    box-shadow: 0 0 35px #168BFF, inset 0 0 20px #8B5CFF, 0 0 60px rgba(139, 92, 255, 0.5);
    animation: pulse-orb 4s ease-in-out infinite;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 2.5rem;
    font-weight: 900;
    color: #F4F7FF;
}

@keyframes pulse-orb {
    0%, 100% { transform: scale(1); box-shadow: 0 0 30px #168BFF, inset 0 0 15px #8B5CFF; }
    50% { transform: scale(1.06); box-shadow: 0 0 50px #8B5CFF, inset 0 0 25px #168BFF; }
}

/* Glass Cards */
.shiv-card {
    background: #0B1628;
    border: 1px solid rgba(22, 139, 255, 0.25);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    text-align: center;
    transition: all 0.3s ease;
    margin-bottom: 12px;
}

.shiv-card:hover {
    border-color: #168BFF;
    box-shadow: 0 0 20px rgba(22, 139, 255, 0.4);
    transform: translateY(-2px);
}

.card-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #F4F7FF;
    margin-top: 8px;
    margin-bottom: 4px;
}

.card-desc {
    font-size: 0.78rem;
    color: #9AAAC4;
}

/* Header Branding */
.brand-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: 3px;
    color: #F4F7FF;
    text-align: center;
    margin: 0;
}

.brand-sub {
    font-family: 'Rajdhani', sans-serif;
    color: #9AAAC4;
    font-size: 0.95rem;
    letter-spacing: 2px;
    text-align: center;
    text-transform: uppercase;
    margin-bottom: 15px;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #050914 !important;
    border-right: 1px solid rgba(22, 139, 255, 0.2);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #0B1628;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(22, 139, 255, 0.25);
    justify-content: center;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    color: #9AAAC4;
}

.stTabs [aria-selected="true"] {
    color: #F4F7FF !important;
    background: #168BFF !important;
    border-radius: 8px;
    box-shadow: 0 0 15px rgba(22, 139, 255, 0.5);
}

/* Chat Bubbles */
[data-testid="stChatMessage"] {
    background: #0B1628 !important;
    border: 1px solid rgba(22, 139, 255, 0.2);
    border-left: 4px solid #168BFF;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
}

/* Buttons */
.stButton > button {
    font-family: 'Orbitron', sans-serif;
    background: #168BFF;
    color: #F4F7FF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    letter-spacing: 1px;
    box-shadow: 0 0 15px rgba(22, 139, 255, 0.3);
    width: 100%;
}

.stButton > button:hover {
    background: #8B5CFF;
    box-shadow: 0 0 25px rgba(139, 92, 255, 0.6);
}
</style>

<div class="neural-orb-container">
    <div class="neural-orb">S</div>
</div>
<div class="brand-title">ShivAI</div>
<div class="brand-sub">Beyond Intelligence. | Owner: Shivam</div>
"""
st.markdown(SHIVAI_UI_CSS, unsafe_allow_html=True)

# ==========================================
# 2. API & MEMORY SETUP
# ==========================================
API_KEY = st.secrets.get("API_KEY", "").strip()
if not API_KEY:
    st.error("⚠️ CRITICAL: API_KEY missing in Streamlit Secrets, Boss!")
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
    return {"notes": [], "permissions": {"save_memory": True, "voice_reply": True, "web_search": True}}

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
            config = types.GenerateContentConfig(system_instruction=system_prompt)
            res = client.models.generate_content(model=model_name, contents=history_messages, config=config)
            if res and res.text:
                return res.text
        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")
            continue
    return f"⚠️ **GATEWAY ERROR:** `{errors[0] if errors else 'Unknown Error'}`"

# ==========================================
# 4. SIDEBAR NAVIGATION & MENU (Mockup Match)
# ==========================================
with st.sidebar:
    st.markdown("### ⚡ ShivAI Menu")
    menu_choice = st.radio(
        "Navigation",
        ["🏠 Home Dashboard", "💬 AI Chat & Voice", "🔬 Deep Research", "💼 Business (Shivam Tea Traders)", "🛡️ Knowledge Vault & Settings"]
    )

    st.divider()
    st.markdown("### 🌐 Connected Models")
    st.caption("🟢 GPT-4o (Active Proxy)\n🟢 Gemini 2.5 Flash\n🟢 Claude 3.5\n🟢 Llama 3")

    st.divider()
    perm_voice = st.toggle("🔊 Voice Synthesis Reply", value=memory_data["permissions"].get("voice_reply", True))
    perm_memory = st.toggle("🧬 Neural Memory Core", value=memory_data["permissions"].get("save_memory", True))

    memory_data["permissions"]["voice_reply"] = perm_voice
    memory_data["permissions"]["save_memory"] = perm_memory
    save_memory(memory_data)

# ==========================================
# 5. SYSTEM PERSONA
# ==========================================
saved_context = "\n".join([f"- {note}" for note in memory_data["notes"]]) if perm_memory else "No permanent notes."

SYSTEM_PROMPT = f"""
You are ShivAI (Beyond Intelligence), an ultra-intelligent, hyper-loyal personal intelligence system built exclusively by Shivam under Shivam AI Labs.
Your Creator, Owner & Boss: Shivam (address him as "Boss", "Sir", or "Commander Shivam").

CORE PRINCIPLES:
1. **Total Context & Memory Retention:** Remember all previous conversation turns and Knowledge Vault entries.
2. **Proactive Guidance & Mentorship:** Guide Shivam, recall prior goals, and correct any oversights with precision.
3. **Tone:** Futuristic, confident, loyal, witty, and razor-sharp.

Knowledge Vault Context:
{saved_context}
"""

# ==========================================
# 6. MAIN APPLICATION VIEWS
# ==========================================
if menu_choice == "🏠 Home Dashboard":
    st.markdown("### Good Morning, Shivam ☀️")
    st.markdown("<p style='color: #9AAAC4; margin-top: -10px;'>What shall we build today?</p>", unsafe_allow_html=True)

    # Quick Search Bar / Prompt Input
    quick_query = st.text_input("Ask anything...", placeholder="Type or use voice command...")
    if quick_query:
        st.session_state.pending_query = quick_query
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 6 Core Feature Cards (Matching Mockup Grid)[span_4](start_span)[span_4](end_span)[span_5](start_span)[span_5](end_span)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="shiv-card">
            <div style="font-size: 1.5rem;">🔬</div>
            <div class="card-title">Deep Research</div>
            <div class="card-desc">Get real-time info</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Research", key="btn_res"):
            st.rerun()

    with col2:
        st.markdown("""
        <div class="shiv-card">
            <div style="font-size: 1.5rem;">🧠</div>
            <div class="card-title">Think</div>
            <div class="card-desc">Solve complex logic</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Think", key="btn_think"):
            st.rerun()

    with col3:
        st.markdown("""
        <div class="shiv-card">
            <div style="font-size: 1.5rem;">⚡</div>
            <div class="card-title">Create</div>
            <div class="card-desc">Text · Image · Code</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Create", key="btn_create"):
            st.rerun()

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("""
        <div class="shiv-card">
            <div style="font-size: 1.5rem;">🌐</div>
            <div class="card-title">Web Search</div>
            <div class="card-desc">Live internet intelligence</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div class="shiv-card">
            <div style="font-size: 1.5rem;">🤖</div>
            <div class="card-title">AI Models</div>
            <div class="card-desc">GPT · Gemini · Claude</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown("""
        <div class="shiv-card">
            <div style="font-size: 1.5rem;">💼</div>
            <div class="card-title">My Projects</div>
            <div class="card-desc">Shivam Tea Traders</div>
        </div>
        """, unsafe_allow_html=True)

elif menu_choice == "💬 AI Chat & Voice":
    st.subheader("💬 ShivAI Comm-Link & Voice Matrix")

    # Hands-Free Voice Listener Widget ('Hey Shivai')
    voice_html = """
    <div style="background: rgba(22, 139, 255, 0.08); border: 1px solid #168BFF; padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 15px;">
        <p style="color: #168BFF; font-family: 'Orbitron', sans-serif; margin: 0 0 6px 0; font-size: 0.85rem;">🎙️ HANDS-FREE WAKE WORD ACTIVE</p>
        <p style="color: #9AAAC4; font-size: 0.8rem; margin-bottom: 8px;">Say 'Hey Shivai' or 'Wake up Shivai'</p>
        <button id="start-btn" onclick="startListening()" style="background: #168BFF; color: #F4F7FF; border: none; padding: 6px 16px; font-family: 'Orbitron', sans-serif; font-weight: bold; border-radius: 6px; cursor: pointer;">🔴 START MIC</button>
        <p id="transcript-box" style="color: #F4F7FF; font-style: italic; margin-top: 6px; font-size: 0.85rem;"></p>
    </div>
    <script>
    function startListening() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) { alert("Speech recognition not supported"); return; }
        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN';
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = function(event) {
            let transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
            document.getElementById("transcript-box").innerText = "Heard: " + transcript;
            if (transcript.includes("hey shivai") || transcript.includes("wake up shivai") || transcript.includes("shivai")) {
                const inputEl = window.parent.document.querySelector('input[aria-label*="Command"]');
                if (inputEl) {
                    inputEl.value = transcript;
                    inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                    inputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
                }
            }
        };
        recognition.onend = function() { try { recognition.start(); } catch(e) {} };
        recognition.start();
    }
    </script>
    """
    components.html(voice_html, height=145)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "⚡ **All systems online, Boss.** ShivAI is fully synchronized. Bataiye Sir, aaj kya mission hai?"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Command ShivAI, Boss...", key="Command")
    
    # Check if quick query was passed from home
    if "pending_query" in st.session_state and st.session_state.pending_query:
        user_prompt = st.session_state.pending_query
        st.session_state.pending_query = None

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        gemini_history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                gemini_history.append(types.Content(role="user", parts=[types.Part.from_text(text=m["content"])]))
            else:
                gemini_history.append(types.Content(role="model", parts=[types.Part.from_text(text=m["content"])]))

        with st.chat_message("assistant"):
            with st.spinner("⚡ Processing neural intelligence..."):
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

elif menu_choice == "🔬 Deep Research":
    st.subheader("🔬 Deep Research & Intelligence Briefing")
    topic = st.text_input("Research Subject:", value="Wholesale tea market expansion strategy in Ballia, Uttar Pradesh")
    if st.button("🚀 EXECUTE DEEP RESEARCH"):
        with st.spinner("Analyzing market data and generating intelligence report..."):
            reply = ask_shivai([topic], system_prompt=SYSTEM_PROMPT + "\nProvide Executive Summary, Market Dynamics, Competitor Analysis, and Actionable Growth Steps.")
            st.markdown(reply)
            st.download_button("📥 DOWNLOAD DOSSIER", data=reply, file_name="shivai_research_report.md", mime="text/markdown")

elif menu_choice == "💼 Business (Shivam Tea Traders)":
    st.subheader("💼 Shivam Enterprises Workspace")
    module = st.selectbox("Select Business Module:", ["📊 Sales & Revenue", "📦 Inventory & Stock", "🤝 Retailer Outreach", "📈 Growth & Monopoly Strategy"])
    if st.button("⚡ EXECUTE BUSINESS STRATEGY"):
        with st.spinner("Executing business simulation..."):
            reply = ask_shivai([f"Analyze {module} for Shivam Tea Traders in Ballia."], system_prompt=SYSTEM_PROMPT + "\nAct as a top billionaire business strategist. Give crisp, high-ROI execution steps.")
            st.markdown(reply)

elif menu_choice == "🛡️ Knowledge Vault & Settings":
    st.subheader("🛡️ Neural Memory & Knowledge Vault")
    if perm_memory:
        new_directive = st.text_input("Log New Permanent Fact / Directive:")
        if st.button("➕ SAVE TO VAULT") and new_directive:
            memory_data["notes"].append(new_directive)
            save_memory(memory_data)
            st.success("Encrypted in Vault, Boss!")
            st.rerun()

        if memory_data["notes"]:
            st.write("**Secured Directives:**")
            for i, note in enumerate(memory_data["notes"]):
                st.caption(f"🔹 {i+1}. {note}")
            if st.button("🗑️ PURGE VAULT"):
                memory_data["notes"] = []
                save_memory(memory_data)
                st.rerun()
    else:
        st.info("Neural Memory Core is currently disabled in sidebar settings.")
        
