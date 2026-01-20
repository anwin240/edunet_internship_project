import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import json
from gtts import gTTS
import base64
import io
import difflib

from docx import Document
import re

try:
    import textstat

    from textblob import TextBlob
except ImportError:
    pass


# --- CONFIGURATION ---
API_TOKEN = st.secrets["HUGGING_FACE_API_KEY"]
TEXT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# --- AI LOGIC ---
def query_ai(messages):
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
    # Neural TTS Model (Much more natural than gTTS)
    API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

def read_file(uploaded_file):
    if uploaded_file.name.endswith('.docx'):
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    else: # Plain text
        return str(uploaded_file.read(), "utf-8")

def render_social_preview(text, platform):
    if platform == "X (Twitter) 🐦":
        html = f"""
        <div style="font-family: sans-serif; background: #15202b; color: white; padding: 20px; border-radius: 12px; border: 1px solid #38444d; max-width: 500px; margin: auto;">
            <div style="display: flex; gap: 12px;">
                <div style="min-width: 48px; width: 48px; height: 48px; background: #7f00ff; border-radius: 50%;"></div>
                <div>
                    <div style="font-weight: bold;">You <span style="color: #657786; font-weight: normal;">@resonate_user · 1m</span></div>
                    <div style="margin-top: 5px; font-size: 15px; line-height: 1.5;">{text}</div>
                    <div style="margin-top: 15px; color: #657786; font-size: 18px;">
                        💬 2 &nbsp;&nbsp; 🔄 5 &nbsp;&nbsp; ❤️ 12
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    elif platform == "LinkedIn 🔵":
        preview_text = text[:200] + "... see more" if len(text) > 200 else text
        html = f"""
        <div style="font-family: sans-serif; background: white; color: black; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; max-width: 500px; margin: auto;">
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <div style="min-width: 48px; width: 48px; height: 48px; background: #0a66c2; border-radius: 50%;"></div>
                <div>
                    <div style="font-weight: bold; font-size: 14px;">Your Name</div>
                    <div style="color: gray; font-size: 12px;">Creative Visionary • 1st</div>
                    <div style="color: gray; font-size: 12px;">1h • 🌐</div>
                </div>
            </div>
            <div style="font-size: 14px; line-height: 1.5;">{preview_text}</div>
            <div style="margin-top: 10px; height: 150px; background: #f3f2ef; display: flex; align-items: center; justify-content: center; color: gray; border-radius: 4px;">
                [Image/Media Preview Block]
            </div>
            <div style="margin-top: 10px; border-top: 1px solid #e0e0e0; padding-top: 10px; display: flex; justify-content: space-between; color: gray; font-size: 14px;">
                <span>👍 Like</span> <span>💬 Comment</span> <span>↪️ Share</span> <span>✈️ Send</span>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    
    else:
        st.info(f"Visual preview not available for {platform} yet. Switch to 'Final Result' to see your text.")

def execute_transformation(text, tone, platform, emoji_level, length, vibe, target_lang, custom_prompt, target_keywords):
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
    vibe_instr = f"Atmosphere: {vibe}. Additional constraint: {custom_prompt}."
    
    kw_instruction = ""
    if target_keywords:
        kw_instruction = f"MANDATORY: You must naturally include these exact keywords: {target_keywords}."

    messages = [
        {"role": "system", "content": f"You are Resonate AI. Task: {tone_map.get(tone)}. {platform_map.get(platform)}. {emoji_instr} {vibe_instr} {kw_instruction} Length: {length}. Output ONLY the transformed text in {target_lang}. IMPORTANT: On a new line at the very end, add exactly this: [SCORES] followed by 5 comma-separated numbers (0-100) representing (Clarity, Energy, Professionalism, Creativity, Emotion). Example: [SCORES] 85,70,90,65,80"},
        {"role": "user", "content": f"Text: \"{text}\""}
    ]


    output = query_ai(messages)
    try:
        if "choices" in output:
            full_res = output["choices"][0]["message"]["content"].strip()
            
            # More robust extraction using unique delimiter
            if "[SCORES]" in full_res:
                parts = full_res.split("[SCORES]")
                text_part = parts[0].strip()
                score_str = parts[1].strip()
                
                # Extract digits from the score string
                scores = re.findall(r'\d+', score_str)
                if len(scores) >= 5:
                    data_part = ",".join(scores[:5])
                    return text_part, data_part
            
            # Fallback regex search if delimiter is missing but scores are present
            score_match = re.search(r'(\d{1,3}(?:,\s*)?){5}', full_res)
            if score_match:
                matched_str = score_match.group(0)
                scores = re.findall(r'\d+', matched_str)
                if len(scores) >= 5:
                    data_part = ",".join(scores[:5])
                    text_part = full_res.replace(matched_str, "").replace("[SCORES]", "").strip()
                    return text_part, data_part


            return full_res, "50,50,50,50,50"
        return f"⚠️ {output.get('error')}", "0,0,0,0,0"
    except Exception as e:
        return f"❌ Transformation Failed: {str(e)}", "0,0,0,0,0"

