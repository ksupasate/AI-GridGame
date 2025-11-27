import streamlit as st
import time
from datetime import datetime

def auto_capture_with_camera_input():
    """
    Simplified auto-capture using st.camera_input with auto-refresh.
    Returns captured image bytes or None.
    """

    if 'last_capture_time' not in st.session_state:
        st.session_state['last_capture_time'] = None
    if 'pending_capture' not in st.session_state:
        st.session_state['pending_capture'] = None

    interval = st.session_state.get('capture_interval', 5)

    camera_photo = st.camera_input(
        "📸 กล้อง - ถ่ายภาพใหม่เพื่อวิเคราะห์",
        key="camera_auto"
    )

    if camera_photo:
        photo_bytes = camera_photo.getvalue()
        current_time = datetime.now()

        if st.session_state['last_capture_time'] is None:
            st.session_state['last_capture_time'] = current_time
            st.session_state['pending_capture'] = photo_bytes
            return photo_bytes

        time_since_last = (current_time - st.session_state['last_capture_time']).total_seconds()

        if time_since_last >= interval or photo_bytes != st.session_state.get('pending_capture'):
            st.session_state['last_capture_time'] = current_time
            st.session_state['pending_capture'] = photo_bytes
            return photo_bytes

    return None
