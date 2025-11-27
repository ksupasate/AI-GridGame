# AI Game Assistant (Streamlit)

A mobile-friendly Streamlit app that captures your board state, sends it to the OpenAI Vision API for analysis, and reads the guidance aloud so you can stay focused on the game.

## Features
- Camera capture via Streamlit (mobile-ready touch targets and layout)
- Vision analysis with `gpt-4o-mini` using tailored prompts for different coaching styles
- Text-to-speech output for hands-free guidance
- Lightweight setup with either `conda` or `pip`

## Quick start
Prerequisite: Python 3.11+

**Conda (recommended)**
```bash
conda env create -f environment.yml
conda activate ai-grid-guide
```

**pip**
```bash
pip install -r requirements.txt
```

## Configuration
Copy the example environment file and set your OpenAI API key (or enter it in the Streamlit sidebar at runtime):
```bash
cp .env.example .env
# then edit .env and set OPENAI_API_KEY
```

## Run the app
```bash
streamlit run streamlit_app.py
```
The app starts at `http://localhost:8501`.

## Usage
1. Provide your `OPENAI_API_KEY` in the sidebar (or via `.env`).
2. Choose an analysis mode that matches how you want the AI to coach you.
3. Tap **Take Photo**, frame the board, and capture.
4. Let the app analyze the image and listen to the spoken recommendations.

## Project structure
```
ai-grid-guide/
├── streamlit_app.py        # Streamlit UI
├── src/
│   ├── auto_processor.py   # Image hashing, rate limiting, and capture helpers
│   ├── openai_client.py    # OpenAI Vision and TTS helpers
│   ├── prompts.py          # Prompt builder and mode definitions
│   └── simple_capture.py   # Alternative capture helper using st.camera_input
├── requirements.txt
├── environment.yml
├── .env.example
└── README.md
```

## Notes
- Keep your API key private; do not commit real keys to version control.
- If you deploy to Streamlit Community Cloud, add `OPENAI_API_KEY` as a secret in the dashboard.
