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
    margin: 14px 0 1
