# Quick Start Guide

## 1. Activate the Environment

```bash
cd "/home/distiller/projects/voice cloning"
source venv/bin/activate
```

## 2. First Test - Check if XTTS Works

Let's try to load the model:

```bash
python -c "
import warnings
warnings.filterwarnings('ignore')
from TTS.api import TTS
print('Loading XTTS v2...')
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
print('✅ Success! XTTS is ready.')
"
```

**Expected:**
- First run will download ~2GB of models (1-3 minutes)
- If you see "Success!", you're ready to go!

**If you see pandas/numpy error:**
- This is the known issue - see workarounds below

## 3. Try the Voice Cloning Script

### Option A: Record & Clone (Full Pipeline)

```bash
python voice_clone.py --mode full --text "Hello, this is my cloned voice speaking!"
```

This will:
1. Prompt you to speak for 10 seconds
2. Clone your voice
3. Generate the text in your voice
4. Play it back

### Option B: Use an Existing Audio File

If you have a WAV file:

```bash
python voice_clone.py --mode clone \
  --reference /path/to/audio.wav \
  --text "Your text here" \
  --output my_clone.wav
```

### Option C: Just Record Reference Audio

```bash
python voice_clone.py --mode record --duration 10 --reference my_voice.wav
```

## 4. Common Commands

```bash
# See all options
python voice_clone.py --help

# Clone without auto-play
python voice_clone.py --mode clone \
  --reference my_voice.wav \
  --text "Testing voice cloning" \
  --no-play

# Generate in Spanish
python voice_clone.py --mode clone \
  --reference spanish_voice.wav \
  --text "Hola, ¿cómo estás?" \
  --language es
```

## 5. If You Hit the Pandas Error

The pandas/numpy incompatibility prevents TTS from loading. Here are workarounds:

### Workaround 1: Try a Direct XTTS Import (Bypass TTS API)

Create a file `test_direct.py`:

```python
import torch
import torchaudio
from TTS.tts.models.xtts import Xtts

# Load model directly
model = Xtts.init_from_config("path/to/config")
# Use for inference
```

### Workaround 2: Use System Python Packages

```bash
deactivate
sudo apt-get update
sudo apt-get install python3-pandas python3-numpy python3-torch
# Try again without venv
```

### Workaround 3: Rebuild Pandas

```bash
source venv/bin/activate
pip uninstall pandas
pip install --no-binary :all: pandas<2.0
# This will take 10-20 minutes to compile
```

## 6. Alternative: Use Piper TTS (Already on Device)

If XTTS doesn't work, you can use the built-in Piper TTS:

```python
from distiller_cm5_sdk.piper import Piper

tts = Piper()
tts.speak("Hello from Piper!")
```

Piper is faster but requires pre-trained voice models (no zero-shot cloning).

## Next Steps

Once working:
1. Record a good 10-second reference sample (clear, expressive speech)
2. Test with different texts
3. Experiment with different languages
4. Adjust the script for your needs

## Need Help?

Check SETUP_NOTES.md for detailed troubleshooting, or let me know what error you're seeing!
