"""
Audio Manager for Arcade Game
Handles all sound effects and music for the game.
"""

import arcade
import random
import os
from pathlib import Path


class AudioManager:
    """Manages all audio for the game including sound effects and music."""
    
    def __init__(self):
        """Initialize the audio manager and load all sounds."""
        # Volume settings (0.0 to 1.0)
        self.master_volume = 0.7
        self.effects_volume = 0.8
        self.music_volume = 0.5
        self.muted = False
        
        # Sound storage
        self.sounds = {}
        self.music = None
        self.current_music = None
        
        # Track what's currently playing
        self.background_music_playing = False
        
        # Load all sounds (with error handling)
        try:
            self._load_sounds()
        except Exception as e:
            print(f"Warning: Audio initialization failed: {e}")
            print("Game will continue without audio.")
    
    def _load_sounds(self):
        """Load all sound files from the assets/sounds directory."""
        sounds_dir = Path("assets/sounds")
        
        # Define sound mappings - map files to game events
        sound_mappings = {
            # Game event sounds
            "fruit_collect": [
                "Voicy_UM, WHAT THE SIGMA🤔🤨 .mp3",
                "Voicy_Bruh.mp3"
            ],
            "special_fruit": [
                "Voicy_GYATTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT.mp3"
            ],
            "game_over": [
                "Voicy_Titanic Bad Flute Cover.mp3",
                "Voicy_meow meow brainrot sound.mp3",
                "Voicy_gedegedegidagedao .mp3"
            ],
            "pause": [
                "Voicy_Why are you gae_.mp3"
            ],
            "menu_click": [
                "Voicy_GYATTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT.mp3"
            ],
            "background_music": [
                "Voicy_Mewing.mp3"
            ]
        }
        
        # Load sounds based on mappings
        for event_type, filenames in sound_mappings.items():
            self.sounds[event_type] = []
            for filename in filenames:
                file_path = sounds_dir / filename
                if file_path.exists():
                    try:
                        sound = arcade.load_sound(str(file_path))
                        self.sounds[event_type].append(sound)
                        print(f"Loaded sound: {filename} for {event_type}")
                    except Exception as e:
                        print(f"Failed to load sound {filename}: {e}")
                else:
                    print(f"Sound file not found: {filename}")
        
        # Load background music separately
        if self.sounds.get("background_music"):
            self.music = self.sounds["background_music"][0]
    
    def _get_effective_volume(self, sound_type="effect"):
        """Calculate the effective volume considering master volume and mute state."""
        if self.muted:
            return 0.0
        
        base_volume = self.effects_volume if sound_type == "effect" else self.music_volume
        return self.master_volume * base_volume
    
    def play_fruit_collect(self, special=False):
        """Play a fruit collection sound."""
        try:
            sound_type = "special_fruit" if special else "fruit_collect"
            sounds = self.sounds.get(sound_type, [])
            
            if sounds:
                # Randomly select a sound for variety
                sound = random.choice(sounds)
                volume = self._get_effective_volume("effect")
                arcade.play_sound(sound, volume)
        except Exception as e:
            print(f"Error playing fruit collect sound: {e}")
    
    def play_game_over(self):
        """Play a game over sound."""
        try:
            sounds = self.sounds.get("game_over", [])
            if sounds:
                sound = random.choice(sounds)
                volume = self._get_effective_volume("effect")
                arcade.play_sound(sound, volume)
        except Exception as e:
            print(f"Error playing game over sound: {e}")
    
    def play_pause(self):
        """Play a pause sound."""
        try:
            sounds = self.sounds.get("pause", [])
            if sounds:
                sound = random.choice(sounds)
                volume = self._get_effective_volume("effect")
                arcade.play_sound(sound, volume)
        except Exception as e:
            print(f"Error playing pause sound: {e}")
    
    def play_menu_click(self):
        """Play a menu click sound."""
        try:
            sounds = self.sounds.get("menu_click", [])
            if sounds:
                sound = random.choice(sounds)
                volume = self._get_effective_volume("effect")
                arcade.play_sound(sound, volume)
        except Exception as e:
            print(f"Error playing menu click sound: {e}")
    
    def start_background_music(self, loop=True):
        """Start playing background music."""
        try:
            if self.music and not self.background_music_playing:
                volume = self._get_effective_volume("music")
                if volume > 0:  # Only play if not muted
                    # Note: arcade.play_sound doesn't support looping parameter
                    # For looping music, we'd need to use a different approach
                    self.current_music = arcade.play_sound(self.music, volume)
                    self.background_music_playing = True
        except Exception as e:
            print(f"Error starting background music: {e}")
    
    def stop_background_music(self):
        """Stop the background music."""
        if self.current_music:
            arcade.stop_sound(self.current_music)
            self.current_music = None
            self.background_music_playing = False
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds."""
        self.stop_background_music()
        # Note: arcade doesn't provide a direct way to stop all sound effects
        # Individual sound effects are typically short and will finish naturally
    
    def set_master_volume(self, volume):
        """Set the master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def set_effects_volume(self, volume):
        """Set the effects volume (0.0 to 1.0)."""
        self.effects_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def _update_music_volume(self):
        """Update the volume of currently playing music."""
        if self.current_music and self.background_music_playing:
            new_volume = self._get_effective_volume("music")
            # Note: arcade doesn't provide direct volume control for playing sounds
            # This is a limitation of the current arcade library
            # For full volume control, we'd need to restart the music
            pass
    
    def toggle_mute(self):
        """Toggle mute state for all audio."""
        self.muted = not self.muted
        if self.muted:
            self.stop_background_music()
        else:
            # Restart background music if it was playing
            if not self.background_music_playing:
                self.start_background_music()
    
    def is_muted(self):
        """Check if audio is currently muted."""
        return self.muted
    
    def get_volume_info(self):
        """Get current volume settings as a dictionary."""
        return {
            "master": self.master_volume,
            "effects": self.effects_volume,
            "music": self.music_volume,
            "muted": self.muted
        }
    
    def cleanup(self):
        """Clean up audio resources."""
        self.stop_all_sounds()


# Audio configuration constants
class AudioConfig:
    """Configuration constants for audio settings."""
    
    # Default volumes
    DEFAULT_MASTER_VOLUME = 0.7
    DEFAULT_EFFECTS_VOLUME = 0.8
    DEFAULT_MUSIC_VOLUME = 0.5
    
    # Special fruit collection chance (1 in X chance for special sound)
    SPECIAL_FRUIT_CHANCE = 10
    
    # Volume adjustment increments
    VOLUME_STEP = 0.1
