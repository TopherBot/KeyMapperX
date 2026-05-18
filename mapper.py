import json
import sys
import threading
from pathlib import Path

import pygame
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
DEFAULT_PROFILE = {
    "mappings": {
        "BUTTON_A": "action_jump",
        "BUTTON_B": "action_shoot",
        "BUTTON_X": "action_reload",
        "BUTTON_Y": "action_interact"
    },
    "grip_strength": {
        "BUTTON_A": 0.8,
        "BUTTON_B": 1.0,
        "BUTTON_X": 0.5,
        "BUTTON_Y": 0.7
    }
}

# ---------------------------------------------------------------------------
# ACTION CALLBACKS (placeholder implementations)
# ---------------------------------------------------------------------------
def action_jump(strength):
    print(f"🚀 Jump with grip strength {strength:.2f}")

def action_shoot(strength):
    print(f"🔫 Shoot with grip strength {strength:.2f}")

def action_reload(strength):
    print(f"🔄 Reload with grip strength {strength:.2f}")

def action_interact(strength):
    print(f"🤝 Interact with grip strength {strength:.2f}")

ACTION_TABLE = {
    "action_jump": action_jump,
    "action_shoot": action_shoot,
    "action_reload": action_reload,
    "action_interact": action_interact,
}

# ---------------------------------------------------------------------------
# PROFILE HANDLING
# ---------------------------------------------------------------------------
class Profile:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.data = DEFAULT_PROFILE.copy()
        self.load()

    def load(self):
        with self.lock:
            try:
                with self.path.open('r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"[Profile] Loaded from {self.path}")
            except FileNotFoundError:
                print(f"[Profile] File not found, using defaults.")
                self.save()
            except json.JSONDecodeError as e:
                print(f"[Profile] JSON error: {e}. Keeping previous config.")

    def save(self):
        with self.lock:
            with self.path.open('w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
            print(f"[Profile] Saved default to {self.path}")

    def get_mapping(self, button_name):
        with self.lock:
            return self.data["mappings"].get(button_name)

    def get_strength(self, button_name):
        with self.lock:
            return self.data["grip_strength"].get(button_name, 1.0)

# ---------------------------------------------------------------------------
# FILE WATCHER FOR LIVE RELOAD
# ---------------------------------------------------------------------------
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, profile: Profile):
        super().__init__()
        self.profile = profile

    def on_modified(self, event):
        if Path(event.src_path) == self.profile.path:
            print("[Watcher] Detected profile change, reloading…")
            self.profile.load()

def start_watcher(profile: Profile):
    event_handler = ReloadHandler(profile)
    observer = Observer()
    observer.schedule(event_handler, str(profile.path.parent), recursive=False)
    observer.start()
    return observer

# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
def main(profile_path: str):
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No joystick detected. Connect a gamepad and retry.")
        sys.exit(1)
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Detected joystick: {joystick.get_name()}")

    profile = Profile(Path(profile_path))
    observer = start_watcher(profile)

    button_name_map = {
        0: "BUTTON_A",
        1: "BUTTON_B",
        2: "BUTTON_X",
        3: "BUTTON_Y",
        # Extend as needed
    }

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    btn_idx = event.button
                    name = button_name_map.get(btn_idx, f"BUTTON_{btn_idx}")
                    action_key = profile.get_mapping(name)
                    strength = profile.get_strength(name)
                    if action_key and action_key in ACTION_TABLE:
                        ACTION_TABLE[action_key](strength)
                    else:
                        print(f"[Info] No action bound for {name}")
            pygame.time.wait(10)
    except KeyboardInterrupt:
        print("\nExiting…")
    finally:
        observer.stop()
        observer.join()
        pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mapper.py <profile.json>")
        sys.exit(1)
    main(sys.argv[1])
