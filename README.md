# 🦋 Resonate AI - The Architect of Impactful Communication

**Resonate AI** is a premium, high-fidelity text transformation engine. It re-engineers your messy thoughts into polished, platform-specific content while providing deep linguistic insights and neural voice synthesis.

---

## 🛠️ Technology Stack

### Core Engine

- **Framework**: [Streamlit](https://streamlit.io/) - Used for the reactive, high-performance web interface.
- **Language Model**: [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) via Hugging Face Inference API. Used for all text reasoning and styling.
- **Neural Voice**:
  - **Primary**: [facebook/mms-tts-eng](https://huggingface.co/facebook/mms-tts-eng) - State-of-the-Art Neural Text-to-Speech for natural human prosody.
  - **Fallback**: [gTTS](https://pypi.org/project/gTTS/) - Google Text-to-Speech (UK English) for high reliability.

### Data & Visualization

- **Plotly Express**: Generates the "Linguistic DNA" radar charts.
- **Pandas**: Manages the scoring datasets for visualization.
- **Custom CSS**: Implements a premium "Glassmorphism" theme with `Inter` typography and dynamic UI components.

---

## 🚀 Key Features & Implementation

### 1. Refinement Suite 🎭

- **Implementation**: Uses advanced **System Prompting** to map user selections (Persona, Platform, Vibe) into specific linguistic instructions.
- **Capabilities**: Support for 14+ Personas (Professional, Gen Z, Pirate, etc.) and 10+ Platform formats (LinkedIn, WhatsApp, YouTube, etc.).

### 2. Neural Audio Resonance 🔊

- **Implementation**: Text is sent to a Neural TTS model. The resulting audio bytes are encoded in **Base64** and injected into a custom-styled HTML5 `<audio>` element.
- **Optimization**: Uses CSS filters (`invert`, `hue-rotate`) to theme the native browser audio player to match the app's dark-mode aesthetic.

### 3. Linguistic DNA (Insights Architect) 📊

- **Implementation**: The AI engine is instructed to append a "hidden" line of scoring data (Clarity, Energy, Professionalism, Creativity, Emotion) to every transformation.
- **Visualization**: Python parses this hidden data to build a real-time **Radar Chart**, allowing users to visualize the impact of their message.

---

## 🏗️ Project Structure

- `app.py`: The main application logic, AI prompting, and UI rendering.
- `requirements.txt`: List of Python libraries needed (Streamlit, gTTS, Plotly, etc.).
- `.streamlit/secrets.toml`: (Should be created by user) Stores your Hugging Face API Token.

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
   Create a folder named `.streamlit` and a file inside it named `secrets.toml`:

   ```toml
   HUGGING_FACE_API_KEY = "your_hf_token_here"
   ```

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

---

_Crafted for efficiency. Refined for impact. Built to Resonate._
