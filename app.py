import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import json
from gtts import gTTS
import base64
import io

# --- CONFIGURATION ---
try:
    API_TOKEN = st.secrets["HUGGING_FACE_API_KEY"]
except Exception:
    API_TOKEN = "YOUR_HUGGING_FACE_API_KEY_HERE"

# Unified Model
TEXT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# --- AI LOGIC ---
def query_ai(messages):
    if API_TOKEN == "YOUR_HUGGING_FACE_API_KEY_HERE":
        return {"error": "API Key is missing! Please add it to .streamlit/secrets.toml"}
    
    ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"
    payload = {
        "model": TEXT_MODEL,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(ROUTER_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API Error {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def query_audio(text):
    if API_TOKEN == "YOUR_HUGGING_FACE_API_KEY_HERE":
        return None
    
    # Neural TTS Model (Much more natural than gTTS)
    API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

def execute_transformation(text, tone, platform, emoji_level, length, vibe):
    tone_map = {
        "Professional 👔": "Rewrite to be corporate-ready and sophisticated.",
        "Grammar Medic 🩹": "Correct grammar, spelling, and flow only.",
        "Brutally Honest 🎯": "Remove all fluff. Just facts.",
        "Hype Man 🚀": "Make it high-energy and exciting.",
        "Simplifier (ELI5) 👶": "Explain like I'm 5 years old.",
        "Scientific / Academic 🧪": "Use technical, objective language.",
        "Storyteller / Creative 📖": "Add descriptive flair.",
        "Motivational Coach 🏆": "Focus on growth and energy.",
        "Angry Customer 😤": "Demanding, dissatisfied tone.",
        "Passive Aggressive 🙃": "Politely annoying.",
        "Legal/Formal ⚖️": "Strict legal terminology.",
        "Gen Z / Slang 🧢": "Modern slang.",
        "Shakespearean 🎭": "William Shakespeare style.",
        "Pirate 🏴‍☠️": "Gritty pirate captain style."
    }

    platform_map = {
        "Standard Text 📄": "Paragraphs.",
        "WhatsApp 🟢": "Use *bold* for emphasis. Chatty.",
        "LinkedIn 🔵": "Professional spacing + 3 hashtags.",
        "Instagram 📸": "Vibrant + hashtag block.",
        "X (Twitter) 🐦": "Concise hook + 2 hashtags.",
        "Email 📧": "Subject, Greeting, Body, Sign-off.",
        "Slack / Discord 💬": "Fast-paced formatting.",
        "Reddit 🤖": "Markdown + TL;DR.",
        "YouTube Script 🎬": "Hook, Intro, Body, CTA.",
        "SMS 📱": "Maximum brevity."
    }

    emoji_instr = {"None 🚫": "No emojis.", "Sparse 🤏": "Max 2 emojis.", "Heavy ✨": "Generous emojis."}[emoji_level]
    vibe_instr = f"Atmosphere: {vibe}."

    messages = [
        {"role": "system", "content": f"You are Resonate AI. Task: {tone_map.get(tone)}. {platform_map.get(platform)}. {emoji_instr} {vibe_instr} Length: {length}. Output ONLY the transformed text. IMPORTANT: Also, add a single hidden line at the very end with exactly 5 comma-separated values (0-100) representing (Clarity, Energy, Professionalism, Creativity, Emotion)."},
        {"role": "user", "content": f"Text: \"{text}\""}
    ]

    output = query_ai(messages)
    try:
        if "choices" in output:
            full_res = output["choices"][0]["message"]["content"].strip()
            lines = full_res.split('\n')
            if ',' in lines[-1] and any(char.isdigit() for char in lines[-1]):
                text_part = "\n".join(lines[:-1])
                data_part = lines[-1].strip()
                return text_part, data_part
            return full_res, "50,50,50,50,50"
        return f"⚠️ {output.get('error')}", "0,0,0,0,0"
    except:
        return "❌ Transformation Failed.", "0,0,0,0,0"

# --- UI SETUP ---
st.set_page_config(page_title="Resonate AI", page_icon="🦋", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    .main { background-color: #0e1117; font-family: 'Inter', sans-serif; }
    .stTextArea textarea { border-color: #7f00ff; border-radius: 12px; }
    .stButton>button {
        background: linear-gradient(90deg, #7f00ff, #e100ff);
        color: white; border-radius: 15px; height: 3.5em; font-weight: bold; border: none;
    }
    .output-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 25px; border-radius: 15px; border-left: 5px solid #7f00ff;
        font-size: 1.1rem; line-height: 1.6; color: #f0f0f0;
    }
    .voice-badge {
        display: inline-flex; align-items: center; gap: 5px;
        background: rgba(127, 0, 255, 0.2); color: #bc82ff;
        padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 600; margin-bottom: 10px; border: 1px solid rgba(127, 0, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🦋 Resonate AI")
st.markdown("""
**The Architect of Impactful Communication.**  
*Refine your voice, adapt to any platform, and analyze your message's linguistic DNA in seconds.*
""")

col1, col2 = st.columns([1.5, 1])

with col1:
    u_text = st.text_area("Input Content:", height=450, placeholder="Drop your messy thoughts here, let them resonate...", label_visibility="collapsed")

with col2:
    st.subheader("⚙️ Refinement Suite")
    with st.expander("Step 1: Choose Persona 🎭", expanded=True):
        t = st.selectbox("Persona Mode:", ["Professional 👔", "Grammar Medic 🩹", "Simplifier (ELI5) 👶", "Brutally Honest 🎯", "Hype Man 🚀", "Scientific / Academic 🧪", "Storyteller / Creative 📖", "Motivational Coach 🏆", "Angry Customer 😤", "Passive Aggressive 🙃", "Legal/Formal ⚖️", "Gen Z / Slang 辨", "Shakespearean 🎭", "Pirate 🏴‍☠️"])
    
    with st.expander("Step 2: Define Destination 🚀", expanded=True):
        p = st.selectbox("Platform Format:", ["Standard Text 📄", "WhatsApp 🟢", "LinkedIn 🔵", "Instagram 📸", "X (Twitter) 🐦", "Email 📧", "Slack / Discord 💬", "Reddit 🤖", "YouTube Script 🎬", "SMS 📱"])
    
    with st.expander("Step 3: Style intensity ✨", expanded=False):
        c1, c2 = st.columns(2)
        with c1: e = st.selectbox("Emoji Level:", ["None 🚫", "Sparse 🤏", "Heavy ✨"], index=1)
        with c2: l = st.selectbox("Output Depth:", ["Concise", "Detailed"])
    
    with st.expander("Step 4: Atmosphere Tuning 🎻", expanded=False):
        v = st.select_slider("Select Vibe", options=["Neutral", "Inspiring", "Cynical", "Grateful", "Sarcastic"])

    with st.expander("Step 5: Insights Architect 📊", expanded=False):
        show_stats = st.checkbox("Show Linguistic Analysis (Charts)", value=True)

    st.divider()
    if st.button("🚀 EXECUTE FULL TRANSFORMATION", use_container_width=True):
        if u_text:
            with st.spinner("Analyzing resonance..."):
                res, data = execute_transformation(u_text, t, p, e, l, v)
                st.session_state['out'] = res
                st.session_state['data'] = data
        else:
            st.warning("Input required to resonate.")

if 'out' in st.session_state:
    st.divider()
    st.subheader("✨ Output Text")
    
    # Using st.code for the built-in copy button functionality
    st.code(st.session_state['out'], language=None)

    # On-demand Voice Synthesis
    if st.button("🔊 Generate Audio"):
        try:
            with st.spinner("Synthesizing..."):
                # Try Premium Neural TTS first
                audio_content = query_audio(st.session_state['out'])
                
                if audio_content:
                    b64_audio = base64.b64encode(audio_content).decode()
                    format_type = "wav"
                else:
                    # Fallback to gTTS if Neural API is busy
                    tts = gTTS(text=st.session_state['out'], lang='en', tld='co.uk')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    b64_audio = base64.b64encode(audio_fp.getvalue()).decode()
                    format_type = "mp3"
                
                # Premium Audio Player
                audio_html = f"""
                <div style="background: rgba(127, 0, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(127, 0, 255, 0.2); margin-top: 10px; margin-bottom: 20px;">
                    <audio controls autoplay style="width: 100%; filter: invert(100%) hue-rotate(180deg) brightness(1.5);">
                        <source src="data:audio/{format_type};base64,{b64_audio}" type="audio/{format_type}">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Voice Synthesis Error: {str(e)}")
    
    # Linguistic Analysis Section
    st.divider()
    st.subheader("📊 Linguistic Analysis")
    try:
        scores = [int(x) for x in st.session_state['data'].split(',')]
        df = pd.DataFrame(dict(r=scores, theta=['Clarity', 'Energy', 'Professionalism', 'Creativity', 'Emotion']))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,100], color_discrete_sequence=['#7f00ff'])
        fig.update_polars(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100]))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Read Time", f"{max(1, len(st.session_state['out'].split())//150)} min")
        with c2: st.metric("Clarity Score", f"{scores[0]}%")
        impact_score = (scores[1] + scores[4]) // 2
        with c3: st.metric("Impact Score", f"{impact_score}%")
    except:
        st.info("Analysis data for this transformation is being calculated.")
