#!/usr/bin/env python3
"""
Web GUI for XTTS v2 Voice Cloning
Provides easy file upload and voice cloning interface
"""

import os
import sys
import warnings
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename

warnings.filterwarnings('ignore')

# Add Palmir SDK to path
sys.path.insert(0, '/opt/distiller-cm5-sdk')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['SECRET_KEY'] = 'voice-cloning-secret-key-change-in-production'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'pl': 'Polish',
    'tr': 'Turkish',
    'ru': 'Russian',
    'nl': 'Dutch',
    'cs': 'Czech',
    'ar': 'Arabic',
    'zh-cn': 'Chinese',
    'ja': 'Japanese',
    'hu': 'Hungarian',
    'ko': 'Korean',
    'hi': 'Hindi'
}

# Global TTS instance (lazy loaded)
tts_model = None
model_loading = False
model_error = None


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_tts_model():
    """Load TTS model (lazy loading)."""
    global tts_model, model_loading, model_error

    if tts_model is not None:
        return tts_model

    if model_loading:
        return None

    model_loading = True
    try:
        print("Loading XTTS v2 model...")
        from TTS.api import TTS
        tts_model = TTS('tts_models/multilingual/multi-dataset/xtts_v2', progress_bar=False)
        print("✅ Model loaded successfully!")
        model_loading = False
        return tts_model
    except Exception as e:
        model_error = str(e)
        model_loading = False
        print(f"❌ Error loading model: {e}")
        return None


def convert_to_wav(input_path, output_path):
    """Convert audio file to WAV format if needed."""
    try:
        import soundfile as sf
        import librosa

        # Load audio with librosa (supports many formats)
        audio, sr = librosa.load(input_path, sr=22050, mono=True)

        # Save as WAV
        sf.write(output_path, audio, sr, subtype='PCM_16')
        return True
    except Exception as e:
        print(f"Error converting audio: {e}")
        return False


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html', languages=LANGUAGES)


@app.route('/api/status')
def status():
    """Get model loading status."""
    global model_loading, model_error, tts_model

    if tts_model is not None:
        return jsonify({'status': 'ready', 'message': 'Model loaded and ready'})
    elif model_loading:
        return jsonify({'status': 'loading', 'message': 'Loading XTTS v2 model...'})
    elif model_error:
        return jsonify({'status': 'error', 'message': f'Error: {model_error}'})
    else:
        return jsonify({'status': 'idle', 'message': 'Model not loaded'})


@app.route('/api/load_model', methods=['POST'])
def load_model():
    """Load the TTS model."""
    model = load_tts_model()
    if model:
        return jsonify({'success': True, 'message': 'Model loaded successfully'})
    elif model_loading:
        return jsonify({'success': False, 'message': 'Model is loading, please wait...'})
    else:
        return jsonify({'success': False, 'message': f'Failed to load model: {model_error}'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload reference audio file."""
    try:
        print(f"Upload request received. Files: {request.files.keys()}")

        if 'file' not in request.files:
            print("ERROR: No 'file' in request.files")
            return jsonify({'success': False, 'message': 'No file provided'})

        file = request.files['file']
        print(f"File received: {file.filename}")

        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({'success': False, 'message': 'No file selected'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = int(time.time())
            base_name = f"reference_{timestamp}.wav"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], base_name)

            print(f"Saving to: {filepath}")

            # Save uploaded file
            temp_path = filepath + '.tmp'
            file.save(temp_path)
            print(f"File saved to temp: {temp_path}")

            # Convert to WAV if needed
            if filename.lower().endswith('.wav'):
                os.rename(temp_path, filepath)
                print("WAV file renamed")
            else:
                print(f"Converting {filename} to WAV...")
                if convert_to_wav(temp_path, filepath):
                    os.remove(temp_path)
                    print("Conversion successful")
                else:
                    print("ERROR: Conversion failed")
                    return jsonify({'success': False, 'message': 'Failed to convert audio to WAV format'})

            print(f"Upload complete: {base_name}")
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': base_name,
                'path': filepath
            })

        print(f"ERROR: Invalid file type for {file.filename}")
        return jsonify({'success': False, 'message': 'Invalid file type. Allowed: WAV, MP3, OGG, FLAC, M4A'})

    except Exception as e:
        print(f"ERROR in upload_file: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Upload error: {str(e)}'})


@app.route('/api/clone', methods=['POST'])
def clone_voice():
    """Clone voice and generate speech."""
    data = request.json

    reference_file = data.get('reference_file')
    text = data.get('text', '')
    language = data.get('language', 'en')

    if not reference_file:
        return jsonify({'success': False, 'message': 'No reference file specified'})

    if not text:
        return jsonify({'success': False, 'message': 'No text provided'})

    reference_path = os.path.join(app.config['UPLOAD_FOLDER'], reference_file)
    if not os.path.exists(reference_path):
        return jsonify({'success': False, 'message': 'Reference file not found'})

    # Load model if not loaded
    model = load_tts_model()
    if not model:
        return jsonify({'success': False, 'message': f'Model not ready: {model_error or "Unknown error"}'})

    try:
        # Generate output filename
        timestamp = int(time.time())
        output_filename = f"cloned_{timestamp}.wav"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        # Generate speech
        print(f"Generating speech: '{text}' in {language}")
        model.tts_to_file(
            text=text,
            speaker_wav=reference_path,
            language=language,
            file_path=output_path
        )

        return jsonify({
            'success': True,
            'message': 'Voice cloned successfully',
            'output_file': output_filename,
            'download_url': url_for('download_file', filename=output_filename)
        })

    except Exception as e:
        print(f"Error during voice cloning: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Voice cloning failed: {str(e)}'})


@app.route('/api/record', methods=['POST'])
def record_audio():
    """Record audio from Palmir microphone."""
    data = request.json
    duration = data.get('duration', 10)

    try:
        from distiller_cm5_sdk.hardware.audio import Audio

        audio = Audio()
        timestamp = int(time.time())
        filename = f"reference_{timestamp}.wav"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        print(f"Recording {duration} seconds...")
        audio_data = audio.record_audio(duration=duration, sample_rate=22050)
        audio.save_recording(filepath, audio_data, sample_rate=22050)

        return jsonify({
            'success': True,
            'message': f'Recorded {duration} seconds',
            'filename': filename,
            'path': filepath
        })

    except Exception as e:
        print(f"Recording error: {e}")
        return jsonify({'success': False, 'message': f'Recording failed: {str(e)}'})


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated audio file."""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/files')
def list_files():
    """List uploaded reference files."""
    try:
        uploads = []
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.endswith('.wav'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f)
                uploads.append({
                    'name': f,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })

        outputs = []
        for f in os.listdir(app.config['OUTPUT_FOLDER']):
            if f.endswith('.wav'):
                filepath = os.path.join(app.config['OUTPUT_FOLDER'], f)
                outputs.append({
                    'name': f,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath),
                    'download_url': url_for('download_file', filename=f)
                })

        return jsonify({
            'success': True,
            'uploads': sorted(uploads, key=lambda x: x['modified'], reverse=True),
            'outputs': sorted(outputs, key=lambda x: x['modified'], reverse=True)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    PORT = 5001  # Change this to your desired port

    print("=" * 60)
    print("🎙️  XTTS v2 Voice Cloning Web Interface")
    print("=" * 60)
    print("\nStarting web server...")
    print(f"Open your browser to: http://localhost:{PORT}")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False, threaded=True)