# --- UI SETUP ---
st.set_page_config(page_title="Resonate AI", page_icon="🦋", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    .main { background-color: #0e1117; font-family: 'Inter', sans-serif; }
    .stTextArea textarea { border-color: #7f00ff; border-radius: 12px; }
    .stButton>button {
        background: #7f00ff;
        color: white; border-radius: 15px; height: 3.5em; font-weight: bold; border: none;
    }
    .output-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 25px; border-radius: 12px; border-left: 5px solid #7f00ff;
        font-size: 1.1rem; line-height: 1.6; color: #f0f0f0;
        white-space: pre-wrap; word-wrap: break-word;
    }

    div[data-testid="stNotification"] {
        word-wrap: break-word;
        white-space: pre-wrap;
    }

</style>

""", unsafe_allow_html=True)

st.title("🦋 Resonate AI")
st.markdown("""
**The Architect of Impactful Communication.**  
*Refine your voice, adapt to any platform, and analyze your message's linguistic DNA in seconds.*
""")

# --- SESSION STATE INITIALIZATION ---
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'out' not in st.session_state:
    st.session_state['out'] = None
if 'data' not in st.session_state:
    st.session_state['data'] = None

with st.sidebar:
    st.header("📜 Session History")
    if not st.session_state['history']:
        st.info("No history yet. Start resonating!")
    
    for i, item in enumerate(reversed(st.session_state['history'])):
        # Calculate original index since we are reversed
        orig_idx = len(st.session_state['history']) - 1 - i
        with st.expander(f"Run #{orig_idx + 1}: {item['style']}"):
            st.caption("Transformed Preview:")
            st.text(item['transformed'][:100] + "...")
            if st.button("🔄 Load", key=f"load_{orig_idx}"):
                # Clear all previous result states first
                st.session_state['out'] = None
                st.session_state['data'] = None
                if 'final_edit_box' in st.session_state:
                    del st.session_state['final_edit_box']
                
                # Load new values
                st.session_state['out'] = item['transformed']
                st.session_state['data'] = item['metrics']
                st.rerun()
    
    st.divider()
    st.header("🛠️ Manual Overrides")
    custom_prompt = st.text_input("Custom Instruction (Optional)", placeholder="e.g., 'Don't use the word synergy'")
    
    st.divider()
    st.header("🎯 SEO Targeting")
    target_keywords = st.text_input("Target Keywords (comma separated)", placeholder="e.g. AI, growth, synergy")

col1, col2 = st.columns([1.5, 1])

with col1:
    # Toggle between Text Input and File Upload
    input_mode = st.radio("Input Source", ["Type / Paste", "Upload File 📂"], horizontal=True, label_visibility="collapsed")
    
    input_text_placeholder = "Drop your messy thoughts here, let them resonate..."

    if input_mode == "Upload File 📂":
        uploaded_file = st.file_uploader("Drop your draft (DOCX, TXT)", type=['docx', 'txt'])
        if uploaded_file:
            # Auto-fill the text area with file content
            file_text = read_file(uploaded_file)
            u_text = st.text_area("File Content (Editable):", value=file_text, height=400)
        else:
            u_text = ""
            st.info("Waiting for file...")
    else:
        u_text = st.text_area("Input Content:", height=450, placeholder=input_text_placeholder, label_visibility="collapsed")

with col2:
    st.subheader("⚙️ Refinement Suite")
    with st.expander("Step 1: Choose Persona 🎭", expanded=True):
        t = st.selectbox("Persona Mode:", ["Professional 👔", "Grammar Medic 🩹", "Simplifier (ELI5) 👶", "Brutally Honest 🎯", "Hype Man 🚀", "Scientific / Academic 🧪", "Storyteller / Creative 📖", "Motivational Coach 🏆", "Angry Customer 😤", "Passive Aggressive 🙃", "Legal/Formal ⚖️", "Gen Z / Slang 🧢", "Shakespearean 🎭", "Pirate 🏴‍☠️"])
    
    with st.expander("Step 2: Define Destination 🚀", expanded=True):
        p = st.selectbox("Platform Format:", ["Standard Text 📄", "WhatsApp 🟢", "LinkedIn 🔵", "Instagram 📸", "X (Twitter) 🐦", "Email 📧", "Slack / Discord 💬", "Reddit 🤖", "YouTube Script 🎬", "SMS 📱"])
    
    with st.expander("Step 3: Style intensity ✨", expanded=False):
        c1, c2 = st.columns(2)
        with c1: e = st.selectbox("Emoji Level:", ["None 🚫", "Sparse 🤏", "Heavy ✨"], index=1)
        with c2: l = st.selectbox("Output Depth:", ["Concise", "Detailed"])
    
    with st.expander("Step 4: Atmosphere Tuning 🎻", expanded=False):
        v = st.select_slider("Select Vibe", options=["Neutral", "Inspiring", "Cynical", "Grateful", "Sarcastic"])

    with st.expander("Step 5: Global Reach 🌍", expanded=False):
        target_lang = st.selectbox("Target Language 🌍", ["English", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Arabic", "Portuguese", "Russian"])

    with st.expander("Step 6: Insights Architect 📊", expanded=False):
        show_stats = st.checkbox("Show Linguistic Analysis (Charts)", value=True)

    st.divider()
    if st.button("🚀 EXECUTE FULL TRANSFORMATION", use_container_width=True):
        if u_text:
            with st.spinner("Analyzing resonance..."):
                res, data = execute_transformation(u_text, t, p, e, l, v, target_lang, custom_prompt, target_keywords)
                st.session_state['out'] = res

                st.session_state['data'] = data
                # Append to history
                st.session_state['history'].append({
                    "original": u_text,
                    "transformed": res,
                    "style": f"{t} | {p} | {v} | {target_lang}",
                    "metrics": data
                })
                # Rerun to force the UI to recognize session state changes and update the text_area
                st.rerun()

        else:
            st.warning("Input required to resonate.")

if st.session_state['out']:
    st.divider()
    
    # Keyword Hit Rate Check
    if target_keywords:
        st.subheader("🎯 Keyword Hit Rate")
        keywords = [k.strip().lower() for k in target_keywords.split(",") if k.strip()]
        if keywords:
            found_count = 0
            cols = st.columns(len(keywords))
            lower_out = st.session_state['out'].lower()
            
            for idx, kw in enumerate(keywords):
                if kw in lower_out:
                    cols[idx].success(f"✅ {kw}")
                    found_count += 1
                else:
                    cols[idx].error(f"❌ {kw}")
            
            if found_count == len(keywords):
                st.balloons()
        st.divider()

    # Dynamically define tabs based on platform support
    tab_list = ["✨ Final Result"]
    show_preview = p in ["X (Twitter) 🐦", "LinkedIn 🔵"]
    if show_preview:
        tab_list.append("👀 Social Preview")
    tab_list.extend(["⚖️ Side-by-Side", "📊 Linguistic Analysis"])
    
    tabs = st.tabs(tab_list)
    
    # Unpack tabs correctly
    if show_preview:
        tab1, tab_v, tab2, tab3 = tabs
    else:
        tab1, tab2, tab3 = tabs
        tab_v = None

    with tab1:
        st.markdown(f'<div class="output-container">{st.session_state["out"]}</div>', unsafe_allow_html=True)
        st.write("") # Spacer

        # Actions Row for compact buttons
        c_p1, c_p2, c_p3 = st.columns([1.2, 1.2, 2])
        
        with c_p1:
            # Copy to Clipboard Button using JS
            js_text = st.session_state["out"].replace('`', '\\`').replace('\n', '\\n')
            copy_js = f"""
            <button id="copy-btn" onclick="copyToClipboard()" style="
                background: transparent;
                color: #bc82ff;
                border: 1px solid rgba(127, 0, 255, 0.5);
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-family: 'Inter', sans-serif;
                white-space: nowrap;
                box-shadow: 0 4px 15px rgba(127, 0, 255, 0.1);
            " onmouseover="this.style.background='rgba(127, 0, 255, 0.1)'; this.style.boxShadow='0 0 15px rgba(127, 0, 255, 0.4)';" onmouseout="this.style.background='transparent'; this.style.boxShadow='0 4px 15px rgba(127, 0, 255, 0.1)';">
                📋 Copy Result
            </button>

            <script>
            function copyToClipboard() {{
                const text = `{js_text}`;
                navigator.clipboard.writeText(text).then(() => {{
                    const btn = document.getElementById('copy-btn');
                    btn.innerHTML = "✨ Copied!";
                    setTimeout(() => {{
                        btn.innerHTML = "📋 Copy Result";
                    }}, 2000);
                }});
            }}
            </script>
            """
            components.html(copy_js, height=62)

        with c_p2:
            # Download button with updated emoji and style
            st.download_button(
                label="💾 Save as Text File",
                data=st.session_state['out'],
                file_name="resonate_output.txt",
                mime="text/plain",
                use_container_width=False
            )

    if show_preview and tab_v:
        with tab_v:
            st.subheader("👀 Real-World Social Preview")
            render_social_preview(st.session_state['out'], p)

    with tab2:
        col_a, col_b = st.columns(2)
        # Find original text for comparison
        # Fallback to current input if not in history or if just loaded
        orig_text = u_text
        for item in reversed(st.session_state['history']):
            if item['transformed'] == st.session_state['out']:
                orig_text = item['original']
                break
                
        with col_a:
            st.caption("Original")
            st.info(orig_text if orig_text else "No original text available.")
        with col_b:
            st.caption("Resonated")
            st.success(st.session_state['out'])

    with tab3:
        # On-demand Voice Synthesis moved here to keep page short
        if st.button("🔊 Generate Audio"):
            try:
                with st.spinner("Synthesizing..."):
                    audio_content = query_audio(st.session_state['out'])
                    if audio_content:
                        b64_audio = base64.b64encode(audio_content).decode()
                        format_type = "wav"
                    else:
                        tts = gTTS(text=st.session_state['out'], lang='en', tld='co.uk')
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        b64_audio = base64.b64encode(audio_fp.getvalue()).decode()
                        format_type = "mp3"
                    
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
        st.subheader("📊 Linguistic DNA & Deep X-Ray")
        
        # 1. AI DNA Analysis (Radar Chart)
        try:
            raw_data = st.session_state.get('data', "50,50,50,50,50")
            scores = [int(x.strip()) for x in raw_data.split(',')]
            if len(scores) < 5: scores = scores + [50]*(5-len(scores))
            
            df = pd.DataFrame(dict(r=scores[:5], theta=['Clarity', 'Energy', 'Professionalism', 'Creativity', 'Emotion']))
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
            st.info("DNA Chart extraction in progress...")

        # 2. Deep Linguistic X-Ray (TextStat/TextBlob)
        try:
            import textstat
            from textblob import TextBlob
            st.divider()
            content = st.session_state['out']
            if content:
                blob = TextBlob(content)
                reading_level = textstat.flesch_kincaid_grade(content)
                sentiment = blob.sentiment.polarity 
                subjectivity = blob.sentiment.subjectivity 
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Grade Level", f"{reading_level}")
                    st.caption("Lower is easier to understand")
                with k2:
                    sent_label = "Positive 🟢" if sentiment > 0.1 else "Negative 🔴" if sentiment < -0.1 else "Neutral ⚪"
                    st.metric("Sentiment", sent_label, f"{sentiment:.2f}")
                with k3:
                    subj_label = "Opinionated 🗣️" if subjectivity > 0.5 else "Objective ⚖️"
                    st.metric("Tone Type", subj_label, f"{subjectivity:.0%}")
                with k4:
                    word_count = len(content.split())
                    st.metric("Word Count", word_count, f"Est: {word_count/200:.1f} min speech")
        except:
            st.warning("Deep metrics loading...")
