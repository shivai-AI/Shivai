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
st.set_page_config(page_title="SHIVAI", page_icon="🧠", layout="wide")
st.title("SHIVAI")
st.caption("*Your Mind. Your AI. Your Future.* | **Owner:** Shivam")

API_KEY = st.secrets.get("API_KEY", "").strip()

if not API_KEY or API_KEY == "YAHAN_APNI_GEMINI_API_KEY_DAALEIN":
    st.error("⚠️ Kripya Streamlit App Settings -> Secrets me apni API_KEY daalein!")
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
# 2. AUTO-DETECT MODEL ENGINE (Kabhi 404 Nahi Aayega)
# ==========================================
@st.cache_data(ttl=3600)
def get_working_models():
    """Yeh function Google se puch kar aapki Key par chalu models ki list nikalega"""
    valid_models = []
    try:
        for m in client.models.list():
            name = m.name.replace("models/", "")
            # Sirf text/chat generate karne wale gemini models chunein
            if "gemini" in name.lower() and not any(x in name.lower() for x in ["embedding", "imagen", "veo", "audio", "tts", "aqa"]):
                valid_models.append(name)
    except Exception:
        pass
    
    # Flash models ko pehle rakhein kyunki unka free quota sabse zyada hota hai
    flash_models = [m for m in valid_models if "flash" in m]
    other_models = [m for m in valid_models if "flash" not in m]
    
    final_list = flash_models + other_models
    if not final_list:
        final_list = ["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
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
            err_str = str(e)
            errors.append(f"{model_name}: {err_str}")
            # Agar search tool ki wajah se error ho toh bina search ke try karein
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
            
    # Agar sabhi models par 429 Quota error aaye
    if any("429" in err or "RESOURCE_EXHAUSTED" in err for err in errors):
        return "⚠️ **Quota Limit Reached (429):** Aapki is API Key ka free quota abhi khatam ho gaya hai. Kripya Google AI Studio (aistudio.google.com/app/apikey) par jaakar **'Create API key in new project'** par click karein aur woh nayi key Streamlit Secrets me daalein."
        
    return f"⚠️ Koi bhi model jawab nahi de paya. Details:\n`{errors[0] if errors else 'Unknown Error'}`"

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
    perm_search = st.toggle("🌐 Allow Live Internet Search", value=False)
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
    "♊ All-Rounder & Live Search (Gemini Mode)": "Act as a fast, helpful multimodal assistant.",
    "🧠 Deep Reasoning & Problem Solving (ChatGPT Mode)": "Think step-by-step using deep logic and structured problem-solving.",
    "🟣 Advanced Coding & Writing (Claude Mode)": "Write clean, bug-free code with detailed explanations.",
    "🔬 Deep Research Report Generator": "Conduct exhaustive analysis with Executive Summary and Key Findings.",
    "💼 Personal Business & Data Advisor": "Analyse business ideas, ROI, and give practical financial advice."
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
# 5. WORKSPACE TABS
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
            with st.spinner("SHIVAI soch raha hai..."):
                reply = ask_shivai(active_contents, system_prompt=SYSTEM_PROMPT, use_search=perm_search)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                if perm_voice and reply and not reply.startswith("⚠️"):
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
            if st.button("🧠 Analyse Data with SHIVAI"):
                with st.spinner("SHIVAI data analyse kar raha hai..."):
                    data_summary = f"Columns: {list(df.columns)}\nSample:\n{df.head(15).to_string()}\nStats:\n{df.describe().to_string()}"
                    reply = ask_shivai(f"{file_question}\n\nData:\n{data_summary}", system_prompt=SYSTEM_PROMPT)
                    st.markdown(reply)

        elif file_ext in ["png", "jpg", "jpeg"]:
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Image", width=350)
            if st.button("🧠 Analyse Image with SHIVAI"):
                with st.spinner("SHIVAI image dekh raha hai..."):
                    reply = ask_shivai([img, file_question], system_prompt=SYSTEM_PROMPT)
                    st.markdown(reply)

        elif file_ext == "pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() or "" for page in reader.pages[:15]])
            st.success(f"PDF Loaded ({len(reader.pages)} pages)")
            if st.button("🧠 Analyse PDF with SHIVAI"):
                with st.spinner("SHIVAI PDF padh raha hai..."):
                    reply = ask_shivai(f"{file_question}\n\nContent:\n{pdf_text[:20000]}", system_prompt=SYSTEM_PROMPT)
                    st.markdown(reply)

# --- TAB 3: TASK AUTOMATION ---
with tab_auto:
    st.subheader("⚙️ Permission-Based Digital Automation")
    task_type = st.selectbox("Select Automation Task:", [
        "📝 Generate & Save Report to File (.txt / .md)",
        "💻 Generate Python Automation Script",
        "📅 Create Daily Study / Business Action Plan"
    ])
    task_detail = st.text_area("Task ki detail likhein:")
    confirm_permission = st.checkbox("✅ Main SHIVAI ko ye task execute karne ki permission deta hun.")

    if st.button("🚀 Execute Task"):
        if not confirm_permission:
            st.error("⚠️ Pehle checkbox par tick karke permission dein.")
        elif not task_detail:
            st.warning("Pehle task ki detail likhein.")
        else:
            with st.spinner("SHIVAI task execute kar raha hai..."):
                reply = ask_shivai(f"Task Type: {task_type}\nDetails: {task_detail}\nExecute thoroughly.", system_prompt=SYSTEM_PROMPT)
                st.success("✅ Task Completed!")
                st.markdown(reply)
                st.download_button("📥 Download Output File", data=reply, file_name="shivai_output.md", mime="text/markdown")
