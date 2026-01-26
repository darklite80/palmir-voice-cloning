# Voice Cloning Web GUI

A beautiful, easy-to-use web interface for XTTS v2 voice cloning on your Palmir device.

## Features

✨ **Drag & Drop Upload** - Simply drag audio files into the browser
🎤 **Direct Recording** - Record reference audio directly from Palmir's microphone
🌍 **17+ Languages** - Support for English, Spanish, French, German, and more
🎭 **Real-time Cloning** - Generate cloned voices in seconds
📥 **Easy Downloads** - Download generated audio with one click
📱 **Responsive Design** - Works on desktop, tablet, and mobile

## Quick Start

### 1. Start the Web Server

```bash
cd "/home/distiller/projects/voice cloning"
./start_web.sh
```

Or manually:

```bash
source venv/bin/activate
python web_app.py
```

### 2. Open in Browser

**On the same device:**
```
http://localhost:8080
```

**From another device on your network:**
```
http://<palmir-ip-address>:8080
```

Find your IP with: `hostname -I | awk '{print $1}'`

### 3. Start Cloning!

1. **Upload or Record** reference audio (6-10 seconds of clear speech)
2. **Enter text** you want the voice to speak
3. **Select language**
4. **Click "Generate"** and wait 10-30 seconds
5. **Listen and download** your cloned voice!

## How to Use

### Upload Reference Audio

**Method 1: Drag & Drop**
- Drag any audio file (WAV, MP3, OGG, FLAC, M4A) into the upload area
- File automatically converts to WAV format if needed

**Method 2: Browse Files**
- Click the upload area
- Select your audio file

**Method 3: Record**
- Switch to "Record" tab
- Set duration (5-60 seconds)
- Click "Start Recording"
- Speak clearly into Palmir's microphone

### Clone a Voice

1. Make sure reference audio is selected (green border shows selected file)
2. Enter the text you want to speak
3. Choose the language
4. Click "Generate Cloned Voice"
5. Wait for processing (status shown at top)
6. Play the result or download it

### Tips for Best Results

**Reference Audio:**
- Use 6-10 seconds of clear speech
- Avoid background noise
- Include emotional variety for better clones
- Mono audio at 22050 Hz is ideal (but any format works)

**Text Generation:**
- Shorter texts generate faster
- Use natural punctuation for better prosody
- XTTS handles complex sentences well

**Languages:**
- English (en) works best
- Match the reference audio language for best results
- Can clone cross-language (e.g., English voice speaking Spanish)

## API Endpoints

The web interface exposes these REST APIs:

### Status
```
GET /api/status
```
Returns model loading status

### Upload File
```
POST /api/upload
Form-data: file
```
Upload reference audio file

### Record Audio
```
POST /api/record
JSON: {duration: 10}
```
Record from Palmir microphone

### Clone Voice
```
POST /api/clone
JSON: {
  reference_file: "reference_xxx.wav",
  text: "Text to speak",
  language: "en"
}
```
Generate cloned voice

### List Files
```
GET /api/files
```
List uploaded and generated files

### Download
```
GET /download/<filename>
```
Download generated audio

## File Structure

```
uploads/          - Uploaded reference audio files
outputs/          - Generated cloned voice files
templates/        - HTML templates
static/           - CSS/JS assets (auto-generated)
web_app.py        - Flask application
start_web.sh      - Startup script
```

## Configuration

Edit `web_app.py` to change:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max file size
app.run(host='0.0.0.0', port=5000, debug=True)        # Server settings
```

## Troubleshooting

### Model Won't Load

**Symptom:** Status shows "Error" with pandas/numpy message

**Solution 1:** Try loading via button
- Click "Load Model" button in top status bar
- Wait 1-3 minutes for first download

**Solution 2:** Pre-load model
```bash
source venv/bin/activate
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"
```

**Solution 3:** Apply pandas workaround (see SETUP_NOTES.md)

### Can't Access from Another Device

**Check firewall:**
```bash
sudo ufw allow 5000
```

**Check IP address:**
```bash
hostname -I
```

**Try explicit binding:**
Edit `web_app.py`, change `host='0.0.0.0'` to `host='192.168.x.x'` (your actual IP)

### Upload Fails

- Check file size (max 100MB by default)
- Ensure file format is supported (WAV, MP3, OGG, FLAC, M4A)
- Check disk space: `df -h`

### Recording Fails

- Verify Palmir audio hardware:
```bash
source /opt/distiller-cm5-sdk/activate.sh
python -c "from distiller_cm5_sdk.hardware.audio import Audio; Audio()"
```

- Check microphone permissions
- Ensure no other process is using the microphone

### Voice Cloning is Slow

**Normal:** 10-30 seconds per sentence on Raspberry Pi CM5
- Shorter texts are faster
- First generation takes longer (model warm-up)

**Too slow?**
- Close other applications
- Reduce text length
- Monitor CPU: `htop`

## Security Notes

**⚠️ This is a development server!**

For production use:
1. Change `SECRET_KEY` in `web_app.py`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Add authentication
4. Use HTTPS
5. Set `debug=False`

## Example Use Cases

### Voice Assistant
Clone your voice and use it for custom TTS responses

### Audiobook Production
Clone narrator voices for consistency

### Language Learning
Hear how your voice sounds in different languages

### Content Creation
Generate voiceovers in your own voice

### Accessibility
Create personalized voice for communication devices

## Advanced Usage

### Batch Processing

Upload multiple reference files and generate variations:

1. Upload several reference audio samples
2. Use the "Reference Files" list to switch between them
3. Generate the same text with different voice references
4. Compare results

### API Integration

Use the REST API in your own applications:

```python
import requests

# Upload file
files = {'file': open('voice.wav', 'rb')}
r = requests.post('http://localhost:8080/api/upload', files=files)
ref_file = r.json()['filename']

# Clone voice
data = {
    'reference_file': ref_file,
    'text': 'Hello world',
    'language': 'en'
}
r = requests.post('http://localhost:8080/api/clone', json=data)
output_url = r.json()['download_url']
```

## Performance Tuning

### Speed Up Inference

```python
# Edit web_app.py, add to model loading:
tts_model = TTS('...', gpu=False)  # CPU mode
# For future GPU support, change to gpu=True
```

### Reduce Memory Usage

```python
# Lower batch size in config (advanced)
# Edit XTTS config if needed
```

## Support

- Check `SETUP_NOTES.md` for installation issues
- See `README.md` for CLI usage
- See `QUICKSTART.md` for getting started

## Credits

- **XTTS v2** by Coqui AI
- **Palmir SDK** integration
- Built with Flask and modern HTML/CSS/JS

Enjoy your voice cloning studio! 🎙️✨
