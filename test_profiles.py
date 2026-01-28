#!/usr/bin/env python3
"""
Test script for voice profile management
Demonstrates creating profiles, adding samples, and generating speech
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:5001"


def test_profile_workflow():
    """Test complete profile workflow."""
    print("=" * 60)
    print("Voice Profile Management Test")
    print("=" * 60)

    # 1. List existing profiles
    print("\n1. Listing existing profiles...")
    response = requests.get(f"{BASE_URL}/api/profiles")
    if response.ok:
        data = response.json()
        if data['success']:
            profiles = data['profiles']
            print(f"   Found {len(profiles)} profiles:")
            for p in profiles:
                print(f"   - {p['name']}: {p['sample_count']} samples (ID: {p['profile_id']})")
        else:
            print(f"   Error: {data.get('message')}")
    else:
        print(f"   HTTP Error: {response.status_code}")

    # 2. Create a new profile
    print("\n2. Creating new profile...")
    profile_name = "Test Voice Profile"
    response = requests.post(
        f"{BASE_URL}/api/profiles/create",
        json={"name": profile_name}
    )

    if response.ok:
        data = response.json()
        if data['success']:
            profile = data['profile']
            profile_id = profile['profile_id']
            print(f"   ✓ Created profile: {profile_name}")
            print(f"   Profile ID: {profile_id}")
        else:
            print(f"   ✗ Error: {data.get('message')}")
            # If profile already exists, try to get it
            if "already exists" in data.get('message', ''):
                print("   Fetching existing profile...")
                all_profiles = requests.get(f"{BASE_URL}/api/profiles").json()
                for p in all_profiles.get('profiles', []):
                    if p['name'] == profile_name:
                        profile_id = p['profile_id']
                        print(f"   Using existing profile: {profile_id}")
                        break
    else:
        print(f"   HTTP Error: {response.status_code}")
        return False

    # 3. Check for audio files to add
    print("\n3. Checking for audio files to add...")
    uploads_dir = Path("uploads")
    audio_files = list(uploads_dir.glob("*.wav"))

    if not audio_files:
        print("   ✗ No WAV files found in uploads/")
        print("   Please upload some audio files first using the web interface")
        print("   or place WAV files in the uploads/ directory")
        return False

    print(f"   Found {len(audio_files)} audio files")

    # 4. Add samples to profile (up to 3)
    print("\n4. Adding samples to profile...")
    samples_added = 0
    for audio_file in audio_files[:3]:  # Add up to 3 samples
        filename = audio_file.name
        print(f"   Adding: {filename}...")

        response = requests.post(
            f"{BASE_URL}/api/profiles/{profile_id}/add_sample",
            json={"audio_file": filename}
        )

        if response.ok:
            data = response.json()
            if data['success']:
                samples_added += 1
                print(f"   ✓ Added sample {samples_added}")
            else:
                print(f"   ✗ Error: {data.get('message')}")
        else:
            print(f"   HTTP Error: {response.status_code}")

    if samples_added == 0:
        print("   ✗ No samples were added")
        return False

    # 5. Get profile details
    print("\n5. Getting profile details...")
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}")
    if response.ok:
        data = response.json()
        if data['success']:
            profile = data['profile']
            print(f"   Profile: {profile['name']}")
            print(f"   Samples: {profile['sample_count']}")
            for i, sample in enumerate(profile['samples'], 1):
                print(f"     {i}. {sample}")

    # 6. Generate speech with profile
    print("\n6. Generating speech with profile...")
    test_text = "Hello! This is a test of the voice profile system. Multiple samples help improve quality."

    response = requests.post(
        f"{BASE_URL}/api/clone_with_profile",
        json={
            "profile_id": profile_id,
            "text": test_text,
            "language": "en"
        }
    )

    if response.ok:
        data = response.json()
        if data['success']:
            print(f"   ✓ Speech generated successfully!")
            print(f"   Output file: {data['output_file']}")
            print(f"   Download URL: {data['download_url']}")
        else:
            print(f"   ✗ Error: {data.get('message')}")
    else:
        print(f"   HTTP Error: {response.status_code}")

    # 7. List all profiles again
    print("\n7. Final profile list:")
    response = requests.get(f"{BASE_URL}/api/profiles")
    if response.ok:
        data = response.json()
        if data['success']:
            profiles = data['profiles']
            for p in profiles:
                print(f"   - {p['name']}: {p['sample_count']} samples")

    print("\n" + "=" * 60)
    print("✓ Test completed successfully!")
    print("=" * 60)
    print(f"\nProfile ID for future use: {profile_id}")
    print(f"To delete this test profile, run:")
    print(f"  curl -X POST {BASE_URL}/api/profiles/{profile_id}/delete")

    return True


def interactive_mode():
    """Interactive mode for manual testing."""
    print("\nVoice Profile Interactive Mode")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("1. List profiles")
        print("2. Create profile")
        print("3. Add sample to profile")
        print("4. Generate speech")
        print("5. Delete profile")
        print("6. Exit")

        choice = input("\nChoice (1-6): ").strip()

        if choice == '1':
            response = requests.get(f"{BASE_URL}/api/profiles")
            profiles = response.json().get('profiles', [])
            if profiles:
                for p in profiles:
                    print(f"\n{p['name']}")
                    print(f"  ID: {p['profile_id']}")
                    print(f"  Samples: {p['sample_count']}")
            else:
                print("No profiles found")

        elif choice == '2':
            name = input("Profile name: ").strip()
            if name:
                response = requests.post(
                    f"{BASE_URL}/api/profiles/create",
                    json={"name": name}
                )
                data = response.json()
                if data['success']:
                    print(f"✓ Created: {data['profile']['profile_id']}")
                else:
                    print(f"✗ Error: {data.get('message')}")

        elif choice == '3':
            profile_id = input("Profile ID: ").strip()
            audio_file = input("Audio filename (in uploads/): ").strip()
            if profile_id and audio_file:
                response = requests.post(
                    f"{BASE_URL}/api/profiles/{profile_id}/add_sample",
                    json={"audio_file": audio_file}
                )
                data = response.json()
                if data['success']:
                    print("✓ Sample added")
                else:
                    print(f"✗ Error: {data.get('message')}")

        elif choice == '4':
            profile_id = input("Profile ID: ").strip()
            text = input("Text to speak: ").strip()
            if profile_id and text:
                response = requests.post(
                    f"{BASE_URL}/api/clone_with_profile",
                    json={"profile_id": profile_id, "text": text, "language": "en"}
                )
                data = response.json()
                if data['success']:
                    print(f"✓ Generated: {data['output_file']}")
                else:
                    print(f"✗ Error: {data.get('message')}")

        elif choice == '5':
            profile_id = input("Profile ID to delete: ").strip()
            if profile_id:
                confirm = input(f"Delete {profile_id}? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    response = requests.post(
                        f"{BASE_URL}/api/profiles/{profile_id}/delete"
                    )
                    data = response.json()
                    if data['success']:
                        print("✓ Profile deleted")
                    else:
                        print(f"✗ Error: {data.get('message')}")

        elif choice == '6':
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        try:
            test_profile_workflow()
        except requests.exceptions.ConnectionError:
            print("\n✗ Error: Could not connect to server")
            print("  Make sure the voice cloning server is running on port 5001")
            print("  Start it with: python run_production.py")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
