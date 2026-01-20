# 🦋 Resonate AI - The Architect of Impactful Communication

**Resonate AI** is a premium, high-fidelity text transformation engine. It re-engineers your messy thoughts into polished, platform-specific content while providing deep linguistic insights, neural voice synthesis, and real-world social previews.

---

## 🛠️ Technology Stack

### Core Engine

- **Framework**: [Streamlit](https://streamlit.io/) - Used for the reactive, high-performance web interface.
- **Language Model**: [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) via Hugging Face Inference API. Used for all text reasoning and styling.
- **Neural Voice**:
  - **Primary**: [facebook/mms-tts-eng](https://huggingface.co/facebook/mms-tts-eng) - State-of-the-Art Neural Text-to-Speech for natural human prosody.
  - **Fallback**: [gTTS](https://pypi.org/project/gTTS/) - Google Text-to-Speech (UK English) for high reliability.

### Analysis & Analytics

- **Linguistic Logic**: [TextBlob](https://textblob.readthedocs.io/) and [TextStat](https://pypi.org/project/textstat/) for deep sentiment, subjectivity, and readability analysis.
- **File Handling**: `python-docx` for Word documents and `PyPDF2` for PDF scanning.

### Data & Visualization

- **Plotly Express**: Generates the "Linguistic DNA" radar charts.
- **Pandas**: Manages the scoring datasets for visualization.
- **Custom HTML/CSS**: Glassmorphic UI and platform-accurate social media previews.

---

## 🚀 Key Features

### 1. Refinement Suite 🎭

- **Dynamic Personas**: 14+ Personas including "Grammar Medic", "Gen Z", "Scientific", and "Pirate".
- **Global Reach**: Multilingual support for 10+ major languages.
- **Manual Overrides**: provide custom instructions for specific tweaks.

### 2. Social Media Previews 👀

- **X (Twitter) & LinkedIn**: See exactly how your post will look on the live platform before you post it, using custom-designed CSS cards.

### 3. Linguistic DNA & X-Ray 📊

- **Radar Charts**: Visualize Clarity, Energy, Professionalism, Creativity, and Emotion.
- **Deep Analytics**: Real-time checking of reading grade levels, sentiment polarity, and tone subjectivity.

### 4. SEO Keyword Targeting 🎯

- **Mandatory Keywords**: Set specific terms that the AI _must_ include.
- **Hit Rate Dashboard**: Automatic verification and celebration when your keywords are successfully integrated.

### 5. Persistent Session History 📜

- **Recall & Compare**: Access previous transformations from the sidebar history to compare styles or recover work.

---

## 🏗️ Project Structure

- `app.py`: The main application logic, AI prompting, and UI rendering.
- `requirements.txt`: List of Python libraries needed (Streamlit, gTTS, Plotly, TextStat, etc.).
- `.streamlit/secrets.toml`: Stores your Hugging Face API Token.

---

## ⚙️ Installation & Usage

1. **Environment Setup**:

   ```bash
   # Create a virtual environment
   python3 -m venv .venv
   # Activate the environment
   source .venv/bin/activate
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   Create `.streamlit/secrets.toml`:

   ```toml
   HUGGING_FACE_API_KEY = "your_hf_token_here"
   ```

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

---

_Crafted for efficiency. Refined for impact. Built to Resonate._
