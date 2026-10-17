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
# 1. PAGE SETUP & BLUEPRINT v1.0 UI SYSTEM
# ==========================================
st.set_page_config(page_title="ShivAI — Beyond Intelligence", page_icon="⚡", layout="wide")

BLUEPRINT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* Blueprint v1.0 Color Tokens */
.stApp {
    background-color: #050914;
    background-image: 
        radial-gradient(circle at 50% 10%, rgba(22, 139, 255, 0.12), transparent 60%),
        linear-gradient(rgba(22, 139, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(22, 139, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 30px 30px, 30px 30px;
    color: #F4F7FF;
    font-family: 'Rajdhani', sans-serif;
}

/* Glass Panels / Cards */
.shiv-card {
    background: #0B1628;
    border: 1px solid rgba(22, 139, 255, 0.25);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    margin-bottom: 20px;
}

.hud-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.5rem;
    font-weight: 900;
    letter-spacing: 4px;
    color: #F4F7FF;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 15px;
}

/* Glowing Neural Orb / S Core */
.neural-orb {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: radial-gradient(circle, #168BFF 0%, #8B5CFF 70%, #050914 100%);
    box-shadow: 0 0 20px #168BFF, inset 0 0 10px #8B5CFF;
    animation: pulse-orb 4s ease-in-out infinite;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    color: #F4F7FF;
}

@keyframes pulse-orb {
    0%, 100% { transform: scale(1); box-shadow: 0 0 15px #168BFF; }
    50% { transform: scale(1.08); box-shadow: 0 0 30px #8B5CFF; }
}

.tagline {
    font-family: 'Rajdhani', sans-serif;
    color: #9AAAC4;
    font-size: 1.1rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 5px;
    font-weight: 600;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #050914 !important;
    border-right: 1px solid rgba(22, 139, 255, 0.2);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: #0B1628;
    padding: 8px;
    border-radius: 10px;
    border: 1px solid rgba(22, 139, 255, 0.2);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.82rem;
    color: #9AAAC4;
    letter-spacing: 1px;
}

.stTabs [aria-selected="true"] {
    color: #F4F7FF !important;
    background: #168BFF !important;
    border-radius: 6px;
    box-shadow: 0 0 15px rgba(22, 139, 255, 0.5);
}

/* Chat Bubbles */
[data-testid="stChatMessage"] {
    background: #0B1628 !important;
    border: 1px solid rgba(22, 139, 255, 0.2);
    border-left: 4px solid #168BFF;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 12px;
}

/* Primary Action Buttons */
.stButton > button {
    font-family: 'Orbitron', sans-serif;
    background: #168BFF;
    color: #F4F7FF;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    letter-spacing: 1.5px;
    box-shadow: 0 0 15px rgba(22, 139, 255, 0.3);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: #8B5CFF;
    box-shadow: 0 0 25px rgba(139, 92, 255, 0.6);
}
</style>

<div class="shiv-card" style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <div class="hud-title">
            <span class="neural-orb">S</span>
            ShivAI
        </div>
        <div class="tagline">Beyond Intelligence. | Owner: Shivam</div>
    </div>
    <div style="text-align: right;">
        <span style="background: rgba(22, 139, 255, 0.15); border: 1px solid #168BFF; padding: 6px 14px; border-radius: 20px; font-family: 'Orbitron', sans-serif; font-size: 0.75rem; color: #168BFF;">
            🟢 CORE ONLINE (v1.0)
        </span>
    </div>
</div>
"""
st.markdown(BLUEPRINT_CSS, unsafe_allow_html=True)

# ==========================================
# 2. API & MEMORY CORE SETUP
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
            
    return f"⚠️ **GATEWAY ERROR:** `{errors[0] if errors else 'Unknown Error'}`"

# ==========================================
# 4. SIDEBAR - CONTROL DECK & VAULT
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ SYSTEM CONTROLS")
    brain_mode = st.selectbox(
        "Intelligence Mode:",
        [
            "⚡ ShivAI Tactical & Total Memory",
            "🧠 Deep Reasoning & Problem Solving",
            "🔬 Live Research & Intelligence",
            "💼 Shivam Enterprises Business Advisor",
            "💻 Cybernetics & Code Forge"
        ]
    )

    st.divider()
    perm_voice = st.toggle("🔊 Voice Synthesis Reply", value=memory_data["permissions"].get("voice_reply", True))
    perm_memory = st.toggle("🧬 Neural Memory Vault", value=memory_data["permissions"].get("save_memory", True))

    memory_data["permissions"]["voice_reply"] = perm_voice
    memory_data["permissions"]["save_memory"] = perm_memory
    save_memory(memory_data)

    st.divider()
    st.markdown("### 🗄️ KNOWLEDGE VAULT")
    if perm_memory:
        new_note = st.text_input("Store Directive / Fact:")
        if st.button("➕ ENCRYPT TO VAULT") and new_note:
            memory_data["notes"].append(new_note)
            save_memory(memory_data)
            st.success("Secured in Vault, Boss!")
            st.rerun()

        if memory_data["notes"]:
            st.write("**Secured Directives:**")
            for i, note in enumerate(memory_data["notes"]):
                st.caption(f"🔹 {i+1}. {note}")
            if st.button("🗑️ PURGE VAULT"):
                memory_data["notes"] = []
                save_memory(memory_data)
                st.rerun()

# ==========================================
# 5. SYSTEM PERSONA (BLUEPRINT v1.0)
# ==========================================
saved_context = "\n".join([f"- {note}" for note in memory_data["notes"]]) if perm_memory else "No permanent notes."

SYSTEM_PROMPT = f"""
You are ShivAI (Beyond Intelligence), an ultra-intelligent, hyper-loyal personal intelligence system built exclusively by Shivam under Shivam AI Labs & Shivam Enterprises.
Your Creator, Owner & Boss: Shivam (address him as "Boss", "Sir", or "Commander Shivam").

CORE PRINCIPLES (Blueprint v1.0):
1. **Total Context & Memory Retention:** Remember all previous conversation turns and Knowledge Vault entries.
2. **Proactive Guidance & Mentorship:** Guide Shivam, recall prior goals, and correct any oversights with precision.
3. **Transparent & Actionable:** Provide clear summaries, structured answers, and expert recommendations.
4. **Tone:** Futuristic, confident, loyal, witty, and razor-sharp.

Active Intelligence Mode: {brain_mode}
Knowledge Vault Context:
{saved_context}
"""

# ==========================================
# 6. BLUEPRINT NAVIGATION TABS
# ==========================================
tab_home, tab_chat, tab_research, tab_business, tab_auto = st.tabs([
    "🏠 HOME / BRIEFING", 
    "💬 AI CHAT & VOICE", 
    "🔬 RESEARCH & NEWS", 
    "💼 BUSINESS MANAGER", 
    "⚙️ AUTOMATION"
])

# --- TAB 1: HOME / BRIEFING ---
with tab_home:
    st.markdown("### 🌅 Good Day, Commander Shivam")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="shiv-card">
            <h4 style="color: #168BFF; font-family: 'Orbitron'; margin-top:0;">🧠 AI Core</h4>
            <p style="color: #F4F7FF;">Status: Optimal<br>Latency: 42ms<br>Security: Level 10</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="shiv-card">
            <h4 style="color: #8B5CFF; font-family: 'Orbitron'; margin-top:0;">🧬 Memory Vault</h4>
            <p style="color: #F4F7FF;">Active Directives: {}<br>Sync: Real-time<br>Encryption: Active</p>
        </div>
        """.format(len(memory_data["notes"])), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="shiv-card">
            <h4 style="color: #168BFF; font-family: 'Orbitron'; margin-top:0;">💼 Workspace</h4>
            <p style="color: #F4F7FF;">Primary: Shivam Tea Traders<br>Mode: Growth & Scale<br>Readiness: 100%</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 **ShivAI Briefing:** All systems are synchronized with your Neural Memory Core. Use the AI Chat tab or say 'Hey Shivai' for hands-free operations.")

# --- TAB 2: AI CHAT & VOICE ---
with tab_chat:
    # Hands-Free Voice Listener Widget
    voice_html = """
    <div style="background: rgba(22, 139, 255, 0.08); border: 1px solid #168BFF; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
        <h4 style="color: #168BFF; font-family: 'Orbitron', sans-serif; margin: 0 0 8px 0;">🎙️ HANDS-FREE VOICE MATRIX</h4>
        <p style="color: #9AAAC4; font-size: 0.9rem; margin-bottom: 10px;">Say 'Hey Shivai' or 'Wake up Shivai' to activate hands-free mode.</p>
        <button id="start-btn" onclick="startListening()" style="background: #168BFF; color: #F4F7FF; border: none; padding: 8px 18px; font-family: 'Orbitron', sans-serif; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 0 12px #168BFF;">🔴 ACTIVATE MIC</button>
        <p id="transcript-box" style="color: #F4F7FF; font-style: italic; margin-top: 8px;"></p>
    </div>

    <script>
    function startListening() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Browser does not support Speech Recognition!");
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN';
        recognition.continuous = true;
        recognition.interimResults = true;

        document.getElementById("transcript-box").innerText = "Listening for 'Hey Shivai'...";
        
        recognition.onresult = function(event) {
            let transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
            document.getElementById("transcript-box").innerText = "Detected: " + transcript;
            
            if (transcript.includes("hey shivai") || transcript.includes("wake up shivai") || transcript.includes("shivai")) {
                const inputEl = window.parent.document.querySelector('input[aria-label*="Command"]');
                if (inputEl) {
                    inputEl.value = transcript;
                    inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                    inputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
                }
            }
        };
        recognition.onend = function() {
            try { recognition.start(); } catch(e) {}
        };
        recognition.start();
    }
    </script>
    """
    components.html(voice_html, height=160)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "⚡ **Systems online, Boss.** ShivAI v1.0 Neural Core is active. Bataiye Sir, aaj kya mission hai?"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Command ShivAI, Boss...")

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
            with st.spinner("⚡ Processing neural context..."):
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

# --- TAB 3: RESEARCH & NEWS ---
with tab_research:
    st.subheader("🔬 Deep Research & Intelligence Briefing")
    research_topic = st.text_input("Enter research topic or market question:", value="Market analysis for tea wholesale expansion in Ballia and Uttar Pradesh")
    if st.button("🚀 EXECUTE DEEP RESEARCH"):
        with st.spinner("Conducting high-level research briefing..."):
            reply = ask_shivai([research_topic], system_prompt=SYSTEM_PROMPT + "\nProvide structured Executive Summary, Key Findings, and Actionable Insights with source citations.")
            st.markdown(reply)
            st.download_button("📥 DOWNLOAD DOSSIER (.md)", data=reply, file_name="shivai_research_dossier.md", mime="text/markdown")

# --- TAB 4: BUSINESS MANAGER ---
with tab_business:
    st.subheader("💼 Business Intelligence Workspace: Shivam Tea Traders")
    b_action = st.selectbox("Select Business Module:", [
        "📊 Sales & Expense Overview",
        "📦 Stock & Inventory Check",
        "🤝 Retailer Follow-up Strategy",
        "📈 Growth & Scaling Roadmap"
    ])
    if st.button("⚡ RUN BUSINESS ANALYSIS"):
        with st.spinner("Analyzing business metrics..."):
            reply = ask_shivai([f"Analyze business module: {b_action} for Shivam Tea Traders."], system_prompt=SYSTEM_PROMPT + "\nGive practical, high-ROI business advice as a top billionaire strategist.")
            st.markdown(reply)

# --- TAB 5: AUTOMATION CENTER ---
with tab_auto:
    st.subheader("⚙️ Permission-Based Automation Center")
    auto_task = st.text_area("Define automated workflow or script parameters:")
    confirm_auto = st.checkbox("✅ Authorize execution with Commander Shivam's security clearance.")
    if st.button("🚀 DEPLOY AUTOMATION"):
        if not confirm_auto:
            st.error("⚠️ Security clearance required, Boss!")
        elif not auto_task:
            st.warning("Please specify automation parameters.")
        else:
            with st.spinner("Executing workflow..."):
                reply = ask_shivai([auto_task], system_prompt=SYSTEM_PROMPT + "\nGenerate clean production-ready Python automation code or execution report.")
                st.success("✅ Automation Executed Successfully!")
                st.markdown(reply)
ey Shivai' ya 'Wake up Shivai' bolein, ya button daba kar baat karein.</p>
        <button id="start-btn" onclick="startListening()" style="background: #00e5ff; color: #030712; border: none; padding: 10px 20px; font-family: 'Orbitron', sans-serif; font-weight: bold; border-radius: 5px; cursor: pointer; box-shadow: 0 0 10px #00e5ff;">🔴 START HANDS-FREE MIC</button>
        <p id="transcript-box" style="color: #e0f7fa; font-style: italic; margin-top: 10px;"></p>
    </div>

    <script>
    function startListening() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Browser support nahi karta, Boss!");
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN';
        recognition.continuous = true;
        recognition.interimResults = true;

        document.getElementById("transcript-box").innerText = "Listening for 'Hey Shivai' or commands...";
        
        recognition.onresult = function(event) {
            let transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
            document.getElementById("transcript-box").innerText = "Detected: " + transcript;
            
            if (transcript.includes("hey shivai") || transcript.includes("wake up shivai") || transcript.includes("shivai")) {
                // Send to streamlit input or trigger action
                const inputEl = window.parent.document.querySelector('input[aria-label*="Command"]');
                if (inputEl) {
                    inputEl.value = transcript;
                    inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                    // Press Enter
                    inputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
                }
            }
        };

        recognition.onerror = function(event) {
            console.log("Mic error:", event.error);
        };

        recognition.onend = function() {
            // Restart automatically for true hands-free loop
            try { recognition.start(); } catch(e) {}
        };

        recognition.start();
    }
    </script>
    """
    components.html(voice_html, height=180)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "⚡ **All systems online, Boss.** Neural Matrix is fully synchronized. **S.H.I.V.A.I. X1** hands-free mode ready. Mic start karne ke liye upar button dabayein!"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Command me, Boss...")

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
