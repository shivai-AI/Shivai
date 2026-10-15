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
# 1. PAGE SETUP & SHIVAM HUD CSS
# ==========================================
st.set_page_config(page_title="SHIVAI | SHIVAM AI LABS", page_icon="⚡", layout="wide")

SHIVAI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* Main Background - Dark Cyber Grid */
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

/* HUD Header */
.hud-container {
    border: 1px solid rgba(0, 229, 255, 0.4);
    background: linear-gradient(135deg, rgba(5, 18, 36, 0.85) 0%, rgba(2, 8, 20, 0.9) 100%);
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.2), inset 0 0 15px rgba(0, 229, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}

.hud-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 5px;
    color: #00e5ff;
    text-shadow: 0 0 12px rgba(0, 229, 255, 0.8), 0 0 25px rgba(0, 229, 255, 0.4);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 15px;
}

/* Spinning Reactor Ring */
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

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #040d1a !important;
    border-right: 1px solid rgba(0, 229, 255, 0.35);
    box-shadow: 5px 0 20px rgba(0, 229, 255, 0.1);
}

/* Tabs Styling */
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
    letter-spacing: 1px;
}

.stTabs [aria-selected="true"] {
    color: #00e5ff !important;
    background: rgba(0, 229, 255, 0.12) !important;
    border-radius: 6px;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.25);
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background: rgba(6, 20, 39, 0.75) !important;
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-left: 4px solid #00e5ff;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    padding: 12px;
    margin-bottom: 12px;
}

/* Buttons */
.stButton > button {
    font-family: 'Orbitron', sans-serif;
    background: linear-gradient(90deg, rgba(0, 229, 255, 0.15), rgba(0, 119, 255, 0.25));
    color: #00e5ff;
    border: 1px solid #00e5ff;
    border-radius: 6px;
    letter-spacing: 1.5px;
    transition: all 0.3s ease;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
}

.stButton > button:hover {
    background: #00e5ff;
    color: #030712;
    box-shadow: 0 0 20px #00e5ff;
    transform: translateY(-1px);
}
</style>

<div class="hud-container">
    <div class="hud-title">
        <span class="arc-reactor"></span>
        S.H.I.V.A.I.
    </div>
    <div class="hud-sub">⚡ SHIVAM AI LABS | COMMANDER: SHIVAM</div>
    <div class="hud-sub" style="font-size: 0.85rem; color: #00e5ff; margin-top: 2px;">SHIVAM ENTERPRISES NEURAL MATRIX | OWNER: SHIVAM</div>
    <div class="hud-sub" style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">SHIVAM CORE SYSTEMS | OPERATOR: SHIVAM</div>
    
    <div class="hud-metrics">
        <div class="metric-pill">🟢 CORE: ONLINE (SHIVAI-X1)</div>
        <div class="metric-pill">🛡️ SECURITY: SHIVAM-LOCK ACTIVE</div>
        <div class="metric-pill">🎙️ VOICE RELAY: READY</div>
        <div class="metric-pill">⚡ POWER: 400% CAPACITY</div>
    </div>
