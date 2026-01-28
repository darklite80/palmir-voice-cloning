#!/usr/bin/env python3
"""
Voice Profile Management System
Handles creation, storage, and management of voice profiles with multiple training samples
"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class VoiceProfile:
    """Represents a voice profile with multiple audio samples."""

    def __init__(self, name: str, profile_id: str, samples: List[str], created_at: str):
        self.name = name
        self.profile_id = profile_id
        self.samples = samples
        self.created_at = created_at

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'profile_id': self.profile_id,
            'samples': self.samples,
            'created_at': self.created_at,
            'sample_count': len(self.samples)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'VoiceProfile':
        return cls(
            name=data['name'],
            profile_id=data['profile_id'],
            samples=data.get('samples', []),
            created_at=data.get('created_at', datetime.now().isoformat())
        )


class VoiceProfileManager:
    """Manages voice profiles and their audio samples."""

    def __init__(self, profiles_dir: str = "voice_profiles", uploads_dir: str = "uploads"):
        self.profiles_dir = Path(profiles_dir)
        self.uploads_dir = Path(uploads_dir)
        self.profiles_file = self.profiles_dir / "profiles.json"

        # Create directories
        self.profiles_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)

        # Load or initialize profiles
        self._profiles: Dict[str, VoiceProfile] = {}
        self._load_profiles()

    def _load_profiles(self):
        """Load profiles from JSON file."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    self._profiles = {
                        pid: VoiceProfile.from_dict(pdata)
                        for pid, pdata in data.items()
                    }
            except Exception as e:
                print(f"Error loading profiles: {e}")
                self._profiles = {}

    def _save_profiles(self):
        """Save profiles to JSON file."""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(
                    {pid: p.to_dict() for pid, p in self._profiles.items()},
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"Error saving profiles: {e}")

    def create_profile(self, name: str) -> VoiceProfile:
        """
        Create a new voice profile.

        Args:
            name: Name for the voice profile

        Returns:
            VoiceProfile object

        Raises:
            ValueError: If profile name already exists
        """
        # Check if name already exists
        for profile in self._profiles.values():
            if profile.name == name:
                raise ValueError(f"Profile with name '{name}' already exists")

        # Generate unique ID
        profile_id = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create profile directory
        profile_dir = self.profiles_dir / profile_id
        profile_dir.mkdir(exist_ok=True)

        # Create profile
        profile = VoiceProfile(
            name=name,
            profile_id=profile_id,
            samples=[],
            created_at=datetime.now().isoformat()
        )

        self._profiles[profile_id] = profile
        self._save_profiles()

        return profile

    def add_sample(self, profile_id: str, audio_file: str) -> bool:
        """
        Add an audio sample to a voice profile.

        Args:
            profile_id: ID of the profile
            audio_file: Path to audio file in uploads directory

        Returns:
            True if successful

        Raises:
            ValueError: If profile doesn't exist or file not found
        """
        if profile_id not in self._profiles:
            raise ValueError(f"Profile '{profile_id}' not found")

        source_path = self.uploads_dir / audio_file
        if not source_path.exists():
            raise ValueError(f"Audio file '{audio_file}' not found")

        # Copy to profile directory
        profile_dir = self.profiles_dir / profile_id
        dest_path = profile_dir / audio_file

        shutil.copy2(source_path, dest_path)

        # Update profile
        profile = self._profiles[profile_id]
        if audio_file not in profile.samples:
            profile.samples.append(audio_file)
            self._save_profiles()

        return True

    def remove_sample(self, profile_id: str, audio_file: str) -> bool:
        """
        Remove an audio sample from a voice profile.

        Args:
            profile_id: ID of the profile
            audio_file: Filename of the sample to remove

        Returns:
            True if successful
        """
        if profile_id not in self._profiles:
            return False

        profile = self._profiles[profile_id]

        if audio_file in profile.samples:
            profile.samples.remove(audio_file)

            # Delete file
            file_path = self.profiles_dir / profile_id / audio_file
            if file_path.exists():
                file_path.unlink()

            self._save_profiles()
            return True

        return False

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a voice profile and all its samples.

        Args:
            profile_id: ID of the profile to delete

        Returns:
            True if successful
        """
        if profile_id not in self._profiles:
            return False

        # Delete profile directory
        profile_dir = self.profiles_dir / profile_id
        if profile_dir.exists():
            shutil.rmtree(profile_dir)

        # Remove from profiles
        del self._profiles[profile_id]
        self._save_profiles()

        return True

    def get_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Get a voice profile by ID."""
        return self._profiles.get(profile_id)

    def get_profile_by_name(self, name: str) -> Optional[VoiceProfile]:
        """Get a voice profile by name."""
        for profile in self._profiles.values():
            if profile.name == name:
                return profile
        return None

    def list_profiles(self) -> List[Dict]:
        """List all voice profiles."""
        return [p.to_dict() for p in self._profiles.values()]

    def get_primary_sample(self, profile_id: str) -> Optional[str]:
        """
        Get the primary (first) audio sample for a profile.
        This is used for voice cloning with single sample.

        Args:
            profile_id: ID of the profile

        Returns:
            Path to the primary sample file, or None if no samples
        """
        if profile_id not in self._profiles:
            return None

        profile = self._profiles[profile_id]
        if not profile.samples:
            return None

        # Return path to first sample
        sample_path = self.profiles_dir / profile_id / profile.samples[0]
        return str(sample_path) if sample_path.exists() else None

    def get_all_samples(self, profile_id: str) -> List[str]:
        """
        Get all audio sample paths for a profile.

        Args:
            profile_id: ID of the profile

        Returns:
            List of paths to all sample files
        """
        if profile_id not in self._profiles:
            return []

        profile = self._profiles[profile_id]
        profile_dir = self.profiles_dir / profile_id

        return [
            str(profile_dir / sample)
            for sample in profile.samples
            if (profile_dir / sample).exists()
        ]

    def rename_profile(self, profile_id: str, new_name: str) -> bool:
        """
        Rename a voice profile.

        Args:
            profile_id: ID of the profile
            new_name: New name for the profile

        Returns:
            True if successful

        Raises:
            ValueError: If new name already exists
        """
        if profile_id not in self._profiles:
            return False

        # Check if new name already exists (for different profile)
        for pid, profile in self._profiles.items():
            if pid != profile_id and profile.name == new_name:
                raise ValueError(f"Profile with name '{new_name}' already exists")

        self._profiles[profile_id].name = new_name
        self._save_profiles()
        return True


# Testing
if __name__ == "__main__":
    manager = VoiceProfileManager()

    # Create test profile
    profile = manager.create_profile("Test Voice")
    print(f"Created profile: {profile.to_dict()}")

    # List profiles
    print("\nAll profiles:")
    for p in manager.list_profiles():
        print(f"  - {p['name']}: {p['sample_count']} samples")
