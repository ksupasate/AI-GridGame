import base64
import io
from PIL import Image
import numpy as np
from datetime import datetime, timedelta
from .openai_client import analyze_image, generate_speech

class RateLimiter:
    def __init__(self, max_calls=10, period_seconds=60):
        self.max_calls = max_calls
        self.period = timedelta(seconds=period_seconds)
        self.calls = []

    def can_proceed(self):
        now = datetime.now()
        self.calls = [t for t in self.calls if now - t < self.period]
        return len(self.calls) < self.max_calls

    def record_call(self):
        self.calls.append(datetime.now())

    def get_wait_time(self):
        if not self.calls:
            return 0
        now = datetime.now()
        oldest_call = min(self.calls)
        wait_time = (oldest_call + self.period - now).total_seconds()
        return max(0, wait_time)

rate_limiter = RateLimiter(max_calls=10, period_seconds=60)

def compute_image_hash(image_bytes):
    """
    Compute perceptual hash for duplicate detection.
    Returns a string of 64 binary digits representing the image.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
        pixels = np.array(img).flatten()
        avg = pixels.mean()
        hash_bits = ['1' if p > avg else '0' for p in pixels]
        return ''.join(hash_bits)
    except Exception as e:
        print(f"Error computing image hash: {e}")
        return None

def image_similarity(hash1, hash2):
    """
    Calculate similarity between two image hashes.
    Returns a value between 0.0 (completely different) and 1.0 (identical).
    """
    if not hash1 or not hash2 or len(hash1) != len(hash2):
        return 0.0

    diff_bits = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    return 1.0 - (diff_bits / len(hash1))

def should_process_image(new_hash, last_hash, threshold=0.95):
    """
    Determine if a new image should be processed based on similarity to last image.
    """
    if not last_hash:
        return True

    similarity = image_similarity(new_hash, last_hash)
    return similarity < threshold

def dataurl_to_bytes(dataurl):
    """
    Convert data URL (data:image/jpeg;base64,...) to bytes.
    """
    try:
        header, encoded = dataurl.split(',', 1)
        return base64.b64decode(encoded)
    except Exception as e:
        print(f"Error converting data URL to bytes: {e}")
        return None

def process_capture(image_data, prompt, api_key):
    """
    Process a captured image: analyze and generate speech.

    Parameters:
    -----------
    image_data : str
        Base64 encoded image data URL
    prompt : str
        Analysis prompt
    api_key : str
        OpenAI API key

    Returns:
    --------
    dict : {
        'success': bool,
        'analysis': str,
        'audio': bytes,
        'image_hash': str,
        'error': str or None
    }
    """
    if not rate_limiter.can_proceed():
        wait_time = rate_limiter.get_wait_time()
        return {
            'success': False,
            'error': f'Rate limit exceeded. Please wait {int(wait_time)} seconds.',
            'analysis': None,
            'audio': None,
            'image_hash': None
        }

    try:
        image_bytes = dataurl_to_bytes(image_data)
        if not image_bytes:
            return {
                'success': False,
                'error': 'Failed to convert image data',
                'analysis': None,
                'audio': None,
                'image_hash': None
            }

        image_hash = compute_image_hash(image_bytes)

        rate_limiter.record_call()
        analysis_result = analyze_image(image_bytes, prompt, api_key)

        rate_limiter.record_call()
        audio_bytes = generate_speech(analysis_result, api_key)

        return {
            'success': True,
            'analysis': analysis_result,
            'audio': audio_bytes,
            'image_hash': image_hash,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'analysis': None,
            'audio': None,
            'image_hash': None
        }