</div>
"""
st.markdown(SHIVAI_CSS, unsafe_allow_html=True)

# ==========================================
# 2. API & MEMORY SETUP
# ==========================================
API_KEY = st.secrets.get("API_KEY", "").strip()

if not API_KEY or API_KEY == "YAHAN_APNI_GEMINI_API_KEY_DAALEIN":
    st.error("⚠️ SYSTEM ALERT: Neural Core API_KEY missing in Streamlit Secrets, Boss!")
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
# 3. AUTO-DETECT MODEL ENGINE (CRASH PROOF)
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

def ask_shivai(contents, system_prompt=None, use_search=False):
    models_to_try = get_working_models()
    errors = []
    
    for model_name in models_to_try:
        try:
            tools = [{"google_search": {}}] if use_search else None
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=tools
            )
            res = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            if res and res.text:
                return res.text
        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")
            if use_search:
                try:
                    config_no_search = types.GenerateContentConfig(system_instruction=system_prompt)
                    res = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config_no_search
                    )
                    if res and res.text:
                        return res.text
                except Exception:
                    pass
            continue
            
    if any("429" in err or "RESOURCE_EXHAUSTED" in err for err in errors):
        return "⚠️ **SHIVAI SERVER ALERT (429):** Boss, aapki API Key ka free quota abhi full ho gaya hai. 30 second wait karein."
        
    return f"⚠️ **HUD TRANSMISSION ERROR:** `{errors[0] if errors else 'Unknown Error'}`"

# ==========================================
# 4. SIDEBAR: SHIVAI CONTROL DECK
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ SHIVAI NEURAL ROUTER")
    brain_mode = st.selectbox(
        "Select Intelligence Protocol:",
        [
            "⚡ SHIVAI Tactical & Live Recon (All-Rounder)",
            "🧠 X1 Deep Logic & Strategy (Reasoning)",
            "💻 Shivam Cybernetics & Code Forge (Coding)",
            "🛰️ Global Satellite Deep Research (Report)",
            "💼 Shivam Enterprises Boardroom Advisor (Business)"
        ]
    )

    st.divider()
    st.markdown("### 🛡️ SECURITY PROTOCOLS")
    perm_search = st.toggle("🛰️ Satellite Uplink (Live Web Search)", value=False)
    perm_voice = st.toggle("🔊 SHIVAI Voice Synthesis", value=memory_data["permissions"].get("voice_reply", True))
    perm_memory = st.toggle("🧬 Neural Memory Core", value=memory_data["permissions"].get("save_memory", True))

    memory_data["permissions"] = {
        "web_search": perm_search,
        "voice_reply": perm_voice,
        "save_memory": perm_memory
    }
    save_memory(memory_data)

    st.divider()
    st.markdown("### 🗄️ SHIVAM'S CLASSIFIED VAULT")
    if perm_memory:
        new_note = st.text_input("Log New Directive / Goal:")
        if st.button("➕ ENCRYPT & SAVE") and new_note:
            memory_data["notes"].append(new_note)
            save_memory(memory_data)
            st.success("Directive Encrypted in Vault, Boss!")
            st.rerun()

        if memory_data["notes"]:
            st.write("**Active Directives:**")
            for i, note in enumerate(memory_data["notes"]):
                st.caption(f"🔹 {i+1}. {note}")
            if st.button("🗑️ PURGE MEMORY CORE"):
                memory_data["notes"] = []
                save_memory(memory_data)
                st.rerun()
    else:
        st.info("🔒 Neural Memory Core is offline, Boss.")

# ==========================================
# 5. SHIVAI SYSTEM PERSONA
# ==========================================
mode_instructions = {
    "⚡ SHIVAI Tactical & Live Recon (All-Rounder)": "Act as Shivam's personal ultra-intelligent, witty, and loyal AI assistant.",
    "🧠 X1 Deep Logic & Strategy (Reasoning)": "Run deep tactical simulations and step-by-step first-principles calculations.",
    "💻 Shivam Cybernetics & Code Forge (Coding)": "Write futuristic, clean, bug-free production code for Shivam AI Labs.",
    "🛰️ Global Satellite Deep Research (Report)": "Provide high-level intelligence briefings with Executive Summary, Tactical Data, and Actionable Insights.",
    "💼 Shivam Enterprises Boardroom Advisor (Business)": "Advise Shivam like a top billionaire strategist—focus on ROI, scale, monopoly, and smart execution."
}

saved_context = json.dumps(memory_data["notes"], ensure_ascii=False) if perm_memory else "Offline."

SYSTEM_PROMPT = f"""
Identity:
- You are S.H.I.V.A.I. (Shivam's Intelligent Virtual AI), built exclusively by Shivam under Shivam AI Labs & Shivam Enterprises.
- Your Creator, Owner & Commander: Shivam (address him respectfully as "Boss", "Sir", or "Commander Shivam").
- Tone: Cool, futuristic, confident, loyal, crisp, and hyper-intelligent.
- Language: Natural Hinglish, Hindi, or English (match Shivam's style).

Active Protocol: {brain_mode}
Directive: {mode_instructions[brain_mode]}

Classified Vault Memory:
{saved_context}
"""

# ==========================================
# 6. HUD WORKSPACE TABS
# ==========================================
tab_chat, tab_files, tab_auto = st.tabs([
    "⚡ HOLOGRAM COMM-LINK", 
    "🔬 SHIVAI LAB SCANNER", 
    "🤖 AUTONOMOUS LEGION"
])

# --- TAB 1: HOLOGRAM CHAT & VOICE ---
with tab_chat:
    audio_value = st.audio_input("🎙️ VOICE COMMAND UPLINK ('Wake up SHIVAI...'):")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "⚡ **All systems online, Boss.** Shivam Neural Matrix at 100% capacity. **S.H.I.V.A.I. X1** interface is ready for Shivam AI Labs. Bataiye Sir, aaj kya mission hai?"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Enter command for SHIVAI, Boss...")

    active_contents = None
    display_text = None

    if user_prompt:
        display_text = user_prompt
        active_contents = [user_prompt]
    elif audio_value is not None:
        audio_bytes = audio_value.read()
        if "last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes:
            st.session_state.last_audio = audio_bytes
            display_text = "🎙️ *[Encrypted Voice Transmission Sent]*"
            active_contents = [
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                "Sun kar samjho ki Commander Shivam ne kya command di hai aur satik jawab do."
            ]

    if active_contents:
        st.session_state.messages.append({"role": "user", "content": display_text})
        with st.chat_message("user"):
            st.markdown(display_text)

        with st.chat_message("assistant"):
            with st.spinner("⚡ Scanning Shivam Core Systems..."):
                reply = ask_shivai(active_contents, system_prompt=SYSTEM_PROMPT, use_search=perm_search)
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

# --- TAB 2: SHIVAI LAB SCANNER (FILES) ---
with tab_files:
    st.subheader("🔬 Upload Schematics, Data Logs, or Visuals for HUD Scan")
    uploaded_file = st.file_uploader("Drop classified file here", type=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"])
    file_question = st.text_input("Specify Scan Parameters:", value="Run a full diagnostic and tactical summary on this file, Boss.")

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()

        if file_ext in ["csv", "xlsx"]:
            df = pd.read_csv(uploaded_file) if file_ext == "csv" else pd.read_excel(uploaded_file)
            st.write("### 📊 Telemetry Matrix Preview:")
            st.dataframe(df.head(10))
            if st.button("⚡ RUN SHIVAM TELEMETRY SCAN"):
                with st.spinner("Analyzing data matrix..."):
                    data_summary = f"Columns: {list(df.columns)}\nSample:\n{df.head(15).to_string()}\nStats:\n{df.describe().to_string()}"
                    reply = ask_shivai(f"{file_question}\n\nData:\n{data_summary}", system_prompt=SYSTEM_PROMPT)
                    st.markdown(reply)

        elif file_ext in ["png", "jpg", "jpeg"]:
            img = Image.open(uploaded_file)
            st.image(img, caption="Target Visual Locked", width=350)
            if st.button("⚡ INITIATE VISUAL OPTIC SCAN"):
                with st.spinner("Scanning visual target..."):
                    reply = ask_shivai([img, file_question], system_prompt=SYSTEM_PROMPT)
                    st.markdown(reply)

        elif file_ext == "pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() or "" for page in reader.pages[:15]])
            st.success(f"Schematic Loaded ({len(reader.pages)} pages)")
            if st.button("⚡ DECRYPT & ANALYSE DOCUMENT"):
                with st.spinner("Decrypting PDF schematics..."):
                    reply = ask_shivai(f"{file_question}\n\nContent:\n{pdf_text[:20000]}", system_prompt=SYSTEM_PROMPT)
                    st.markdown(reply)

# --- TAB 3: AUTONOMOUS LEGION ---
with tab_auto:
    st.subheader("🤖 SHIVAI Autonomous Protocol")
    task_type = st.selectbox("Select Legion Protocol:", [
        "📝 Generate Classified Intelligence Dossier (.md)",
        "💻 Forge SHIVAI Automation Script (.py)",
        "📅 Deploy Strategic Masterplan"
    ])
    task_detail = st.text_area("Enter Mission Parameters:")
    confirm_permission = st.checkbox("✅ Authorize SHIVAI with Commander Shivam's Override Code.")

    if st.button("🚀 DEPLOY SHIVAI LEGION"):
        if not confirm_permission:
            st.error("⚠️ ACCESS DENIED! Commander authorization checkbox required, Boss.")
        elif not task_detail:
            st.warning("Boss, please enter the mission parameters first.")
        else:
            with st.spinner("Deploying SHIVAI Legion protocol..."):
                reply = ask_shivai(f"Protocol: {task_type}\nMission Details: {task_detail}\nExecute for Commander Shivam.", system_prompt=SYSTEM_PROMPT)
                st.success("✅ Mission Accomplished, Boss!")
                st.markdown(reply)
                st.download_button("📥 DOWNLOAD CLASSIFIED DOSSIER", data=reply, file_name="shivai_dossier.md", mime="text/markdown")
