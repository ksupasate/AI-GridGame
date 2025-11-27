import streamlit as st
from src.prompts import MODES, build_prompt
from src.openai_client import analyze_image, generate_speech
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

st.set_page_config(
    page_title="AI ช่วยเล่นเกม",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Reset and base styles */
    * {
        -webkit-tap-highlight-color: transparent;
    }

    .stApp {
        max-width: 100%;
        padding: 0;
    }

    /* Mobile-first responsive design */
    .block-container {
        padding: 1rem !important;
        max-width: 100% !important;
    }

    /* Large touch targets for mobile */
    .stButton button {
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 1rem !important;
        width: 100% !important;
        min-height: 56px !important;
        border-radius: 12px !important;
        margin: 0.5rem 0 !important;
    }

    /* Camera input optimization */
    [data-testid="stCameraInput"] {
        width: 100% !important;
    }

    [data-testid="stCameraInput"] button {
        width: 100% !important;
        min-height: 56px !important;
        font-size: 18px !important;
    }

    /* Results display */
    .analysis-result {
        background: #1a1a1a;
        color: #00ff00;
        padding: 1.5rem;
        border-radius: 12px;
        font-family: 'Courier New', monospace;
        font-size: 16px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 1rem 0;
        border: 2px solid #00ff00;
    }

    /* Large readable text */
    .large-text {
        font-size: 18px;
        line-height: 1.6;
    }

    .large-text li {
        margin: 0.8rem 0;
        font-size: 16px;
    }

    /* Mobile header */
    h1 {
        font-size: 24px !important;
        margin-bottom: 0.5rem !important;
    }

    h3 {
        font-size: 18px !important;
    }

    /* Sidebar optimization for mobile */
    [data-testid="stSidebar"] {
        background: #0e1117;
    }

    /* Input fields */
    .stTextInput input {
        font-size: 16px !important;
        padding: 1rem !important;
        min-height: 48px !important;
    }

    .stSelectbox select {
        font-size: 16px !important;
        padding: 1rem !important;
    }

    /* Status indicators */
    .stSuccess, .stError, .stWarning, .stInfo {
        font-size: 16px !important;
        padding: 1rem !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
    }

    /* Expandable sections */
    .streamlit-expanderHeader {
        font-size: 16px !important;
        padding: 1rem !important;
    }

    /* Audio player */
    audio {
        width: 100% !important;
        margin: 1rem 0 !important;
    }

    /* Spinner */
    .stSpinner {
        text-align: center;
    }

    /* Tablet optimization (portrait) */
    @media (min-width: 768px) {
        .block-container {
            padding: 2rem !important;
            max-width: 640px !important;
            margin: 0 auto !important;
        }

        h1 {
            font-size: 32px !important;
        }
    }

    /* Desktop */
    @media (min-width: 1024px) {
        .block-container {
            max-width: 720px !important;
        }
    }

    /* Very small phones */
    @media (max-width: 360px) {
        .block-container {
            padding: 0.5rem !important;
        }

        h1 {
            font-size: 20px !important;
        }

        .stButton button {
            font-size: 16px !important;
            padding: 0.8rem !important;
        }
    }

    /* Landscape mode */
    @media (orientation: landscape) and (max-height: 500px) {
        .block-container {
            padding: 0.5rem !important;
        }

        h1 {
            font-size: 20px !important;
            margin-bottom: 0.25rem !important;
        }
    }

    /* iOS Safari fixes */
    @supports (-webkit-touch-callout: none) {
        .stButton button {
            -webkit-appearance: none;
        }

        input, select {
            -webkit-appearance: none;
            border-radius: 8px;
        }
    }

    /* Dark mode optimization */
    @media (prefers-color-scheme: dark) {
        .analysis-result {
            background: #0a0a0a;
        }
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'last_image_hash' not in st.session_state:
    st.session_state['last_image_hash'] = None
if 'capture_count' not in st.session_state:
    st.session_state['capture_count'] = 0
if 'error_count' not in st.session_state:
    st.session_state['error_count'] = 0
if 'auto_process' not in st.session_state:
    st.session_state['auto_process'] = True
if 'voice_instructions_played' not in st.session_state:
    st.session_state['voice_instructions_played'] = False

def create_voice_instruction(text, api_key):
    """Generate voice instructions"""
    try:
        return generate_speech(text, api_key)
    except:
        return None

# Sidebar (collapsed by default on mobile)
with st.sidebar:
    st.header("⚙️ การตั้งค่า")

    default_key = os.getenv('OPENAI_API_KEY', '')
    api_key = st.text_input(
        "🔑 API Key",
        value=default_key,
        type="password",
        placeholder="sk-...",
        key="api_key_input",
        help="ใส่ OpenAI API Key"
    )

    mode = st.selectbox(
        "📊 โหมดการวิเคราะห์",
        list(MODES.keys()),
        index=0,
        key="mode_select",
        help="เลือกรูปแบบการวิเคราะห์"
    )

    st.markdown("---")

    st.session_state['auto_process'] = st.checkbox(
        "⚡ ประมวลผลอัตโนมัติ",
        value=st.session_state.get('auto_process', True),
        help="วิเคราะห์และพูดทันทีที่ถ่ายรูป"
    )

    if st.session_state['capture_count'] > 0:
        st.metric("✅ วิเคราะห์แล้ว", st.session_state['capture_count'])
        if st.session_state['error_count'] > 0:
            st.metric("❌ ข้อผิดพลาด", st.session_state['error_count'])

    st.markdown("---")

    if st.button("🔊 ฟังคำแนะนำ", use_container_width=True):
        if api_key:
            instructions = """
            ยินดีต้อนรับสู่แอพ เอไอ ช่วยเล่นเกม

            วิธีใช้งาน:
            1. กดปุ่มถ่ายรูป
            2. จัดมุมกล้องให้เห็นกระดาน
            3. กดปุ่มถ่าย
            4. ฟังคำแนะนำทันที

            เริ่มใช้งานได้เลย
            """
            audio = create_voice_instruction(instructions, api_key)
            if audio:
                st.audio(audio, format="audio/mpeg", autoplay=True)
        else:
            st.warning("กรุณาใส่ API Key ก่อน")

    st.caption("🎮 AI Game Helper")
    st.caption("📱 รองรับทุกอุปกรณ์")

# Main content
st.title("🎮 AI ช่วยเล่นเกม")

if not api_key:
    st.error("⚠️ กรุณาเปิด Sidebar ด้านซ้ายและใส่ API Key")
    st.info("👈 กดที่ลูกศรมุมซ้ายบนเพื่อเปิด Sidebar")
    st.stop()

# Welcome voice (only once)
if not st.session_state['voice_instructions_played'] and api_key:
    welcome = "ยินดีต้อนรับ กดปุ่มถ่ายรูปด้านล่างเพื่อเริ่มต้น"
    audio = create_voice_instruction(welcome, api_key)
    if audio:
        st.audio(audio, format="audio/mpeg", autoplay=True)
        st.session_state['voice_instructions_played'] = True

# Instructions
st.markdown("""
<div class="large-text">
    <p><strong>📸 วิธีใช้ง่ายๆ:</strong></p>
    <ol>
        <li>📷 กดปุ่ม "Take Photo" ด้านล่าง</li>
        <li>🎯 จัดมุมกล้องให้เห็นกระดานชัดเจน</li>
        <li>📸 กดปุ่มถ่ายรูป</li>
        <li>🔊 ฟังคำแนะนำทันที</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Tips expander
with st.expander("💡 เทคนิคการใช้งาน"):
    st.markdown("""
    **สำหรับมือถือ:**
    - ✅ ถ่ายในที่แสงสว่างเพียงพอ
    - ✅ จับมือถือให้มั่นคง
    - ✅ กระดานต้องอยู่ในกรอบชัดเจน
    - ✅ หลีกเลี่ยงเงาบดกระดาน

    **ประหยัดแบตเตอรี่:**
    - 🔋 ลดความสว่างหน้าจอ
    - 🔋 ปิดการถ่ายซ้ำถ้าไม่จำเป็น

    **เน็ตช้า:**
    - 📶 ถ่ายรูปครั้งเดียว รอให้เสร็จ
    - 📶 อย่ากดถ่ายซ้ำจนกว่าจะเสร็จ
    """)

# Camera input with mobile optimization
st.markdown("---")
camera_photo = st.camera_input(
    "📷 กล้อง",
    key="camera",
    help="กดปุ่มนี้เพื่อถ่ายรูปกระดาน (ใช้ได้ทั้งกล้องหน้าและหลัง)"
)

if camera_photo:
    photo_bytes = camera_photo.getvalue()
    current_hash = hashlib.sha256(photo_bytes).hexdigest()

    # Check if new photo
    if current_hash != st.session_state.get('last_image_hash'):
        st.session_state['last_image_hash'] = current_hash

        if st.session_state['auto_process']:
            # Processing feedback
            processing_audio = create_voice_instruction("กำลังวิเคราะห์ กรุณารอสักครู่", api_key)
            if processing_audio:
                st.audio(processing_audio, format="audio/mpeg", autoplay=True)

            with st.spinner("🔍 กำลังวิเคราะห์... (อาจใช้เวลา 5-15 วินาที)"):
                try:
                    # Analyze
                    prompt = build_prompt(mode)
                    analysis_result = analyze_image(photo_bytes, prompt, api_key)
                    st.session_state['analysis_result'] = analysis_result
                    st.session_state['capture_count'] += 1
                    st.session_state['error_count'] = 0

                    # Generate speech
                    audio_bytes = generate_speech(analysis_result, api_key)

                    # Success
                    st.success(f"✅ วิเคราะห์สำเร็จ! (ครั้งที่ {st.session_state['capture_count']})")

                    # Play audio
                    st.audio(audio_bytes, format="audio/mpeg", autoplay=True)

                    # Show text
                    st.markdown(
                        f"""<div class="analysis-result">
                        <strong>📋 ผลการวิเคราะห์:</strong><br><br>
                        {analysis_result}
                        </div>""",
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.session_state['error_count'] += 1
                    error_msg = str(e)

                    # User-friendly error messages
                    if "rate_limit" in error_msg.lower():
                        st.error("⚠️ ใช้งานถี่เกินไป กรุณารอ 1 นาที แล้วลองใหม่")
                    elif "insufficient_quota" in error_msg.lower():
                        st.error("⚠️ API Key หมดโควต้า กรุณาเติมเงินใน OpenAI")
                    elif "invalid" in error_msg.lower():
                        st.error("⚠️ API Key ไม่ถูกต้อง กรุณาตรวจสอบ")
                    else:
                        st.error(f"❌ เกิดข้อผิดพลาด: {error_msg}")

                    # Voice error
                    error_audio = create_voice_instruction(
                        "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง",
                        api_key
                    )
                    if error_audio:
                        st.audio(error_audio, format="audio/mpeg", autoplay=True)

else:
    st.info("👆 กดปุ่ม Take Photo เพื่อเริ่มต้น")

# Show last result
if st.session_state.get('analysis_result') and not camera_photo:
    st.markdown("---")
    st.markdown("### 📝 ผลล่าสุด:")
    st.markdown(
        f"""<div class="analysis-result">
        {st.session_state['analysis_result']}
        </div>""",
        unsafe_allow_html=True
    )

    # Replay button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 ฟังอีกครั้ง", use_container_width=True):
            audio = create_voice_instruction(st.session_state['analysis_result'], api_key)
            if audio:
                st.audio(audio, format="audio/mpeg", autoplay=True)

    with col2:
        if st.button("🗑️ ลบผล", use_container_width=True):
            st.session_state['analysis_result'] = None
            st.rerun()


