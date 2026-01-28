# Voice Profiles API Documentation

The voice cloning system now supports **Voice Profiles** - allowing you to create named voices with multiple training samples for better quality cloning.

## Features

- ✅ Create named voice profiles
- ✅ Add multiple audio samples (10-second clips) to each profile
- ✅ Select which profile to use for voice generation
- ✅ Delete profiles you don't want
- ✅ Rename profiles
- ✅ Remove individual samples from profiles

## API Endpoints

### List All Profiles
```
GET /api/profiles
```

**Response:**
```json
{
  "success": true,
  "profiles": [
    {
      "profile_id": "profile_20260128_123456",
      "name": "My Voice",
      "samples": ["sample1.wav", "sample2.wav"],
      "sample_count": 2,
      "created_at": "2026-01-28T12:34:56"
    }
  ]
}
```

### Create New Profile
```
POST /api/profiles/create
Content-Type: application/json

{
  "name": "My Voice"
}
```

### Add Sample to Profile
```
POST /api/profiles/{profile_id}/add_sample
Content-Type: application/json

{
  "audio_file": "reference_123456.wav"
}
```

**Workflow:**
1. Upload audio file using `/api/upload`
2. Add the uploaded file to a profile using this endpoint

### Remove Sample from Profile
```
POST /api/profiles/{profile_id}/remove_sample
Content-Type: application/json

{
  "audio_file": "reference_123456.wav"
}
```

### Delete Profile
```
POST /api/profiles/{profile_id}/delete
```

### Rename Profile
```
POST /api/profiles/{profile_id}/rename
Content-Type: application/json

{
  "new_name": "New Voice Name"
}
```

### Clone Voice with Profile
```
POST /api/clone_with_profile
Content-Type: application/json

{
  "profile_id": "profile_20260128_123456",
  "text": "Hello, this is my cloned voice!",
  "language": "en"
}
```

## Python Usage Example

```python
import requests

BASE_URL = "http://localhost:5001"

# 1. Create a new voice profile
response = requests.post(f"{BASE_URL}/api/profiles/create",
    json={"name": "My Voice"})
profile = response.json()['profile']
profile_id = profile['profile_id']
print(f"Created profile: {profile_id}")

# 2. Upload audio files
files_to_upload = ["clip1.wav", "clip2.wav", "clip3.wav"]
for audio_file in files_to_upload:
    # Upload file
    with open(audio_file, 'rb') as f:
        upload_response = requests.post(
            f"{BASE_URL}/api/upload",
            files={'file': f}
        )
    uploaded_filename = upload_response.json()['filename']

    # Add to profile
    requests.post(
        f"{BASE_URL}/api/profiles/{profile_id}/add_sample",
        json={"audio_file": uploaded_filename}
    )
    print(f"Added sample: {uploaded_filename}")

# 3. Generate speech with the profile
response = requests.post(f"{BASE_URL}/api/clone_with_profile",
    json={
        "profile_id": profile_id,
        "text": "Hello! This is my cloned voice.",
        "language": "en"
    })

if response.json()['success']:
    output_url = response.json()['download_url']
    print(f"Generated audio: {output_url}")

# 4. List all profiles
response = requests.get(f"{BASE_URL}/api/profiles")
profiles = response.json()['profiles']
for p in profiles:
    print(f"Profile: {p['name']} ({p['sample_count']} samples)")

# 5. Delete a profile
requests.post(f"{BASE_URL}/api/profiles/{profile_id}/delete")
print("Profile deleted")
```

## JavaScript/Browser Usage

```javascript
// Create profile
async function createProfile(name) {
    const response = await fetch('/api/profiles/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    });
    return await response.json();
}

// Upload and add sample
async function addSampleToProfile(profileId, file) {
    // Upload file first
    const formData = new FormData();
    formData.append('file', file);

    const uploadResp = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    const uploadData = await uploadResp.json();

    // Add to profile
    const addResp = await fetch(`/api/profiles/${profileId}/add_sample`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({audio_file: uploadData.filename})
    });
    return await addResp.json();
}

// Generate with profile
async function cloneWithProfile(profileId, text, language = 'en') {
    const response = await fetch('/api/clone_with_profile', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({profile_id: profileId, text, language})
    });
    return await response.json();
}

// List profiles
async function listProfiles() {
    const response = await fetch('/api/profiles');
    const data = await response.json();
    return data.profiles;
}

// Delete profile
async function deleteProfile(profileId) {
    const response = await fetch(`/api/profiles/${profileId}/delete`, {
        method: 'POST'
    });
    return await response.json();
}
```

## Command-Line Usage

```bash
# Create a profile
curl -X POST http://localhost:5001/api/profiles/create \
  -H "Content-Type: application/json" \
  -d '{"name": "My Voice"}'

# Upload audio file
curl -X POST http://localhost:5001/api/upload \
  -F "file=@my_voice_clip1.wav"

# Add sample to profile
curl -X POST http://localhost:5001/api/profiles/profile_20260128_123456/add_sample \
  -H "Content-Type: application/json" \
  -d '{"audio_file": "reference_1234567890.wav"}'

# Generate speech
curl -X POST http://localhost:5001/api/clone_with_profile \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "profile_20260128_123456",
    "text": "Hello from my cloned voice!",
    "language": "en"
  }'

# List all profiles
curl http://localhost:5001/api/profiles

# Delete profile
curl -X POST http://localhost:5001/api/profiles/profile_20260128_123456/delete
```

## Best Practices

### Multiple Samples
- Upload 3-5 audio clips of 10-30 seconds each
- Use different sentences/expressions for variety
- All samples should be from the same voice
- Ensure consistent audio quality

### Audio Quality
- Use clean, noise-free recordings
- WAV format at 22050Hz or higher
- Clear speech without background music
- Consistent volume levels

### Profile Organization
- Use descriptive names ("John's Voice", "Female Narrator", etc.)
- Delete profiles you're not satisfied with
- Test with short phrases before long generations

## Storage

Voice profiles are stored in:
```
voice_profiles/
├── profiles.json                 # Profile metadata
├── profile_20260128_123456/      # Profile directory
│   ├── reference_111.wav         # Sample 1
│   ├── reference_222.wav         # Sample 2
│   └── reference_333.wav         # Sample 3
└── profile_20260128_234567/
    └── reference_444.wav
```

## Migration from Single-File Mode

If you have existing reference files in `uploads/`, you can:

1. Create a new profile
2. Add your existing uploads to the profile
3. Use the profile for generation

The old single-file API (`/api/clone`) still works for backward compatibility.

## Troubleshooting

**Profile not found**
- Check profile ID is correct
- Use `/api/profiles` to list all profiles

**No samples in profile**
- Upload files first with `/api/upload`
- Add them to profile with `/api/profiles/{id}/add_sample`

**Poor quality output**
- Add more varied samples (3-5 recommended)
- Ensure all samples are clear and high quality
- Try different sample combinations

## Future Enhancements

Potential features being considered:
- Combine multiple samples for better quality
- Voice profile sharing/export
- Sample quality analysis
- Automatic sample selection based on text
