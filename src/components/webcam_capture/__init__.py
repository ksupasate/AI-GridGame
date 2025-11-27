import os
import streamlit.components.v1 as components

_RELEASE = True
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend")

_component_func = components.declare_component(
    "webcam_capture",
    path=build_dir,
)

def webcam_capture_component(key=None, active=False, interval_seconds=5, height=400):
    """
    Custom Streamlit component for auto-capturing webcam frames.

    Parameters:
    -----------
    key : str
        Unique key for the component
    active : bool
        Whether auto-capture is active
    interval_seconds : int
        Seconds between captures (default: 5)
    height : int
        Component height in pixels (default: 400)

    Returns:
    --------
    dict or None
        {
            'type': 'capture' | 'error',
            'data': str (base64 image data URL),
            'timestamp': int (milliseconds),
            'message': str (error message if type='error')
        }
    """
    component_value = _component_func(
        active=active,
        interval_seconds=interval_seconds,
        key=key,
        default=None,
        height=height
    )

    return component_value

__all__ = ['webcam_capture_component']
