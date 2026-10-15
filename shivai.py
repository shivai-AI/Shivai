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
# 1. API & PRIVACY CONFIGURATION
# ==========================================
# Cloud secrets se API Key lega, agar local ho toh direct bhi chalega
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
    API_KEY = "YAHAN_APNI_GEMINI_API_KEY_DAALEIN"

client = genai.Client(api_key=API_KEY)

MEMORY_FILE = "shivai_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"notes": [], "permissions": {"save_memory": True, "voice_reply": True, "web_search": True}}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

memory_data = load_memory()

# ==========================================
# 2. PAGE SETUP (PHONE + LAPTOP UI)
# ==========================================
st.set_page_config(page_title="SHIVAI", page_icon="🧠", layout="wide")

st.title("SHIVAI")
st.caption("*Your Mind. Your AI. Your Future.* | **Owner:** Shivam")

# ==========================================
# 3. SIDEBAR: BRAIN ROUTER, PRIVACY & MEMORY
# ==========================================
with st.sidebar:
    st.header("⚡ 1. Choose SHIVAI Brain Mode")
    brain_mode = st.selectbox(
        "Select Intelligence Engine:",
        [
            "♊ All-Rounder & Live Search (Gemini Mode)",
            "🧠 Deep Reasoning & Problem Solving (ChatGPT Mode)",
            "🟣 Advanced Coding & Writing (Claude Mode)",
            "🔬 Deep Research Report Generator",
            "💼 Personal Business & Data Advisor"
        ]
    )

    st.divider()
    st.header("🔐 2. Privacy & Permissions")
    perm_search = st.toggle("🌐 Allow Live Internet Search", value=memory_data["permissions"].get("web_search", True))
    perm_voice = st.toggle("🎙️ Enable Voice Audio Reply", value=memory_data["permissions"].get("voice_reply", True))
    perm_memory = st.toggle("🧠 Allow Personal Memory Access", value=memory_data["permissions"].get("save_memory", True))

    memory_data["permissions"] = {
        "web_search": perm_search,
        "voice_reply": perm_voice,
        "save_memory": perm_memory
    }
    save_memory(memory_data)

    st.divider()
    st.header("🧠 3. Personal Memory Vault")
    if perm_memory:
        new_note = st.text_input("Add Goal / Preference / Project:")
        if st.button("➕ Save with Permission") and new_note:
            memory_data["notes"].append(new_note)
            save_memory(memory_data)
            st.success("Saved to SHIVAI Memory!")
            st.rerun()

        if memory_data["notes"]:
            st.write("**Saved Items:**")
            for i, note in enumerate(memory_data["notes"]):
                st.caption(f"{i+1}. {note}")
            if st.button("🗑️ Wipe All Memory"):
                memory_data["notes"] = []
                save_memory(memory_data)
                st.rerun()
    else:
        st.info("🔒 Memory access is turned OFF by Shivam.")

# ==========================================
# 4. DYNAMIC SYSTEM INSTRUCTIONS
# ==========================================
mode_instructions = {
    "♊ All-Rounder & Live Search (Gemini Mode)": "Act as a fast, multimodal assistant with real-time internet knowledge.",
    "🧠 Deep Reasoning & Problem Solving (ChatGPT Mode)": "Think step-by-step using deep logic, first-principles reasoning, and structured problem-solving.",
    "🟣 Advanced Coding & Writing (Claude Mode)": "Write clean, production-ready, bug-free code with detailed explanations, and craft high-quality, articulate writing.",
    "🔬 Deep Research Report Generator": "Conduct exhaustive multi-source analysis. Structure your answer with an Executive Summary, Key Findings, Data Breakdown, and Verified Sources.",
    "💼 Personal Business & Data Advisor": "Analyse business ideas, calculate ROI, sales, expenses, profit margins, and give practical financial & strategic advice."
}

saved_context = json.dumps(memory_data["notes"], ensure_ascii=False) if perm_memory else "Memory access disabled."

SYSTEM_PROMPT = f"""
Identity:
- AI Name: SHIVAI (Shivam's Intelligent Virtual AI)
- Owner: Shivam
- Tagline: Your Mind. Your AI. Your Future.
- Personality: Intelligent, calm, practical, loyal to Shivam.
- Language: Natural Hinglish, Hindi, and English.

Current Active Brain Mode: {brain_mode}
Special Mode Instruction: {mode_instructions[brain_mode]}

Shivam's Saved Personal Memory:
{saved_context}
"""

# ==========================================
# 5. WORKSPACE TABS (CHAT, VOICE, FILES, AUTOMATION)
# ==========================================
tab_chat, tab_files, tab_auto = st.tabs([
    "💬 Chat & 🎙️ Voice AI", 
    "📄 File Intelligence & 📊 Data Analysis", 
    "⚙️ Task Automation"
])

