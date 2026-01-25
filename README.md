# XTTS v2 Voice Cloning for Palmir Device

Local voice cloning using Coqui TTS XTTS v2 on your Raspberry Pi CM5.

## Features

- 🎙️ **Zero-shot voice cloning** - Clone any voice from 6-10 seconds of audio
- 🌍 **Multilingual** - Supports 17+ languages
- 🔊 **Integrated with Palmir hardware** - Uses device microphone and speakers
- 💻 **Fully local** - No internet required after setup
- 🚀 **Easy to use** - Simple CLI interface

## Installation

The environment is already set up! Just activate it:

```bash
cd "/home/distiller/projects/voice cloning"
source venv/bin/activate
```

## Usage

### Quick Start (Full Pipeline)

Record your voice and generate cloned speech in one command:

```bash
python voice_clone.py --mode full --text "Hello, this is my cloned voice!"
```

This will:
1. Record 10 seconds of your voice as reference
2. Clone your voice and generate the specified text
3. Play back the result

### Step-by-Step Usage

#### 1. Record Reference Audio

```bash
python voice_clone.py --mode record --duration 10 --reference my_voice.wav
```

Speak naturally for the duration. The more expressive, the better!

#### 2. Clone Voice and Generate Speech

```bash
python voice_clone.py --mode clone \
  --reference my_voice.wav \
  --text "This is the text I want to speak in the cloned voice" \
  --output output.wav
```

### Advanced Options

```bash
python voice_clone.py \
  --mode clone \
  --reference voice_reference.wav \
  --text "Your text here" \
  --output generated.wav \
  --language en \
  --no-play  # Don't auto-play the result
```

### Supported Languages

- **English**: `en`
- **Spanish**: `es`
- **French**: `fr`
- **German**: `de`
- **Italian**: `it`
- **Portuguese**: `pt`
- **Polish**: `pl`
- **Turkish**: `tr`
- **Russian**: `ru`
- **Dutch**: `nl`
- **Czech**: `cs`
- **Arabic**: `ar`
- **Chinese**: `zh-cn`
- **Japanese**: `ja`
- **Hungarian**: `hu`
- **Korean**: `ko`
- **Hindi**: `hi`

## Performance

On Raspberry Pi CM5 (ARM64, 4-core):
- **First run**: ~2-3 minutes (downloads models)
- **Voice cloning**: ~10-30 seconds per sentence
- **RAM usage**: ~3-4GB during inference
- **Quality**: Near-human naturalness

## Tips for Best Results

1. **Reference audio quality**:
   - Use 6-10 seconds of clear speech
   - Avoid background noise
   - Include emotional variety if possible

2. **Text generation**:
   - Shorter sentences generate faster
   - Natural punctuation improves prosody
   - XTTS handles complex text well

3. **Performance**:
   - First generation takes longer (model loading)
   - Subsequent generations are faster
   - CPU mode is slower but works well

## Troubleshooting

### Model download fails
First run downloads ~2GB of models. Ensure good internet connection:
```bash
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"
```

### Audio hardware issues
Test Palmir audio separately:
```bash
source /opt/distiller-cm5-sdk/activate.sh
python -c "from distiller_cm5_sdk.hardware.audio import Audio; a = Audio(); print('Audio OK')"
```

### Out of memory
Close other applications or reduce text length.

## Examples

### Clone your voice
```bash
# Record yourself
python voice_clone.py --mode record --duration 10

# Generate speech
python voice_clone.py --mode clone \
  --text "I can now speak any text in my own voice!"
```

### Use existing audio file
```bash
# Clone from any WAV file
python voice_clone.py --mode clone \
  --reference /path/to/audio.wav \
  --text "The quick brown fox jumps over the lazy dog"
```

### Multiple languages
```bash
# Generate in Spanish
python voice_clone.py --mode clone \
  --reference spanish_speaker.wav \
  --text "Hola, ¿cómo estás?" \
  --language es
```

## Architecture

- **TTS Engine**: Coqui TTS XTTS v2
- **Backend**: PyTorch (CPU mode)
- **Audio I/O**: Palmir SDK (ALSA)
- **Sample Rate**: 22050 Hz
- **Format**: WAV (16-bit PCM)

## License

This tool uses Coqui TTS, which is open source. Check their license for commercial use.