# --- TAB 1: CHAT & VOICE ---
with tab_chat:
    audio_value = st.audio_input("🎙️ Bolkar command dein ('Hey SHIVAI...'):")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello Shivam! **SHIVAI** system online hai. Aap likhkar ya माइक दबाकर बोलकर बात कर सकते हैं।"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Ask SHIVAI anything (Coding, Research, Business, General)...")

    active_contents = None
    display_text = None

    if user_prompt:
        display_text = user_prompt
        active_contents = [user_prompt]
    elif audio_value is not None:
        audio_bytes = audio_value.read()
        if "last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes:
            st.session_state.last_audio = audio_bytes
            display_text = "🎙️ *[Voice Command Sent]*"
            active_contents = [
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                "Sun kar samjho ki Shivam ne kya kaha hai aur uska satik jawab do."
            ]

    if active_contents:
        st.session_state.messages.append({"role": "user", "content": display_text})
        with st.chat_message("user"):
            st.markdown(display_text)

        with st.chat_message("assistant"):
            with st.spinner(f"SHIVAI ({brain_mode.split('(')[0]}) soch raha hai..."):
                tools_list = [{"google_search": {}}] if perm_search else []
                
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=active_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=tools_list,
                    ),
                )
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                if perm_voice and reply:
                    try:
                        clean_speech = reply.replace("*", "").replace("#", "")[:500]
                        tts = gTTS(text=clean_speech, lang="hi")
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp.getvalue(), format="audio/mp3")
                    except Exception:
                        pass

# --- TAB 2: FILE INTELLIGENCE & DATA ANALYSIS ---
with tab_files:
    st.subheader("📄 Upload PDF, Image, or Excel/CSV for Instant Analysis")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"])
    file_question = st.text_input("Is file ke baare mein kya puchna ya analyse karna hai?", value="Is file ka pura analysis aur summary do.")

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()

        if file_ext in ["csv", "xlsx"]:
            df = pd.read_csv(uploaded_file) if file_ext == "csv" else pd.read_excel(uploaded_file)
            st.write("### 📊 Data Preview:")
            st.dataframe(df.head(10))
            
            st.write("### 📈 Quick Statistical Summary:")
            st.write(df.describe())

            if st.button("🧠 Analyse Data with SHIVAI"):
                with st.spinner("SHIVAI data analyse kar raha hai..."):
                    data_summary = f"Columns: {list(df.columns)}\nSample Data:\n{df.head(20).to_string()}\nStats:\n{df.describe().to_string()}"
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"{file_question}\n\nData:\n{data_summary}",
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    )
                    st.markdown(res.text)

        elif file_ext in ["png", "jpg", "jpeg"]:
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Image", width=350)
            if st.button("🧠 Analyse Image with SHIVAI"):
                with st.spinner("SHIVAI image dekh raha hai..."):
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[img, file_question],
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    )
                    st.markdown(res.text)

        elif file_ext == "pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = ""
            for page in reader.pages[:15]:
                pdf_text += page.extract_text() or ""
            st.success(f"PDF Loaded ({len(reader.pages)} pages)")
            if st.button("🧠 Analyse PDF with SHIVAI"):
                with st.spinner("SHIVAI PDF padh raha hai..."):
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"{file_question}\n\nDocument Content:\n{pdf_text[:20000]}",
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                    )
                    st.markdown(res.text)

# --- TAB 3: TASK AUTOMATION ---
with tab_auto:
    st.subheader("⚙️ Permission-Based Digital Automation")
    st.write("SHIVAI aapki permission ke bina koi action nahi lega.")
    
    task_type = st.selectbox("Select Automation Task:", [
        "📝 Generate & Save Report to File (.txt / .md)",
        "💻 Generate Python Automation Script",
        "📅 Create Daily Study / Business Action Plan"
    ])
    
    task_detail = st.text_area("Task ki detail likhein (e.g., 'AI startup ke liye 30 days ka plan banao'):")
    confirm_permission = st.checkbox("✅ Main SHIVAI ko ye task execute karne ki permission deta hun.")

    if st.button("🚀 Execute Task"):
        if not confirm_permission:
            st.error("⚠️ Permission Denied! Pehle checkbox par tick karke permission dein.")
        elif not task_detail:
            st.warning("Pehle task ki detail likhein.")
        else:
            with st.spinner("SHIVAI task execute kar raha hai..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Task Type: {task_type}\nDetails: {task_detail}\nExecute this thoroughly.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
                )
                st.success("✅ Task Completed Successfully!")
                st.markdown(res.text)
                st.download_button(
                    label="📥 Download Output File",
                    data=res.text,
                    file_name="shivai_output.md",
                    mime="text/markdown"
                )
